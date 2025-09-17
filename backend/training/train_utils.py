import os

# Get the directory of this file (training directory)
TRAINING_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the backend directory (parent of training)
BACKEND_DIR = os.path.dirname(TRAINING_DIR)
# Get the project root directory (parent of backend)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

# Data paths
DATA_DIR = os.path.join(BACKEND_DIR, "data")
DATA_FILE_NAME = "student_personas_named.csv"
DATA_FILE_PATH = os.path.join(DATA_DIR, DATA_FILE_NAME)

# Model paths
APP_DIR = os.path.join(BACKEND_DIR, "app")
MODEL_DIR_NAME = "models"
MODEL_NAME = "model.joblib"
MODEL_DIR = os.path.join(APP_DIR, MODEL_DIR_NAME)
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)