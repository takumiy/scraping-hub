import os

from botocore.exceptions import ClientError
from dotenv import load_dotenv

from scraping_hub.yahoo_access_ranking.dynamodb_client import get_dynamodb_client

# .envファイルから環境変数を読み込む
load_dotenv()

# DynamoDBクライアントを取得
dynamodb = get_dynamodb_client()

table_name = os.getenv('YAHOO_ACCESS_RANKING_DYNAMODB_TABLE')

try:
    # 既存のテーブルのリストを取得
    existing_tables = dynamodb.list_tables()

    # テーブルが既に存在するか確認
    if table_name not in existing_tables['TableNames']:
        # 新しいテーブルを作成
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'news', 'KeyType': 'HASH'},  # パーティションキー
                {'AttributeName': 'execution_timestamp', 'KeyType': 'RANGE'}  # ソートキー
            ],
            AttributeDefinitions=[
                {'AttributeName': 'news', 'AttributeType': 'S'},  # 文字列型
                {'AttributeName': 'execution_timestamp', 'AttributeType': 'N'}  # 数値型
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print(f'Table {table_name} created successfully.')
    else:
        print(f'Table {table_name} already exists.')
except ClientError as e:
    print(f'An error occurred: {e}')
