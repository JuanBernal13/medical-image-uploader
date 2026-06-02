import asyncio
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
from app.domain.models import ImageMetadata
from app.ports.outputs import MetadataRepositoryPort

class DynamoDBMetadataRepository(MetadataRepositoryPort):
    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.dynamodb = self.session.resource(
            'dynamodb',
            endpoint_url=settings.AWS_DYNAMODB_ENDPOINT_URL
        )
        self.table = self.dynamodb.Table(settings.DYNAMODB_TABLE_NAME)

    def _save(self, metadata: ImageMetadata) -> ImageMetadata:
        item = {
            "image_id": metadata.image_id,
            "patient_id": metadata.patient_id,
            "modality": metadata.modality,
            "body_part": metadata.body_part,
            "patient_age": int(metadata.patient_age),
            "patient_gender": metadata.patient_gender,
            "width": int(metadata.width),
            "height": int(metadata.height)
        }
        self.table.put_item(Item=item)
        return metadata

    async def save_metadata(self, metadata: ImageMetadata) -> ImageMetadata:
        return await asyncio.to_thread(self._save, metadata)

    def _get(self, image_id: str) -> Optional[ImageMetadata]:
        try:
            response = self.table.get_item(Key={"image_id": image_id})
            item = response.get("Item")
            if not item:
                return None
            return ImageMetadata(
                image_id=item["image_id"],
                patient_id=item["patient_id"],
                modality=item["modality"],
                body_part=item["body_part"],
                patient_age=int(item["patient_age"]),
                patient_gender=item["patient_gender"],
                width=int(item["width"]),
                height=int(item["height"])
            )
        except ClientError:
            return None

    async def get_metadata(self, image_id: str) -> Optional[ImageMetadata]:
        return await asyncio.to_thread(self._get, image_id)

    def _update(self, metadata: ImageMetadata) -> ImageMetadata:
        self.table.update_item(
            Key={"image_id": metadata.image_id},
            UpdateExpression="SET patient_id = :p, modality = :m, body_part = :b, patient_age = :a, patient_gender = :g, width = :w, height = :h",
            ExpressionAttributeValues={
                ":p": metadata.patient_id,
                ":m": metadata.modality,
                ":b": metadata.body_part,
                ":a": int(metadata.patient_age),
                ":g": metadata.patient_gender,
                ":w": int(metadata.width),
                ":h": int(metadata.height)
            }
        )
        return metadata

    async def update_metadata(self, metadata: ImageMetadata) -> ImageMetadata:
        return await asyncio.to_thread(self._update, metadata)

    def _delete(self, image_id: str) -> None:
        self.table.delete_item(Key={"image_id": image_id})

    async def delete_metadata(self, image_id: str) -> None:
        await asyncio.to_thread(self._delete, image_id)
