# Medical Image Reviewer API

A high-performance backend API designed for medical image upload, metadata tracking, and clinical reviews. The project is implemented using FastAPI and  Hexagonal (Ports and Adapters) architecture, using AWS S3 for image files, DynamoDB for metadata lookups, and MongoDB for reviews and general indexes.

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

## Endpoints (26 Total)

### Clinical API v1 Router

#### Image Operations
1.  `POST /api/v1/images/upload`: Upload image binary and form data metadata.
2.  `GET /api/v1/images/{image_id}`: Get consolidated image metadata and review reports.
3.  `GET /api/v1/images/{image_id}/download`: Get temporary S3 download link.
4.  `DELETE /api/v1/images/{image_id}`: Delete image from S3, DynamoDB, MongoDB, and delete reviews.
5.  `GET /api/v1/images`: List all registered images.
6.  `POST /api/v1/images/{image_id}/reprocess`: Re-reads the raw file from S3, extracts dimensions, and updates DynamoDB.

#### Annotations & Tags
7.  `POST /api/v1/images/{image_id}/tags`: Add search tags (e.g. "Urgent", "Cardiology") to an image.
8.  `DELETE /api/v1/images/{image_id}/tags/{tag}`: Delete a search tag from an image.
9.  `GET /api/v1/images/tags/{tag}`: List all images matching a specific tag.

#### Image Search queries
10. `GET /api/v1/images/search/modality/{modality}`: Find images by modality (e.g. MRI, XRAY).
11. `GET /api/v1/images/search/body-part/{body_part}`: Find images by body part.
12. `GET /api/v1/images/search/age`: Query images by patient age range (e.g., `?min_age=20&max_age=60`).

#### Clinical Reviews & Comments
13. `POST /api/v1/images/{image_id}/reviews`: Submit a clinical review.
14. `GET /api/v1/images/{image_id}/reviews`: List all reviews for an image.
15. `GET /api/v1/images/{image_id}/reviews/count`: Get the number of reviews written for an image.
16. `PATCH /api/v1/reviews/{review_id}/status`: Modify review report status.
17. `GET /api/v1/reviews/pending`: List all review reports currently pending.
18. `POST /api/v1/reviews/{review_id}/comments`: Append comments to a clinical review.
19. `PUT /api/v1/reviews/{review_id}/comments/{comment_index}`: Edit comments at a specific index.
20. `DELETE /api/v1/reviews/{review_id}/comments/{comment_index}`: Delete comments at a specific index.

#### Patient & Reviewer stats
21. `PUT /api/v1/images/{image_id}/metadata`: Update patient metadata.
22. `GET /api/v1/patients/{patient_id}/images`: Get all images associated with a patient ID.
23. `GET /api/v1/patients`: List all unique patient IDs in the system.
24. `GET /api/v1/reviewers`: List all unique reviewer names in the database.
25. `GET /api/v1/reviewers/{reviewer_name}/stats`: Performance statistics for a specific reviewer.
26. `GET /api/v1/stats`: Retrieve clinical aggregation statistics.

### System & Health Actuator Router

27. `GET /actuator/health`: System health status (verifies S3, DynamoDB, MongoDB connections).
28. `GET /actuator/info`: App version and configuration details.
29. `GET /actuator/metrics`: CPU/memory process metrics and application statistics.

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
    Verify all endpoints end-to-end:
    ```bash
    pip install -r requirements.txt
    python verify.py
    ```
