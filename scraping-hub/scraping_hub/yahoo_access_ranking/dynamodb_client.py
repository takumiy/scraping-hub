import boto3
import os

from dotenv import load_dotenv

load_dotenv()


def get_dynamodb_client():
    if os.getenv('APP_ENV') == 'local':
        return boto3.client(
            'dynamodb',
            endpoint_url=os.getenv('DYNAMODB_ENDPOINT'),
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )

    return boto3.client('dynamodb')
