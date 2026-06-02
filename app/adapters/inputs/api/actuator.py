import os
import asyncio
from fastapi import APIRouter, Response, status
import psutil
from app.core.config import settings
from app.core.container import Container

router = APIRouter(prefix="/actuator", tags=["actuator"])

@router.get("/health")
async def health(response: Response):
    mongo_status = "DOWN"
    mongo_details = {}
    try:
        mongo_repo = Container.get_mongo_repo()
        await mongo_repo.db.command("ping")
        mongo_status = "UP"
        mongo_details = {"database": mongo_repo.db.name}
    except Exception as e:
        mongo_details = {"error": str(e)}

    dynamodb_status = "DOWN"
    dynamodb_details = {}
    try:
        metadata_repo = Container.get_metadata_repo()
        await asyncio.to_thread(lambda: metadata_repo.table.table_status)
        dynamodb_status = "UP"
        dynamodb_details = {"table": settings.DYNAMODB_TABLE_NAME}
    except Exception as e:
        dynamodb_details = {"error": str(e)}

    s3_status = "DOWN"
    s3_details = {}
    try:
        storage = Container.get_storage()
        await asyncio.to_thread(
            storage.s3_client.head_bucket,
            Bucket=settings.S3_BUCKET_NAME
        )
        s3_status = "UP"
        s3_details = {"bucket": settings.S3_BUCKET_NAME}
    except Exception as e:
        s3_details = {"error": str(e)}

    overall_status = "UP" if (mongo_status == "UP" and dynamodb_status == "UP" and s3_status == "UP") else "DOWN"
    
    if overall_status == "DOWN":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": overall_status,
        "components": {
            "mongodb": {"status": mongo_status, "details": mongo_details},
            "dynamodb": {"status": dynamodb_status, "details": dynamodb_details},
            "s3": {"status": s3_status, "details": s3_details}
        }
    }

@router.get("/info")
async def info():
    return {
        "app": {
            "name": "Medical Image Reviewer API",
            "version": "1.0.0",
            "environment": settings.ENV,
            "description": "Backend API following Hexagonal architecture storing images on S3, metadata on DynamoDB, and reviews on MongoDB"
        }
    }

@router.get("/metrics")
async def metrics():
    process = psutil.Process(os.getpid())
    try:
        db_stats = await Container.get_image_service().get_system_stats()
    except Exception:
        db_stats = {}
    return {
        "system": {
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_usage_bytes": process.memory_info().rss,
            "threads_count": process.num_threads()
        },
        "application": db_stats
    }
