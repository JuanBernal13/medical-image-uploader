import asyncio
import boto3
from app.core.config import settings
from app.ports.outputs import ImageStoragePort

class S3ImageStorage(ImageStoragePort):
    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.s3_client = self.session.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL
        )
        self.bucket = settings.S3_BUCKET_NAME

    def _upload(self, file_content: bytes, filename: str, content_type: str) -> str:
        s3_key = f"images/{filename}"
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=s3_key,
            Body=file_content,
            ContentType=content_type
        )
        return s3_key

    async def upload_file(self, file_content: bytes, filename: str, content_type: str) -> str:
        return await asyncio.to_thread(self._upload, file_content, filename, content_type)

    def _download(self, s3_key: str) -> bytes:
        response = self.s3_client.get_object(Bucket=self.bucket, Key=s3_key)
        return response['Body'].read()

    async def download_file(self, s3_key: str) -> bytes:
        return await asyncio.to_thread(self._download, s3_key)

    def _delete(self, s3_key: str) -> None:
        self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)

    async def delete_file(self, s3_key: str) -> None:
        await asyncio.to_thread(self._delete, s3_key)

    def _generate_url(self, s3_key: str, expiration: int) -> str:
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': s3_key},
            ExpiresIn=expiration
        )

    async def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        return await asyncio.to_thread(self._generate_url, s3_key, expiration)
