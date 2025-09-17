from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.cache.redis_cache import get_cache_stats, clear_cache_pattern

router = APIRouter()

@router.get('/cache/stats')
def get_cache_statistics(user = Depends(get_current_user)):
    """Get Redis cache performance statistics"""
    return get_cache_stats()

@router.delete('/cache/clear')
def clear_cache(pattern: str = "*", user = Depends(get_current_user)):
    """Clear cache entries (use with caution in production)"""
    cleared_count = clear_cache_pattern(pattern)
    return {"message": f"Cleared {cleared_count} cache entries", "pattern": pattern}
