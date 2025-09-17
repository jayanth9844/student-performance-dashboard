import joblib
import pandas as pd
import os
from app.core.config import settings
from app.cache.redis_cache import set_cached_prediction,get_cached_prediction


model = joblib.load(settings.MODEL_PATH)
scaler = joblib.load(os.path.join(os.path.dirname(settings.MODEL_PATH), "scaler.pkl"))

def predict_assignment_score(data:dict):
    cache_key = " ".join([str(val) for val in data.values()])
    cached = get_cached_prediction(cache_key)
    if cached:
        return cached
    
    # Create DataFrame with correct column order
    feature_columns = ["comprehension", "attention", "focus", "retention", "engagement_time"]
    input_data = pd.DataFrame([data])[feature_columns]
    
    # Apply scaling (same as used in training)
    input_data_scaled = scaler.transform(input_data)
    
    prediction = model.predict(input_data_scaled)[0]
    set_cached_prediction(cache_key, prediction)
    return float(prediction)