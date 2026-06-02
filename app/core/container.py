from app.adapters.outputs.storage.s3 import S3ImageStorage
from app.adapters.outputs.db.dynamodb import DynamoDBMetadataRepository
from app.adapters.outputs.db.mongodb import MongoDBRepository
from app.core.use_cases import MedicalImageService

class Container:
    _storage = None
    _metadata_repo = None
    _mongo_repo = None
    _image_service = None

    @classmethod
    def get_storage(cls) -> S3ImageStorage:
        if cls._storage is None:
            cls._storage = S3ImageStorage()
        return cls._storage

    @classmethod
    def get_metadata_repo(cls) -> DynamoDBMetadataRepository:
        if cls._metadata_repo is None:
            cls._metadata_repo = DynamoDBMetadataRepository()
        return cls._metadata_repo

    @classmethod
    def get_mongo_repo(cls) -> MongoDBRepository:
        if cls._mongo_repo is None:
            cls._mongo_repo = MongoDBRepository()
        return cls._mongo_repo

    @classmethod
    def get_image_service(cls) -> MedicalImageService:
        if cls._image_service is None:
            cls._image_service = MedicalImageService(
                storage=cls.get_storage(),
                metadata_repo=cls.get_metadata_repo(),
                image_repo=cls.get_mongo_repo(),
                review_repo=cls.get_mongo_repo()
            )
        return cls._image_service
