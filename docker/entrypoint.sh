#!/bin/sh
# entrypoint.sh

# YahooアクセスランキングDynamoDBテーブル削除
python -m scraping_hub.yahoo_access_ranking.delete_dynamodb_table

# YahooアクセスランキングDynamoDBテーブル作成
python -m scraping_hub.yahoo_access_ranking.create_dynamodb_table

# YahooアクセスランキングS3バケット作成
python -m scraping_hub.yahoo_access_ranking.create_s3_bucket

exec "$@"
