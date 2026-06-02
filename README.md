# Medical Image Reviewer API

A high-performance backend API designed for medical image upload, metadata tracking, and clinical reviews. The project is implemented using FastAPI and strict Hexagonal (Ports and Adapters) architecture, using AWS S3 for image files, DynamoDB for metadata lookups, and MongoDB for reviews and general indexes.

## Architecture

This project is built using Hexagonal Architecture to isolate core business rules from external libraries, frameworks, and databases:

*   **Domain Layer**: Contains the core business entities and rules. It has no dependencies on databases or frameworks.
*   **Ports Layer**: Defines interfaces (contracts) for input boundaries (use cases) and output boundaries (repositories and external storage).
*   **Adapters Layer**: Concrete implementations of the ports. Input adapters handle HTTP requests (FastAPI), while output adapters connect to MongoDB, DynamoDB, and S3.
*   **Core/DI**: Manages configuration settings and wiring/dependency injection.

### Project Layout

```
/app
  /domain
    /models.py
    /exceptions.py
  /ports
    /inputs.py
    /outputs.py
  /adapters
    /inputs
      /api
        /v1
          /routers.py
        /actuator.py
    /outputs
      /db
        /mongodb.py
        /dynamodb.py
      /storage
        /s3.py
  /core
    /config.py
    /container.py
    /use_cases.py
  /utils
    /image_utils.py
  /main.py
/docker
  /localstack
    /init-aws.py
Dockerfile
docker-compose.yml
requirements.txt
verify.py
README.md
```

## Storage Map

| Component | Storage | Purpose |
| :--- | :--- | :--- |
| **Medical Images** | AWS S3 (LocalStack) | Raw image binaries (e.g. PNG/JPG representation of X-Rays/CTs). |
| **Image Metadata** | AWS DynamoDB (LocalStack) | Patient and image technical specifications, optimized for fast lookups. |
| **General Info & Reviews** | MongoDB | General image database manifests, clinical review documents, and nested comments. |

## Endpoints

### API v1 Endpoints

*   `POST /api/v1/images/upload`: Upload image binary and form data metadata.
*   `GET /api/v1/images/{image_id}`: Get consolidated image metadata and review reports.
*   `GET /api/v1/images/{image_id}/download`: Get temporary S3 download link.
*   `DELETE /api/v1/images/{image_id}`: Delete image from S3, DynamoDB, MongoDB, and delete reviews.
*   `GET /api/v1/images`: List all registered images.
*   `POST /api/v1/images/{image_id}/reviews`: Submit a clinical review.
*   `GET /api/v1/images/{image_id}/reviews`: List all reviews for an image.
*   `POST /api/v1/reviews/{review_id}/comments`: Append comments to a clinical review.
*   `PUT /api/v1/images/{image_id}/metadata`: Update patient metadata.
*   `GET /api/v1/patients/{patient_id}/images`: Get all images associated with a patient ID.
*   `GET /api/v1/stats`: Retrieve clinical aggregation statistics.

### Actuator Endpoints

*   `GET /actuator/health`: System health status (verifies S3, DynamoDB, MongoDB connections).
*   `GET /actuator/info`: App version and configuration details.
*   `GET /actuator/metrics`: CPU/memory process metrics and application statistics.

## How to Run

### Prerequisites

*   Docker and Docker Compose
*   Python 3.11+ (if running tests locally)

### Steps

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/JuanBernal13/medical-image-uploader.git
    cd medical-image-uploader
    ```

2.  **Start Services via Docker Compose**:
    ```bash
    docker compose up --build -d
    ```
    This spins up MongoDB, LocalStack (S3 + DynamoDB), and the FastAPI application in the background.

3.  **Explore API Documentation**:
    Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser to view the OpenAPI Swagger interface.

4.  **Run Integration Verification Script**:
    Verify all 14 endpoints end-to-end:
    ```bash
    pip install -r requirements.txt
    python verify.py
    ```
