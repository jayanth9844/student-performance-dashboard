import joblib
import pandas as pd
import os
import time
import hashlib
import json
from typing import List, Dict, Any, Optional
from app.core.config import settings

# Try to import Redis cache, but make it optional
try:
    from app.cache.redis_cache import set_cached_prediction, get_cached_prediction
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Load clustering model and scaler
kmeans_model = joblib.load(os.path.join(os.path.dirname(settings.MODEL_PATH), "kmeans_model.joblib"))
scaler = joblib.load(os.path.join(os.path.dirname(settings.MODEL_PATH), "scaler.pkl"))

# Persona mapping based on clustering analysis
PERSONA_MAPPING = {
    0: "📈 Consistent Learner",
    1: "🌟 Highly Engaged High Performer", 
    2: "💤 Low Engagement Risk",
    3: "📚 Developing Performer"
}

def _generate_cluster_cache_key(data: dict) -> str:
    """Generate consistent cache key for clustering data"""
    sorted_data = {k: data[k] for k in sorted(data.keys())}
    data_str = json.dumps(sorted_data, sort_keys=True)
    return "cluster_" + hashlib.md5(data_str.encode()).hexdigest()[:16]

def predict_student_cluster(data: dict) -> Dict[str, Any]:
    """Predict student cluster/persona with optional caching"""
    
    # Try cache only if Redis is available and working
    if REDIS_AVAILABLE:
        try:
            cache_key = _generate_cluster_cache_key(data)
            cached = get_cached_prediction(cache_key)
            if cached:
                return cached
        except Exception:
            pass  # Continue without cache if Redis fails
    
    # Create DataFrame with correct column order
    feature_columns = ["comprehension", "attention", "focus", "retention", "engagement_time"]
    input_data = pd.DataFrame([data])[feature_columns]
    
    # Apply scaling (same as used in training)
    input_data_scaled = scaler.transform(input_data)
    
    # Make cluster prediction
    cluster_label = kmeans_model.predict(input_data_scaled)[0]
    persona_name = PERSONA_MAPPING.get(int(cluster_label), "Unknown Persona")
    
    result = {
        "cluster_label": int(cluster_label),
        "persona_name": persona_name,
        "confidence": "high"  # KMeans doesn't provide probability, but we can indicate confidence
    }
    
    # Try to cache only for Redis free tier (short expiration)
    if REDIS_AVAILABLE:
        try:
            cache_key = _generate_cluster_cache_key(data)
            set_cached_prediction(cache_key, result, expire_time=300)  # 5 minutes only
        except Exception:
            pass  # Continue without caching if Redis fails
    
    return result

def predict_batch_student_clusters(student_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Efficient batch clustering prediction optimized for Render free tier
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
                    cache_key = _generate_cluster_cache_key(data)
                    cached_pred = get_cached_prediction(cache_key)
                    if cached_pred:
                        cache_hits += 1
                except Exception:
                    pass
            
            if cached_pred is not None:
                batch_predictions.append({
                    "student_index": batch_start + i,
                    "cluster_label": cached_pred["cluster_label"],
                    "persona_name": cached_pred["persona_name"],
                    "confidence": cached_pred["confidence"],
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
            batch_clusters = kmeans_model.predict(batch_scaled)
            
            # Store results and optionally cache
            for i, cluster_label in enumerate(batch_clusters):
                cluster_int = int(cluster_label)
                persona_name = PERSONA_MAPPING.get(cluster_int, "Unknown Persona")
                student_index = uncached_indices[i]
                
                result = {
                    "student_index": student_index,
                    "cluster_label": cluster_int,
                    "persona_name": persona_name,
                    "confidence": "high",
                    "cached": False
                }
                
                batch_predictions.append(result)
                
                # Light caching for Redis free tier
                if REDIS_AVAILABLE:
                    try:
                        cache_key = _generate_cluster_cache_key(uncached_data[i])
                        cache_result = {
                            "cluster_label": cluster_int,
                            "persona_name": persona_name,
                            "confidence": "high"
                        }
                        set_cached_prediction(cache_key, cache_result, expire_time=300)  # 5 minutes
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
        "redis_available": REDIS_AVAILABLE,
        "available_personas": list(PERSONA_MAPPING.values())
    }
