import json 
import redis
from typing import List, Dict, Any, Optional
from app.core.config import settings

# Initialize Redis client with error handling for free tier
try:
    redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=5)
    # Test connection
    redis_client.ping()
except (redis.RedisError, ConnectionError):
    redis_client = None

def get_cached_prediction(key: str) -> Optional[float]:
    """Get single cached prediction"""
    if redis_client is None:
        return None
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except (redis.RedisError, json.JSONDecodeError):
        return None

def set_cached_prediction(key: str, value: float, expire_time: int = 300) -> bool:
    """Set single cached prediction with expiration (default 5 minutes for free tier)"""
    if redis_client is None:
        return False
    try:
        redis_client.setex(key, expire_time, json.dumps(value))
        return True
    except redis.RedisError:
        return False

def get_multiple_cached_predictions(keys: List[str]) -> List[Optional[float]]:
    """Get multiple cached predictions using Redis pipeline for efficiency"""
    if not keys:
        return []
    
    try:
        pipe = redis_client.pipeline()
        for key in keys:
            pipe.get(key)
        results = pipe.execute()
        
        parsed_results = []
        for result in results:
            if result:
                try:
                    parsed_results.append(json.loads(result))
                except json.JSONDecodeError:
                    parsed_results.append(None)
            else:
                parsed_results.append(None)
        
        return parsed_results
    except redis.RedisError:
        return [None] * len(keys)

def set_multiple_cached_predictions(predictions: Dict[str, float], expire_time: int = 3600) -> bool:
    """Set multiple cached predictions using Redis pipeline for efficiency"""
    if not predictions:
        return True
    
    try:
        pipe = redis_client.pipeline()
        for key, value in predictions.items():
            pipe.setex(key, expire_time, json.dumps(value))
        pipe.execute()
        return True
    except redis.RedisError:
        return False

def clear_cache_pattern(pattern: str = "*") -> int:
    """Clear cache entries matching pattern (useful for testing/maintenance)"""
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except redis.RedisError:
        return 0

def get_cache_stats() -> Dict[str, Any]:
    """Get Redis cache statistics"""
    try:
        info = redis_client.info()
        return {
            "connected_clients": info.get("connected_clients", 0),
            "used_memory": info.get("used_memory_human", "0B"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "total_commands_processed": info.get("total_commands_processed", 0)
        }
    except redis.RedisError:
        return {"error": "Unable to connect to Redis"}
