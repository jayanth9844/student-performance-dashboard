from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.api  import routes_auth ,routes_predict
from app.middleware.logging_middleware import LoggingMiddleware
from app.core.exceptions import register_exception_handler


app = FastAPI(title="student score prediction")

# link Middleware
app.add_middleware(LoggingMiddleware)

#link router
app.include_router(routes_auth.router ,tags=["Auth"])
app.include_router(routes_predict.router,tags=["prediction"])

#monitoring using prometheus
Instrumentator().instrument(app).expose(app)

# add exception handling 
register_exception_handler(app)