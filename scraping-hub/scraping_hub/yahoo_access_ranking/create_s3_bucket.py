import dotenv
import os

from botocore.exceptions import ClientError

from scraping_hub.yahoo_access_ranking.s3_client import get_s3_client

dotenv.load_dotenv()

# S3クライアントを取得
s3 = get_s3_client()

# 作成するバケットの名前
bucket_name = os.getenv('YAHOO_ACCESS_RANKING_S3_BUCKET')

try:
    # 既存のバケットのリストを取得
    existing_buckets = s3.list_buckets()

    # バケットが既に存在するか確認
    bucket_exists = any(bucket['Name'] == bucket_name for bucket in existing_buckets['Buckets'])

    if not bucket_exists:
        # 新しいバケットを作成
        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} created successfully.")
    else:
        print(f"Bucket {bucket_name} already exists.")
except ClientError as e:
    print(f'An error occurred: {e}')
