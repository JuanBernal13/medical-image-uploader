from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.domain.models import MedicalImage, ImageReview, Comment
from app.ports.outputs import ImageRepositoryPort, ReviewRepositoryPort

class MongoDBRepository(ImageRepositoryPort, ReviewRepositoryPort):
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        db_name = settings.MONGODB_URI.split("/")[-1].split("?")[0]
        if not db_name:
            db_name = "medical_db"
        self.db = self.client[db_name]
        self.images_col = self.db["images"]
        self.reviews_col = self.db["reviews"]

    async def save_image(self, image: MedicalImage) -> MedicalImage:
        doc = {
            "_id": image.id,
            "filename": image.filename,
            "s3_key": image.s3_key,
            "content_type": image.content_type,
            "size": image.size,
            "uploaded_at": image.uploaded_at
        }
        await self.images_col.replace_one({"_id": image.id}, doc, upsert=True)
        return image

    async def get_image(self, image_id: str) -> Optional[MedicalImage]:
        doc = await self.images_col.find_one({"_id": image_id})
        if not doc:
            return None
        return MedicalImage(
            id=doc["_id"],
            filename=doc["filename"],
            s3_key=doc["s3_key"],
            content_type=doc["content_type"],
            size=doc["size"],
            uploaded_at=doc["uploaded_at"]
        )

    async def list_images(self) -> List[MedicalImage]:
        cursor = self.images_col.find()
        images = []
        async for doc in cursor:
            images.append(MedicalImage(
                id=doc["_id"],
                filename=doc["filename"],
                s3_key=doc["s3_key"],
                content_type=doc["content_type"],
                size=doc["size"],
                uploaded_at=doc["uploaded_at"]
            ))
        return images

    async def delete_image(self, image_id: str) -> None:
        await self.images_col.delete_one({"_id": image_id})

    async def save_review(self, review: ImageReview) -> ImageReview:
        comments_list = []
        for c in review.comments:
            comments_list.append({
                "author": c.author,
                "text": c.text,
                "created_at": c.created_at
            })
        doc = {
            "_id": review.id,
            "image_id": review.image_id,
            "reviewer_name": review.reviewer_name,
            "status": review.status,
            "findings": review.findings,
            "severity": review.severity,
            "comments": comments_list,
            "reviewed_at": review.reviewed_at
        }
        await self.reviews_col.replace_one({"_id": review.id}, doc, upsert=True)
        return review

    async def get_review(self, review_id: str) -> Optional[ImageReview]:
        doc = await self.reviews_col.find_one({"_id": review_id})
        if not doc:
            return None
        comments = [
            Comment(author=c["author"], text=c["text"], created_at=c["created_at"])
            for c in doc.get("comments", [])
        ]
        return ImageReview(
            id=doc["_id"],
            image_id=doc["image_id"],
            reviewer_name=doc["reviewer_name"],
            status=doc["status"],
            findings=doc["findings"],
            severity=doc["severity"],
            comments=comments,
            reviewed_at=doc["reviewed_at"]
        )

    async def get_reviews_by_image(self, image_id: str) -> List[ImageReview]:
        cursor = self.reviews_col.find({"image_id": image_id})
        reviews = []
        async for doc in cursor:
            comments = [
                Comment(author=c["author"], text=c["text"], created_at=c["created_at"])
                for c in doc.get("comments", [])
            ]
            reviews.append(ImageReview(
                id=doc["_id"],
                image_id=doc["image_id"],
                reviewer_name=doc["reviewer_name"],
                status=doc["status"],
                findings=doc["findings"],
                severity=doc["severity"],
                comments=comments,
                reviewed_at=doc["reviewed_at"]
            ))
        return reviews

    async def list_all_reviews(self) -> List[ImageReview]:
        cursor = self.reviews_col.find()
        reviews = []
        async for doc in cursor:
            comments = [
                Comment(author=c["author"], text=c["text"], created_at=c["created_at"])
                for c in doc.get("comments", [])
            ]
            reviews.append(ImageReview(
                id=doc["_id"],
                image_id=doc["image_id"],
                reviewer_name=doc["reviewer_name"],
                status=doc["status"],
                findings=doc["findings"],
                severity=doc["severity"],
                comments=comments,
                reviewed_at=doc["reviewed_at"]
            ))
        return reviews

    async def delete_reviews_by_image(self, image_id: str) -> None:
        await self.reviews_col.delete_many({"image_id": image_id})

    async def get_global_stats(self) -> Dict[str, Any]:
        total_images = await self.images_col.count_documents({})
        total_reviews = await self.reviews_col.count_documents({})
        
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        status_counts = {}
        cursor = self.reviews_col.aggregate(pipeline)
        async for doc in cursor:
            status_counts[doc["_id"]] = doc["count"]

        pipeline_severity = [
            {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
        ]
        severity_counts = {}
        cursor = self.reviews_col.aggregate(pipeline_severity)
        async for doc in cursor:
            severity_counts[doc["_id"]] = doc["count"]

        return {
            "total_images": total_images,
            "total_reviews": total_reviews,
            "status_distribution": status_counts,
            "severity_distribution": severity_counts
        }
