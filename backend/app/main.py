from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.api.v1 import auth, ai_assistant, document_digitizing

# Import dependencies for proper loading
from app.api.dependencies import get_current_user

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Healthcare Management System API",
    version="1.0.0",
    debug=settings.DEBUG
)

app.include_router(
    document_digitizing.router,
    prefix=f"{settings.API_V1_PREFIX}/documents",
    tags=["Document Digitizing"]
)

# CORS Middleware - Allow Flutter app to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Flutter app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers

app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"]
)
app.include_router(
    ai_assistant.router,
    prefix=f"{settings.API_V1_PREFIX}/ai",
    tags=["AI Medical Assistant"]
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Welcome to Aarogyan API",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "environment": "development" if settings.DEBUG else "production"
    }
