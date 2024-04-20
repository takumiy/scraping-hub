import os
import pytz

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from scraping_hub.yahoo_access_ranking.dynamodb_client import get_dynamodb_client
from scraping_hub.yahoo_access_ranking.news_feed import news_feed
from scraping_hub.yahoo_access_ranking.s3_client import get_s3_client

# .envファイルから環境変数を読み込む
load_dotenv()


def _create_ranking_html(feed, result):
    # スクリプトのあるディレクトリの絶対パスを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # base_ranking.htmlへの絶対パスを構築
    base_ranking_file_path = os.path.join(script_dir, 'base_ranking.html')

    with open(base_ranking_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    ranking_header_div = soup.new_tag('div', attrs={'class': 'ranking-header'})
    ranking_header_div.string = f'Yahooアクセスランキング: {feed['カテゴリ']}'

    soup.body.append(ranking_header_div)

    update_time_div = soup.new_tag('div', attrs={'class': 'update-time'})
    # 現在の日付を取得し、分秒を '00:00' に設定
    execution_time = datetime.now(pytz.timezone('Asia/Tokyo')).replace(minute=0, second=0, microsecond=0)
    update_time_div.string = f'({execution_time.strftime('%Y年%m月%d日 %H:%M')} 更新)'

    soup.body.append(update_time_div)

    # HTMLにランキングリストを追加するためのdivを作成
    ranking_list_div = soup.new_tag('div', **{'class': 'ranking-list'})
    soup.body.append(ranking_list_div)

    current_rank = ...
    current_point = float('inf')
    for position, record in enumerate(result, 1):
        title, url, image_url, point = record.values()

        if point < current_point:
            current_rank = position
            current_point = point

        # ランキングアイテムのdivを作成
        item_div = soup.new_tag('div', **{'class': 'ranking-item'})
        ranking_list_div.append(item_div)

        # 画像を追加
        img_tag = soup.new_tag('img', src=image_url, **{'class': 'ranking-image', 'alt': f'ランキング画像: {title}'})
        item_div.append(img_tag)

        # タイトル（リンク付き）を追加
        title_tag = soup.new_tag('div', **{'class': 'ranking-title'})
        link_tag = soup.new_tag('a', href=url)
        link_tag.string = title
        title_tag.append(link_tag)
        item_div.append(title_tag)

        # ランキングの詳細（ポイント）を追加
        details_tag = soup.new_tag('div', **{'class': 'ranking-details'})
        details_tag.string = f'ランク: {current_rank}, ポイント: {current_point}'
        item_div.append(details_tag)

    filename = f'ranking_{feed['category']}.html'

    # ranking_{category}.htmlへの絶対パスを構築
    if os.getenv('APP_ENV') == 'local':
        ranking_file_path = os.path.join(script_dir, 'html_reports', filename)
    else:
        ranking_file_path = os.path.join('/tmp', filename)

    with open(ranking_file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

    # S3クライアントを取得
    s3 = get_s3_client()

    s3_file_path = '/'.join([execution_time.strftime('%Y/%m/%d/%H'), filename])

    # S3にアップロード
    s3.upload_file(
        Filename=ranking_file_path,
        Bucket=os.getenv('YAHOO_ACCESS_RANKING_S3_BUCKET'),
        Key=s3_file_path,
        ExtraArgs={'ContentType': 'text/html', 'ACL': 'public-read'}
    )


def _send_to_slack(feed, result):
    client = WebClient(token=os.getenv('YAHOO_ACCESS_RANKING_OAUTH_TOKEN'))

    try:
        blocks = [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*{feed['カテゴリ']}*'
                }
            },
            {
                'type': 'divider'
            }
        ]

        current_rank = ...
        current_point = float('inf')
        for position, record in enumerate(result, 1):
            title, url, image_url, point = record.values()

            if point < current_point:
                current_rank = position
                current_point = point

            # ランキングアイテムのセクションを追加
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*{current_rank}位: <{url}|{title}>*\nポイント: {current_point}'
                },
                'accessory': {
                    'type': 'image',
                    'image_url': image_url,
                    'alt_text': 'thumbnail image'
                }
            })

            # 区切り線を追加
            blocks.append({
                'type': 'divider'
            })

            if position == 3:
                break

        # 現在の日付を取得し、分秒を '00:00' に設定
        execution_time = datetime.now(pytz.timezone('Asia/Tokyo')).replace(minute=0, second=0, microsecond=0)
        s3_url = '/'.join([
            os.getenv('YAHOO_ACCESS_RANKING_S3_URL'),
            execution_time.strftime('%Y/%m/%d/%H'),
            f'ranking_{feed['category']}.html'
        ])

        blocks.append({
            'type': 'actions',
            'elements': [
                {
                    'type': 'button',
                    'text': {
                        'type': 'plain_text',
                        'text': 'もっと見る'
                    },
                    'url': s3_url
                }
            ]
        })

        client.chat_postMessage(
            channel=os.getenv('YAHOO_ACCESS_RANKING_CHANNEL_ID'),
            text=f'Yahooアクセスランキング: {feed['カテゴリ']}',
            blocks=blocks,
            unfurl_links=False
        )
    except SlackApiError as e:
        print(f'Got an error: {e.response['error']}')


def lambda_handler(event=None, context=None):
    for feed in news_feed:
        # 現在の日付を取得し、分秒を '00:00' に設定
        end_time = datetime.now(pytz.timezone('Asia/Tokyo')).replace(minute=0, second=0, microsecond=0)

        # UNIXエポックタイムに変換（秒単位）
        end_timestamp = int(end_time.timestamp())

        # 24時間前の時刻を計算
        start_time = end_time - timedelta(days=1)

        # UNIXエポックタイムに変換（秒単位）
        start_timestamp = int(start_time.timestamp())

        # DynamoDBクライアントを取得
        dynamodb = get_dynamodb_client()

        # 24時間のデータをクエリ
        response = dynamodb.query(
            TableName=os.getenv('YAHOO_ACCESS_RANKING_DYNAMODB_TABLE'),
            KeyConditionExpression='news = :news_val AND execution_timestamp BETWEEN :start_ts AND :end_ts',
            ExpressionAttributeValues={
                ':news_val': {'S': feed['category']},
                ':start_ts': {'N': str(start_timestamp)},
                ':end_ts': {'N': str(end_timestamp)}
            }
        )

        # 順位をポイントに変換して集計
        result = {}
        for item in response['Items']:
            news_data = item['news_data']['L']
            for position, news_dict in enumerate(news_data, 1):
                news = news_dict['M']
                title = news['title']['S']
                url = news['url']['S']
                image_url = news['image_url']['S']
                result.setdefault(url, {
                    'title': title,
                    'url': url,
                    'image_url': image_url,
                    'point': 0
                })
                result[url]['point'] += len(news_data) + 1 - position

        result_sorted = sorted(result.values(), key=lambda record: -record['point'])

        _create_ranking_html(feed, result_sorted)

        # Slackに集計結果を通知
        _send_to_slack(feed, result_sorted)


if __name__ == '__main__':
    lambda_handler()
