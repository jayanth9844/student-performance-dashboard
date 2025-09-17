from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.api import routes_auth, routes_predict, routes_clustering, routes_admin
from app.middleware.logging_middleware import LoggingMiddleware
from app.core.exceptions import register_exception_handler


app = FastAPI(title="Student Performance Dashboard API")

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