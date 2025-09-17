import json 
import redis
from redis import StrictRedis
from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Redis connection configuration
REDIS_CONFIG = {
    'socket_timeout': 10,
    'socket_connect_timeout': 10,
    'socket_keepalive': True,
    'socket_keepalive_options': {},
    'connection_pool_kwargs': {
        'max_connections': 50,
        'retry_on_timeout': True,
    },
    'health_check_interval': 30,
    'decode_responses': True,
    'encoding': 'utf-8',
    'encoding_errors': 'strict'
}

# Initialize Redis client with StrictRedis and improved configuration
redis_client = None
connection_pool = None

def initialize_redis_connection():
    """Initialize Redis connection with StrictRedis and connection pooling"""
    global redis_client, connection_pool
    
    try:
        # Create connection pool for better connection management
        connection_pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            **REDIS_CONFIG['connection_pool_kwargs'],
            socket_timeout=REDIS_CONFIG['socket_timeout'],
            socket_connect_timeout=REDIS_CONFIG['socket_connect_timeout'],
            socket_keepalive=REDIS_CONFIG['socket_keepalive'],
            socket_keepalive_options=REDIS_CONFIG['socket_keepalive_options'],
            health_check_interval=REDIS_CONFIG['health_check_interval'],
            decode_responses=REDIS_CONFIG['decode_responses'],
            encoding=REDIS_CONFIG['encoding'],
            encoding_errors=REDIS_CONFIG['encoding_errors']
        )
        
        # Initialize StrictRedis client with connection pool
        redis_client = StrictRedis(
            connection_pool=connection_pool,
            socket_timeout=REDIS_CONFIG['socket_timeout'],
            socket_connect_timeout=REDIS_CONFIG['socket_connect_timeout']
        )
        
        # Test connection with ping
        redis_client.ping()
        logger.info("Redis connection established successfully")
        return True
        
    except redis.ConnectionError as e:
        logger.error(f"Redis connection failed: {e}")
        redis_client = None
        connection_pool = None
        return False
    except redis.RedisError as e:
        logger.error(f"Redis error during initialization: {e}")
        redis_client = None
        connection_pool = None
        return False
    except Exception as e:
        logger.error(f"Unexpected error during Redis initialization: {e}")
        redis_client = None
        connection_pool = None
        return False

def ensure_redis_connection():
    """Ensure Redis connection is active, reconnect if necessary"""
    global redis_client
    
    if redis_client is None:
        return initialize_redis_connection()
    
    try:
        redis_client.ping()
        return True
    except (redis.ConnectionError, redis.TimeoutError):
        logger.warning("Redis connection lost, attempting to reconnect...")
        return initialize_redis_connection()
    except redis.RedisError as e:
        logger.error(f"Redis error during connection check: {e}")
        return False

# Initialize connection on module load
initialize_redis_connection()

def get_cached_prediction(key: str) -> Optional[Any]:
    """Get single cached prediction with connection retry - supports any JSON serializable type"""
    if not ensure_redis_connection():
        return None
    
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except (redis.RedisError, json.JSONDecodeError) as e:
        logger.warning(f"Error getting cached prediction for key {key}: {e}")
        return None

def set_cached_prediction(key: str, value: Any, expire_time: int = 300) -> bool:
    """Set single cached prediction with expiration and connection retry - supports any JSON serializable type"""
    if not ensure_redis_connection():
        return False
    
    try:
        redis_client.setex(key, expire_time, json.dumps(value))
        return True
    except (redis.RedisError, TypeError) as e:
        logger.warning(f"Error setting cached prediction for key {key}: {e}")
        return False

def get_multiple_cached_predictions(keys: List[str]) -> List[Optional[Any]]:
    """Get multiple cached predictions using Redis pipeline with connection retry - supports any JSON serializable type"""
    if not keys:
        return []
    
    if not ensure_redis_connection():
        return [None] * len(keys)
    
    try:
        # Use StrictRedis pipeline with transaction support
        pipe = redis_client.pipeline(transaction=True)
        for key in keys:
            pipe.get(key)
        results = pipe.execute()
        
        parsed_results = []
        for i, result in enumerate(results):
            if result:
                try:
                    parsed_results.append(json.loads(result))
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON decode error for key {keys[i]}: {e}")
                    parsed_results.append(None)
            else:
                parsed_results.append(None)
        
        return parsed_results
    except redis.RedisError as e:
        logger.warning(f"Error getting multiple cached predictions: {e}")
        return [None] * len(keys)

def set_multiple_cached_predictions(predictions: Dict[str, Any], expire_time: int = 3600) -> bool:
    """Set multiple cached predictions using Redis pipeline with connection retry - supports any JSON serializable type"""
    if not predictions:
        return True
    
    if not ensure_redis_connection():
        return False
    
    try:
        # Use StrictRedis pipeline with transaction support
        pipe = redis_client.pipeline(transaction=True)
        for key, value in predictions.items():
            pipe.setex(key, expire_time, json.dumps(value))
        pipe.execute()
        return True
    except (redis.RedisError, TypeError) as e:
        logger.warning(f"Error setting multiple cached predictions: {e}")
        return False

def clear_cache_pattern(pattern: str = "*") -> int:
    """Clear cache entries matching pattern with connection retry"""
    if not ensure_redis_connection():
        return 0
    
    try:
        # Use SCAN instead of KEYS for better performance
        cursor = 0
        deleted_count = 0
        
        while True:
            cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                deleted_count += redis_client.delete(*keys)
            if cursor == 0:
                break
                
        return deleted_count
    except redis.RedisError as e:
        logger.warning(f"Error clearing cache pattern {pattern}: {e}")
        return 0

def get_cache_stats() -> Dict[str, Any]:
    """Get Redis cache statistics with connection retry"""
    if not ensure_redis_connection():
        return {"error": "Unable to connect to Redis", "connected": False}
    
    try:
        info = redis_client.info()
        return {
            "connected": True,
            "connected_clients": info.get("connected_clients", 0),
            "used_memory": info.get("used_memory_human", "0B"),
            "used_memory_bytes": info.get("used_memory", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "total_commands_processed": info.get("total_commands_processed", 0),
            "redis_version": info.get("redis_version", "unknown"),
            "uptime_in_seconds": info.get("uptime_in_seconds", 0),
            "hit_rate": _calculate_hit_rate(info.get("keyspace_hits", 0), info.get("keyspace_misses", 0))
        }
    except redis.RedisError as e:
        logger.warning(f"Error getting cache stats: {e}")
        return {"error": f"Redis error: {str(e)}", "connected": False}

def _calculate_hit_rate(hits: int, misses: int) -> float:
    """Calculate cache hit rate percentage"""
    total = hits + misses
    if total == 0:
        return 0.0
    return round((hits / total) * 100, 2)

def get_connection_info() -> Dict[str, Any]:
    """Get Redis connection information"""
    return {
        "redis_url": settings.REDIS_URL,
        "connection_pool_active": connection_pool is not None,
        "redis_client_active": redis_client is not None,
        "config": REDIS_CONFIG
    }

def test_redis_connection() -> Dict[str, Any]:
    """Test Redis connection and return detailed status"""
    try:
        if not ensure_redis_connection():
            return {"status": "failed", "error": "Could not establish connection"}
        
        # Test basic operations
        test_key = "test:connection:ping"
        test_value = "pong"
        
        # Test SET
        redis_client.setex(test_key, 10, test_value)
        
        # Test GET
        retrieved_value = redis_client.get(test_key)
        
        # Test DELETE
        redis_client.delete(test_key)
        
        if retrieved_value == test_value:
            return {
                "status": "success", 
                "message": "Redis connection test passed",
                "operations_tested": ["ping", "set", "get", "delete"]
            }
        else:
            return {
                "status": "failed", 
                "error": "Value mismatch in test operation"
            }
            
    except Exception as e:
        return {
            "status": "failed", 
            "error": f"Connection test failed: {str(e)}"
        }
