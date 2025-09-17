from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.api import routes_auth, routes_predict, routes_clustering, routes_admin
from app.middleware.logging_middleware import LoggingMiddleware
from app.core.exceptions import register_exception_handler
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Student Performance Dashboard API",
    description="AI-powered student performance prediction and clustering API",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None
)

# Add CORS middleware for web frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else ["https://*.render.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint for Render
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        # Test Redis connection if available
        from app.cache.redis_cache import test_redis_connection
        redis_status = test_redis_connection()
        
        return {
            "status": "healthy", 
            "service": "student-performance-dashboard-api",
            "environment": settings.ENVIRONMENT,
            "redis": redis_status.get("status", "unknown")
        }
    except Exception as e:
        return {
            "status": "healthy", 
            "service": "student-performance-dashboard-api",
            "environment": settings.ENVIRONMENT,
            "redis": "unavailable",
            "note": "API functional without Redis"
        }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Student Performance Dashboard API", 
        "status": "running",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs" if settings.ENVIRONMENT != "production" else "disabled"
    }

# link Middleware
app.add_middleware(LoggingMiddleware)

#link router
app.include_router(routes_auth.router, tags=["Auth"])
app.include_router(routes_predict.router, tags=["Score Prediction"])
app.include_router(routes_clustering.router, tags=["Student Clustering"])
app.include_router(routes_admin.router, prefix="/admin", tags=["Admin"])

#monitoring using prometheus
Instrumentator().instrument(app).expose(app)

# add exception handling 
register_exception_handler(app)