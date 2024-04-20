import boto3
import dotenv
import os

dotenv.load_dotenv()


def get_s3_client():
    if os.getenv('APP_ENV') == 'local':
        return boto3.client(
            's3',
            endpoint_url=os.getenv('MINIO_ENDPOINT'),
            aws_access_key_id=os.getenv('MINIO_ROOT_USER'),
            aws_secret_access_key=os.getenv('MINIO_ROOT_PASSWORD'),
        )

    return boto3.client('s3')
