from fastapi import FastAPI
from app.adapters.inputs.api.v1.routers import router as api_router
from app.adapters.inputs.api.actuator import router as actuator_router

app = FastAPI(
    title="Medical Image Reviewer API",
    version="1.0.0",
    description="Backend API following Hexagonal architecture (FastAPI, MongoDB, DynamoDB, AWS S3)"
)

app.include_router(api_router)
app.include_router(actuator_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Medical Image Reviewer API. Visit /docs for API documentation."}
