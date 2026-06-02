from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.domain.models import ImageMetadata, ImageReview

class MedicalImageUseCase(ABC):
    @abstractmethod
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
        pass

    @abstractmethod
    async def get_image_details(self, image_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_image_download_url(self, image_id: str) -> str:
        pass

    @abstractmethod
    async def delete_image(self, image_id: str) -> None:
        pass

    @abstractmethod
    async def list_images(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def add_review(
        self,
        image_id: str,
        reviewer_name: str,
        status: str,
        findings: str,
        severity: str
    ) -> ImageReview:
        pass

    @abstractmethod
    async def get_image_reviews(self, image_id: str) -> List[ImageReview]:
        pass

    @abstractmethod
    async def add_review_comment(self, review_id: str, author: str, text: str) -> ImageReview:
        pass

    @abstractmethod
    async def update_image_metadata(
        self,
        image_id: str,
        patient_id: str,
        modality: str,
        body_part: str,
        patient_age: int,
        patient_gender: str
    ) -> ImageMetadata:
        pass

    @abstractmethod
    async def get_patient_images(self, patient_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_system_stats(self) -> Dict[str, Any]:
        pass
