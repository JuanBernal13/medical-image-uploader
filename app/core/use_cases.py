import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.domain.models import MedicalImage, ImageMetadata, ImageReview, Comment
from app.domain.exceptions import ImageNotFoundError, ReviewNotFoundError, InvalidImageError
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
            patient_id=patient_id,
            filename=filename,
            s3_key=s3_key,
            content_type=content_type,
            size=len(file_content),
            tags=[],
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
            "patient_id": image.patient_id,
            "filename": image.filename,
            "s3_key": image.s3_key,
            "content_type": image.content_type,
            "size": image.size,
            "tags": image.tags,
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
                "patient_id": img.patient_id,
                "filename": img.filename,
                "s3_key": img.s3_key,
                "content_type": img.content_type,
                "size": img.size,
                "tags": img.tags,
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
        await self.metadata_repo.save_metadata(new_meta)
        
        image.patient_id = patient_id
        await self.image_repo.save_image(image)
        
        return new_meta

    async def get_patient_images(self, patient_id: str) -> List[Dict[str, Any]]:
        images = await self.image_repo.list_images()
        result = []
        for img in images:
            if img.patient_id == patient_id:
                meta = await self.metadata_repo.get_metadata(img.id)
                result.append({
                    "id": img.id,
                    "patient_id": img.patient_id,
                    "filename": img.filename,
                    "s3_key": img.s3_key,
                    "content_type": img.content_type,
                    "size": img.size,
                    "tags": img.tags,
                    "uploaded_at": img.uploaded_at,
                    "metadata": meta
                })
        return result

    async def get_system_stats(self) -> Dict[str, Any]:
        return await self.review_repo.get_global_stats()

    async def list_reviewers(self) -> List[str]:
        return await self.review_repo.get_unique_reviewers()

    async def get_reviewer_stats(self, reviewer_name: str) -> Dict[str, Any]:
        return await self.review_repo.get_reviewer_stats(reviewer_name)

    async def delete_comment(self, review_id: str, comment_index: int) -> ImageReview:
        review = await self.review_repo.get_review(review_id)
        if not review:
            raise ReviewNotFoundError(review_id)
        if comment_index < 0 or comment_index >= len(review.comments):
            raise IndexError("Comment index out of range")
        review.comments.pop(comment_index)
        return await self.review_repo.save_review(review)

    async def update_comment(self, review_id: str, comment_index: int, text: str) -> ImageReview:
        review = await self.review_repo.get_review(review_id)
        if not review:
            raise ReviewNotFoundError(review_id)
        if comment_index < 0 or comment_index >= len(review.comments):
            raise IndexError("Comment index out of range")
        review.comments[comment_index].text = text
        return await self.review_repo.save_review(review)

    async def add_tag(self, image_id: str, tag: str) -> List[str]:
        image = await self.image_repo.get_image(image_id)
        if not image:
            raise ImageNotFoundError(image_id)
        return await self.image_repo.add_tag(image_id, tag)

    async def remove_tag(self, image_id: str, tag: str) -> List[str]:
        image = await self.image_repo.get_image(image_id)
        if not image:
            raise ImageNotFoundError(image_id)
        return await self.image_repo.remove_tag(image_id, tag)

    async def list_images_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        images = await self.image_repo.get_images_by_tag(tag)
        result = []
        for img in images:
            meta = await self.metadata_repo.get_metadata(img.id)
            result.append({
                "id": img.id,
                "patient_id": img.patient_id,
                "filename": img.filename,
                "s3_key": img.s3_key,
                "content_type": img.content_type,
                "size": img.size,
                "tags": img.tags,
                "uploaded_at": img.uploaded_at,
                "metadata": meta
            })
        return result

    async def search_by_modality(self, modality: str) -> List[Dict[str, Any]]:
        images = await self.image_repo.list_images()
        result = []
        for img in images:
            meta = await self.metadata_repo.get_metadata(img.id)
            if meta and meta.modality.upper() == modality.upper():
                result.append({
                    "id": img.id,
                    "patient_id": img.patient_id,
                    "filename": img.filename,
                    "s3_key": img.s3_key,
                    "content_type": img.content_type,
                    "size": img.size,
                    "tags": img.tags,
                    "uploaded_at": img.uploaded_at,
                    "metadata": meta
                })
        return result

    async def search_by_body_part(self, body_part: str) -> List[Dict[str, Any]]:
        images = await self.image_repo.list_images()
        result = []
        for img in images:
            meta = await self.metadata_repo.get_metadata(img.id)
            if meta and meta.body_part.upper() == body_part.upper():
                result.append({
                    "id": img.id,
                    "patient_id": img.patient_id,
                    "filename": img.filename,
                    "s3_key": img.s3_key,
                    "content_type": img.content_type,
                    "size": img.size,
                    "tags": img.tags,
                    "uploaded_at": img.uploaded_at,
                    "metadata": meta
                })
        return result

    async def search_by_age(self, min_age: int, max_age: int) -> List[Dict[str, Any]]:
        images = await self.image_repo.list_images()
        result = []
        for img in images:
            meta = await self.metadata_repo.get_metadata(img.id)
            if meta and min_age <= meta.patient_age <= max_age:
                result.append({
                    "id": img.id,
                    "patient_id": img.patient_id,
                    "filename": img.filename,
                    "s3_key": img.s3_key,
                    "content_type": img.content_type,
                    "size": img.size,
                    "tags": img.tags,
                    "uploaded_at": img.uploaded_at,
                    "metadata": meta
                })
        return result

    async def reprocess_image(self, image_id: str) -> ImageMetadata:
        image = await self.image_repo.get_image(image_id)
        if not image:
            raise ImageNotFoundError(image_id)
        try:
            content = await self.storage.download_file(image.s3_key)
        except Exception as e:
            raise InvalidImageError(f"Could not retrieve raw file from storage: {e}")
        
        width, height = get_image_dimensions(content)
        
        current_meta = await self.metadata_repo.get_metadata(image_id)
        if not current_meta:
            raise ImageNotFoundError(f"Metadata for image '{image_id}' not found.")
            
        current_meta.width = width
        current_meta.height = height
        return await self.metadata_repo.save_metadata(current_meta)

    async def update_review_status(self, review_id: str, status: str) -> ImageReview:
        review = await self.review_repo.get_review(review_id)
        if not review:
            raise ReviewNotFoundError(review_id)
        review.status = status
        return await self.review_repo.save_review(review)

    async def list_pending_reviews(self) -> List[ImageReview]:
        return await self.review_repo.get_reviews_by_status("PENDING")

    async def list_all_patients(self) -> List[str]:
        return await self.image_repo.get_unique_patients()

    async def get_image_reviews_count(self, image_id: str) -> int:
        image = await self.image_repo.get_image(image_id)
        if not image:
            raise ImageNotFoundError(image_id)
        return await self.review_repo.count_reviews_by_image(image_id)
