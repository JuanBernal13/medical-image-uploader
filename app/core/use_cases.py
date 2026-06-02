import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.domain.models import MedicalImage, ImageMetadata, ImageReview, Comment
from app.domain.exceptions import ImageNotFoundError, ReviewNotFoundError
from app.ports.inputs import MedicalImageUseCase
from app.ports.outputs import ImageStoragePort, MetadataRepositoryPort, ImageRepositoryPort, ReviewRepositoryPort
from app.utils.image_utils import get_image_dimensions

class MedicalImageService(MedicalImageUseCase):
    def __init__(
        self,
        storage: ImageStoragePort,
        metadata_repo: MetadataRepositoryPort,
        image_repo: ImageRepositoryPort,
        review_repo: ReviewRepositoryPort
    ):
        self.storage = storage
        self.metadata_repo = metadata_repo
        self.image_repo = image_repo
        self.review_repo = review_repo

    async def upload_image(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        patient_id: str,
        modality: str,
        body_part: str,
        patient_age: int,
        patient_gender: str
    ) -> Dict[str, Any]:
        image_id = str(uuid.uuid4())
        s3_key = await self.storage.upload_file(file_content, f"{image_id}_{filename}", content_type)
        
        image = MedicalImage(
            id=image_id,
            filename=filename,
            s3_key=s3_key,
            content_type=content_type,
            size=len(file_content),
            uploaded_at=datetime.utcnow()
        )
        await self.image_repo.save_image(image)
        
        width, height = get_image_dimensions(file_content)
        
        metadata = ImageMetadata(
            image_id=image_id,
            patient_id=patient_id,
            modality=modality,
            body_part=body_part,
            patient_age=patient_age,
            patient_gender=patient_gender,
            width=width,
            height=height
        )
        await self.metadata_repo.save_metadata(metadata)
        
        return {
            "image_id": image_id,
            "filename": filename,
            "s3_key": s3_key,
            "uploaded_at": image.uploaded_at,
            "metadata": metadata
        }

    async def get_image_details(self, image_id: str) -> Dict[str, Any]:
        image = await self.image_repo.get_image(image_id)
        if not image:
            raise ImageNotFoundError(image_id)
        
        metadata = await self.metadata_repo.get_metadata(image_id)
        reviews = await self.review_repo.get_reviews_by_image(image_id)
        
        return {
            "id": image.id,
            "filename": image.filename,
            "s3_key": image.s3_key,
            "content_type": image.content_type,
            "size": image.size,
            "uploaded_at": image.uploaded_at,
            "metadata": metadata,
            "reviews": reviews
        }

    async def get_image_download_url(self, image_id: str) -> str:
        image = await self.image_repo.get_image(image_id)
        if not image:
            raise ImageNotFoundError(image_id)
        return await self.storage.generate_presigned_url(image.s3_key)

    async def delete_image(self, image_id: str) -> None:
        image = await self.image_repo.get_image(image_id)
        if not image:
            raise ImageNotFoundError(image_id)
        
        await self.storage.delete_file(image.s3_key)
        await self.metadata_repo.delete_metadata(image_id)
        await self.review_repo.delete_reviews_by_image(image_id)
        await self.image_repo.delete_image(image_id)

    async def list_images(self) -> List[Dict[str, Any]]:
        images = await self.image_repo.list_images()
        result = []
        for img in images:
            meta = await self.metadata_repo.get_metadata(img.id)
            result.append({
                "id": img.id,
                "filename": img.filename,
                "s3_key": img.s3_key,
                "content_type": img.content_type,
                "size": img.size,
                "uploaded_at": img.uploaded_at,
                "metadata": meta
            })
        return result

    async def add_review(
        self,
        image_id: str,
        reviewer_name: str,
        status: str,
        findings: str,
        severity: str
    ) -> ImageReview:
        image = await self.image_repo.get_image(image_id)
        if not image:
            raise ImageNotFoundError(image_id)
        
        review_id = str(uuid.uuid4())
        review = ImageReview(
            id=review_id,
            image_id=image_id,
            reviewer_name=reviewer_name,
            status=status,
            findings=findings,
            severity=severity,
            comments=[],
            reviewed_at=datetime.utcnow()
        )
        return await self.review_repo.save_review(review)

    async def get_image_reviews(self, image_id: str) -> List[ImageReview]:
        image = await self.image_repo.get_image(image_id)
        if not image:
            raise ImageNotFoundError(image_id)
        return await self.review_repo.get_reviews_by_image(image_id)

    async def add_review_comment(self, review_id: str, author: str, text: str) -> ImageReview:
        review = await self.review_repo.get_review(review_id)
        if not review:
            raise ReviewNotFoundError(review_id)
        
        comment = Comment(author=author, text=text, created_at=datetime.utcnow())
        review.comments.append(comment)
        return await self.review_repo.save_review(review)

    async def update_image_metadata(
        self,
        image_id: str,
        patient_id: str,
        modality: str,
        body_part: str,
        patient_age: int,
        patient_gender: str
    ) -> ImageMetadata:
        image = await self.image_repo.get_image(image_id)
        if not image:
            raise ImageNotFoundError(image_id)
        
        current_meta = await self.metadata_repo.get_metadata(image_id)
        width = current_meta.width if current_meta else 0
        height = current_meta.height if current_meta else 0
        
        new_meta = ImageMetadata(
            image_id=image_id,
            patient_id=patient_id,
            modality=modality,
            body_part=body_part,
            patient_age=patient_age,
            patient_gender=patient_gender,
            width=width,
            height=height
        )
        return await self.metadata_repo.save_metadata(new_meta)

    async def get_patient_images(self, patient_id: str) -> List[Dict[str, Any]]:
        images = await self.image_repo.list_images()
        result = []
        for img in images:
            meta = await self.metadata_repo.get_metadata(img.id)
            if meta and meta.patient_id == patient_id:
                result.append({
                    "id": img.id,
                    "filename": img.filename,
                    "s3_key": img.s3_key,
                    "content_type": img.content_type,
                    "size": img.size,
                    "uploaded_at": img.uploaded_at,
                    "metadata": meta
                })
        return result

    async def get_system_stats(self) -> Dict[str, Any]:
        return await self.review_repo.get_global_stats()
