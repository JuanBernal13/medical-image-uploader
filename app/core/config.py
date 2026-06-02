from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENV: str = "development"
    MONGODB_URI: str = "mongodb://localhost:27017/medical_db"
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = "mock"
    AWS_SECRET_ACCESS_KEY: str = "mock"
    AWS_S3_ENDPOINT_URL: Optional[str] = None
    AWS_DYNAMODB_ENDPOINT_URL: Optional[str] = None
    S3_BUCKET_NAME: str = "medical-images"
    DYNAMODB_TABLE_NAME: str = "MedicalImageMetadata"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
