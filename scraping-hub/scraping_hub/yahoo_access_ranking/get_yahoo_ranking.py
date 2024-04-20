import os
import pytz
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv

from scraping_hub.yahoo_access_ranking.dynamodb_client import get_dynamodb_client
from scraping_hub.yahoo_access_ranking.news_feed import news_feed

# .envファイルから環境変数を読み込む
load_dotenv()


def lambda_handler(event=None, context=None):
    for feed in news_feed:
        # ページのHTMLを取得
        response = requests.get(feed['url'])

        # BeautifulSoupを使ってHTMLを解析
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')

        # newsFeed_item_linkクラスが付いたaタグをすべて検索
        news_items = soup.find_all('a', class_='newsFeed_item_link')

        # 結果を格納するリスト
        news_data = []

        # 各ニュース項目に対して処理
        for item in news_items:
            news = {
                'M': {'url': {'S': item['href']}}
            }

            # newsFeed_item_titleクラスが付いたdivタグを検索
            title_div = item.find('div', class_='newsFeed_item_title')
            if title_div:
                news['M']['title'] = {'S': title_div.get_text()}

            # item内のpicture要素を検索
            picture = item.find('picture')
            if picture:
                source = picture.find('source', {'type': 'image/jpeg'})
                if source and source.has_attr('srcset'):
                    news['M']['image_url'] = {'S': source['srcset']}

            # リストに追加
            news_data.append(news)

        # DynamoDBクライアントを取得
        dynamodb = get_dynamodb_client()

        # 現在の日付を取得し、分秒を '00:00' に設定
        execution_time = datetime.now(pytz.timezone('Asia/Tokyo')).replace(minute=0, second=0, microsecond=0)

        # UNIXエポックタイムに変換（秒単位）
        execution_timestamp = str(int(execution_time.timestamp()))

        # データをDynamoDBに保存
        dynamodb.put_item(
            TableName=os.getenv('YAHOO_ACCESS_RANKING_DYNAMODB_TABLE'),
            Item={
                'news': {'S': feed['category']},
                'execution_timestamp': {'N': execution_timestamp},
                'news_data': {'L': news_data}
            }
        )


if __name__ == '__main__':
    lambda_handler()
