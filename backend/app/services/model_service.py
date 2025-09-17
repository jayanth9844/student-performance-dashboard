import joblib
import pandas as pd
import os
import time
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.config import settings

# Try to import Redis cache, but make it optional
try:
    from app.cache.redis_cache import set_cached_prediction, get_cached_prediction
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Safe model loading with error handling for Render deployment
def load_models():
    """Load ML models with proper error handling for deployment"""
    try:
        model_path = Path(settings.MODEL_PATH)
        scaler_path = Path(settings.SCALER_PATH)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found at {model_path}")
        if not scaler_path.exists():
            raise FileNotFoundError(f"Scaler file not found at {scaler_path}")
            
        model = joblib.load(str(model_path))
        scaler = joblib.load(str(scaler_path))
        return model, scaler
    except Exception as e:
        print(f"Error loading models: {e}")
        # For development/testing, create dummy models
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
        import numpy as np
        
        print("Creating dummy models for development...")
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        scaler = StandardScaler()
        
        # Fit with dummy data
        dummy_data = np.random.rand(100, 5)
        dummy_targets = np.random.rand(100) * 100
        scaler.fit(dummy_data)
        model.fit(scaler.transform(dummy_data), dummy_targets)
        
        return model, scaler

model, scaler = load_models()

def _generate_cache_key(data: dict) -> str:
    """Generate consistent cache key for student data"""
    sorted_data = {k: data[k] for k in sorted(data.keys())}
    data_str = json.dumps(sorted_data, sort_keys=True)
    return hashlib.md5(data_str.encode()).hexdigest()[:16]  # Shorter keys for Redis free tier

def predict_assignment_score(data: dict) -> float:
    """Predict assignment score for a single student with optional caching"""
    prediction_float = None
    
    # Try cache only if Redis is available and working
    if REDIS_AVAILABLE:
        try:
            cache_key = _generate_cache_key(data)
            cached = get_cached_prediction(cache_key)
            if cached:
                return cached
        except Exception:
            pass  # Continue without cache if Redis fails
    
    # Create DataFrame with correct column order
    feature_columns = ["comprehension", "attention", "focus", "retention", "engagement_time"]
    input_data = pd.DataFrame([data])[feature_columns]
    
    # Apply scaling
    input_data_scaled = scaler.transform(input_data)
    
    # Make prediction
    prediction = model.predict(input_data_scaled)[0]
    prediction_float = float(prediction)
    
    # Try to cache only for Redis free tier (short expiration)
    if REDIS_AVAILABLE:
        try:
            cache_key = _generate_cache_key(data)
            set_cached_prediction(cache_key, prediction_float, expire_time=300)  # 5 minutes only
        except Exception:
            pass  # Continue without caching if Redis fails
    
    return prediction_float

def predict_batch_assignment_scores(student_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Efficient batch prediction optimized for Render free tier
    Uses minimal caching to work with Redis 25MB limit
    """
    start_time = time.time()
    cache_hits = 0
    
    # For Redis free tier, we'll use very light caching or no caching
    predictions = []
    
    # Process in smaller batches to be memory efficient
    batch_size = 25  # Smaller batches for free tier
    
    for batch_start in range(0, len(student_data_list), batch_size):
        batch_end = min(batch_start + batch_size, len(student_data_list))
        batch_data = student_data_list[batch_start:batch_end]
        
        # Check cache for this batch (only if Redis available)
        batch_predictions = []
        uncached_data = []
        uncached_indices = []
        
        for i, data in enumerate(batch_data):
            cached_pred = None
            
            if REDIS_AVAILABLE:
                try:
                    cache_key = _generate_cache_key(data)
                    cached_pred = get_cached_prediction(cache_key)
                    if cached_pred:
                        cache_hits += 1
                except Exception:
                    pass
            
            if cached_pred is not None:
                batch_predictions.append({
                    "student_index": batch_start + i,
                    "predicted_score": cached_pred,
                    "cached": True
                })
            else:
                uncached_data.append(data)
                uncached_indices.append(batch_start + i)
        
        # Process uncached predictions
        if uncached_data:
            feature_columns = ["comprehension", "attention", "focus", "retention", "engagement_time"]
            batch_df = pd.DataFrame(uncached_data)[feature_columns]
            batch_scaled = scaler.transform(batch_df)
            batch_preds = model.predict(batch_scaled)
            
            # Store results and optionally cache
            for i, pred in enumerate(batch_preds):
                pred_float = float(pred)
                student_index = uncached_indices[i]
                
                batch_predictions.append({
                    "student_index": student_index,
                    "predicted_score": pred_float,
                    "cached": False
                })
                
                # Light caching for Redis free tier
                if REDIS_AVAILABLE:
                    try:
                        cache_key = _generate_cache_key(uncached_data[i])
                        set_cached_prediction(cache_key, pred_float, expire_time=300)  # 5 minutes
                    except Exception:
                        pass
        
        predictions.extend(batch_predictions)
    
    # Sort predictions by student_index to maintain order
    predictions.sort(key=lambda x: x["student_index"])
    
    processing_time = (time.time() - start_time) * 1000
    
    return {
        "predictions": predictions,
        "total_processed": len(student_data_list),
        "cache_hits": cache_hits,
        "processing_time_ms": round(processing_time, 2),
        "redis_available": REDIS_AVAILABLE
    }