import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = "Student Performance API"
    API_KEY = os.getenv("API_KEY", "demo_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret")
    JWT_ALGORITHM = "HS256"
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Dynamic model paths for Render deployment
    BASE_DIR = Path(__file__).parent.parent
    MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "model.joblib"))
    CLUSTER_MODEL_PATH = os.getenv("CLUSTER_MODEL_PATH", str(BASE_DIR / "models" / "cluster_model.joblib"))
    SCALER_PATH = os.getenv("SCALER_PATH", str(BASE_DIR / "models" / "scaler.pkl"))
    
    # Environment settings
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Render-specific settings
    PORT = int(os.getenv("PORT", 8000))

settings = Settings()
