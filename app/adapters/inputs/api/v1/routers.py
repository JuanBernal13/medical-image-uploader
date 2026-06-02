from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from app.core.container import Container
from app.domain.exceptions import ImageNotFoundError, ReviewNotFoundError, InvalidImageError

router = APIRouter(prefix="/api/v1", tags=["medical-images"])

class ReviewCreateRequest(BaseModel):
    reviewer_name: str
    status: str
    findings: str
    severity: str

class CommentCreateRequest(BaseModel):
    author: str
    text: str

class CommentUpdateRequest(BaseModel):
    text: str

class MetadataUpdateRequest(BaseModel):
    patient_id: str
    modality: str
    body_part: str
    patient_age: int
    patient_gender: str

class TagRequest(BaseModel):
    tag: str

class StatusUpdateRequest(BaseModel):
    status: str

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

@router.get("/reviewers")
async def list_reviewers():
    service = Container.get_image_service()
    return await service.list_reviewers()

@router.get("/reviewers/{reviewer_name}/stats")
async def get_reviewer_stats(reviewer_name: str):
    service = Container.get_image_service()
    return await service.get_reviewer_stats(reviewer_name)

@router.delete("/reviews/{review_id}/comments/{comment_index}")
async def delete_comment(review_id: str, comment_index: int):
    try:
        service = Container.get_image_service()
        return await service.delete_comment(review_id, comment_index)
    except ReviewNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except IndexError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/reviews/{review_id}/comments/{comment_index}")
async def update_comment(review_id: str, comment_index: int, request: CommentUpdateRequest):
    try:
        service = Container.get_image_service()
        return await service.update_comment(review_id, comment_index, request.text)
    except ReviewNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except IndexError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/images/{image_id}/tags")
async def add_tag(image_id: str, request: TagRequest):
    try:
        service = Container.get_image_service()
        return await service.add_tag(image_id, request.tag)
    except ImageNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/images/{image_id}/tags/{tag}")
async def remove_tag(image_id: str, tag: str):
    try:
        service = Container.get_image_service()
        return await service.remove_tag(image_id, tag)
    except ImageNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/images/tags/{tag}")
async def list_images_by_tag(tag: str):
    service = Container.get_image_service()
    return await service.list_images_by_tag(tag)

@router.get("/images/search/modality/{modality}")
async def search_by_modality(modality: str):
    service = Container.get_image_service()
    return await service.search_by_modality(modality)

@router.get("/images/search/body-part/{body_part}")
async def search_by_body_part(body_part: str):
    service = Container.get_image_service()
    return await service.search_by_body_part(body_part)

@router.get("/images/search/age")
async def search_by_age(min_age: int = 0, max_age: int = 120):
    service = Container.get_image_service()
    return await service.search_by_age(min_age, max_age)

@router.post("/images/{image_id}/reprocess")
async def reprocess_image(image_id: str):
    try:
        service = Container.get_image_service()
        return await service.reprocess_image(image_id)
    except ImageNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidImageError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

@router.patch("/reviews/{review_id}/status")
async def update_review_status(review_id: str, request: StatusUpdateRequest):
    try:
        service = Container.get_image_service()
        return await service.update_review_status(review_id, request.status)
    except ReviewNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/reviews/pending")
async def list_pending_reviews():
    service = Container.get_image_service()
    return await service.list_pending_reviews()

@router.get("/patients")
async def list_all_patients():
    service = Container.get_image_service()
    return await service.list_all_patients()

@router.get("/images/{image_id}/reviews/count")
async def get_image_reviews_count(image_id: str):
    try:
        service = Container.get_image_service()
        count = await service.get_image_reviews_count(image_id)
        return {"image_id": image_id, "reviews_count": count}
    except ImageNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
