import os

from botocore.exceptions import ClientError
from dotenv import load_dotenv

from scraping_hub.yahoo_access_ranking.dynamodb_client import get_dynamodb_client

# .envファイルから環境変数を読み込む
load_dotenv()

# DynamoDBクライアントを取得
dynamodb = get_dynamodb_client()

# 削除するテーブルの名前
table_name = os.getenv('YAHOO_ACCESS_RANKING_DYNAMODB_TABLE')

try:
    # 既存のテーブルのリストを取得
    existing_tables = dynamodb.list_tables()

    # テーブルが既に存在するか確認
    if table_name in existing_tables['TableNames']:
        # テーブルの削除
        dynamodb.delete_table(TableName=table_name)
        print(f'Table {table_name} deleted successfully.')
    else:
        print(f'Table {table_name} does not exist.')
except ClientError as e:
    print(f'An error occurred: {e}')
