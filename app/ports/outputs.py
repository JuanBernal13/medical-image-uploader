from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.domain.models import MedicalImage, ImageMetadata, ImageReview

class ImageStoragePort(ABC):
    @abstractmethod
    async def upload_file(self, file_content: bytes, filename: str, content_type: str) -> str:
        pass

    @abstractmethod
    async def download_file(self, s3_key: str) -> bytes:
        pass

    @abstractmethod
    async def delete_file(self, s3_key: str) -> None:
        pass

    @abstractmethod
    async def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        pass


class MetadataRepositoryPort(ABC):
    @abstractmethod
    async def save_metadata(self, metadata: ImageMetadata) -> ImageMetadata:
        pass

    @abstractmethod
    async def get_metadata(self, image_id: str) -> Optional[ImageMetadata]:
        pass

    @abstractmethod
    async def update_metadata(self, metadata: ImageMetadata) -> ImageMetadata:
        pass

    @abstractmethod
    async def delete_metadata(self, image_id: str) -> None:
        pass


class ImageRepositoryPort(ABC):
    @abstractmethod
    async def save_image(self, image: MedicalImage) -> MedicalImage:
        pass

    @abstractmethod
    async def get_image(self, image_id: str) -> Optional[MedicalImage]:
        pass

    @abstractmethod
    async def list_images(self) -> List[MedicalImage]:
        pass

    @abstractmethod
    async def delete_image(self, image_id: str) -> None:
        pass

    @abstractmethod
    async def add_tag(self, image_id: str, tag: str) -> List[str]:
        pass

    @abstractmethod
    async def remove_tag(self, image_id: str, tag: str) -> List[str]:
        pass

    @abstractmethod
    async def get_images_by_tag(self, tag: str) -> List[MedicalImage]:
        pass

    @abstractmethod
    async def get_unique_patients(self) -> List[str]:
        pass


class ReviewRepositoryPort(ABC):
    @abstractmethod
    async def save_review(self, review: ImageReview) -> ImageReview:
        pass

    @abstractmethod
    async def get_review(self, review_id: str) -> Optional[ImageReview]:
        pass

    @abstractmethod
    async def get_reviews_by_image(self, image_id: str) -> List[ImageReview]:
        pass

    @abstractmethod
    async def list_all_reviews(self) -> List[ImageReview]:
        pass

    @abstractmethod
    async def delete_reviews_by_image(self, image_id: str) -> None:
        pass

    @abstractmethod
    async def get_global_stats(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_unique_reviewers(self) -> List[str]:
        pass

    @abstractmethod
    async def get_reviewer_stats(self, reviewer_name: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_reviews_by_status(self, status: str) -> List[ImageReview]:
        pass

    @abstractmethod
    async def count_reviews_by_image(self, image_id: str) -> int:
        pass
