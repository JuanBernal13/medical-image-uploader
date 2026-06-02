from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class Comment(BaseModel):
    author: str
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MedicalImage(BaseModel):
    id: str
    filename: str
    s3_key: str
    content_type: str
    size: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class ImageMetadata(BaseModel):
    image_id: str
    patient_id: str
    modality: str
    body_part: str
    patient_age: int
    patient_gender: str
    width: int
    height: int

class ImageReview(BaseModel):
    id: str
    image_id: str
    reviewer_name: str
    status: str
    findings: str
    severity: str
    comments: List[Comment] = Field(default_factory=list)
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)
