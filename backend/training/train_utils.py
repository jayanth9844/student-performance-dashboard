import os
DATA_DIR = "backend\data"
DATA_FILE_NAME = "student_personas_named.csv"
DATA_FILE_PATH = os.path.join(DATA_DIR,DATA_FILE_NAME)

APP_DIR = "backend\app"
MODEL_DIR_NAME = "backend\models"
MODEL_NAME = "model.joblib"
MODEL_DIR = os.path.join(APP_DIR,MODEL_DIR_NAME)
MODEL_PATH = os.path.join(MODEL_DIR,MODEL_NAME)