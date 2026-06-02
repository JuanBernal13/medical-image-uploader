from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from app.core.container import Container
from app.domain.exceptions import ImageNotFoundError, ReviewNotFoundError

router = APIRouter(prefix="/api/v1", tags=["medical-images"])

class ReviewCreateRequest(BaseModel):
    reviewer_name: str
    status: str
    findings: str
    severity: str

class CommentCreateRequest(BaseModel):
    author: str
    text: str

class MetadataUpdateRequest(BaseModel):
    patient_id: str
    modality: str
    body_part: str
    patient_age: int
    patient_gender: str

@router.post("/images/upload", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    modality: str = Form(...),
    body_part: str = Form(...),
    patient_age: int = Form(...),
    patient_gender: str = Form(...)
):
    content = await file.read()
    service = Container.get_image_service()
    result = await service.upload_image(
        file_content=content,
        filename=file.filename,
        content_type=file.content_type,
        patient_id=patient_id,
        modality=modality,
        body_part=body_part,
        patient_age=patient_age,
        patient_gender=patient_gender
    )
    return result

@router.get("/images/{image_id}")
async def get_image_details(image_id: str):
    try:
        service = Container.get_image_service()
        return await service.get_image_details(image_id)
    except ImageNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/images/{image_id}/download")
async def get_image_download_url(image_id: str):
    try:
        service = Container.get_image_service()
        url = await service.get_image_download_url(image_id)
        return {"download_url": url}
    except ImageNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(image_id: str):
    try:
        service = Container.get_image_service()
        await service.delete_image(image_id)
    except ImageNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/images")
async def list_images():
    service = Container.get_image_service()
    return await service.list_images()

@router.post("/images/{image_id}/reviews", status_code=status.HTTP_201_CREATED)
async def create_review(image_id: str, request: ReviewCreateRequest):
    try:
        service = Container.get_image_service()
        return await service.add_review(
            image_id=image_id,
            reviewer_name=request.reviewer_name,
            status=request.status,
            findings=request.findings,
            severity=request.severity
        )
    except ImageNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/images/{image_id}/reviews")
async def get_image_reviews(image_id: str):
    try:
        service = Container.get_image_service()
        return await service.get_image_reviews(image_id)
    except ImageNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/reviews/{review_id}/comments", status_code=status.HTTP_201_CREATED)
async def add_review_comment(review_id: str, request: CommentCreateRequest):
    try:
        service = Container.get_image_service()
        return await service.add_review_comment(
            review_id=review_id,
            author=request.author,
            text=request.text
        )
    except ReviewNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/images/{image_id}/metadata")
async def update_image_metadata(image_id: str, request: MetadataUpdateRequest):
    try:
        service = Container.get_image_service()
        return await service.update_image_metadata(
            image_id=image_id,
            patient_id=request.patient_id,
            modality=request.modality,
            body_part=request.body_part,
            patient_age=request.patient_age,
            patient_gender=request.patient_gender
        )
    except ImageNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/patients/{patient_id}/images")
async def get_patient_images(patient_id: str):
    service = Container.get_image_service()
    return await service.get_patient_images(patient_id)

@router.get("/stats")
async def get_stats():
    service = Container.get_image_service()
    return await service.get_system_stats()
