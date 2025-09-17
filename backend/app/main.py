from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.api import routes_auth, routes_predict, routes_clustering, routes_admin
from app.middleware.logging_middleware import LoggingMiddleware
from app.core.exceptions import register_exception_handler


app = FastAPI(title="Student Performance Dashboard API")

# Health check endpoint for Render
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "service": "student-performance-dashboard-api"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Student Performance Dashboard API", "status": "running"}

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