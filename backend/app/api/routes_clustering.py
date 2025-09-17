from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List
from app.core.dependencies import get_api_key, get_current_user
from app.services.clustering_service import predict_batch_student_clusters

router = APIRouter()

class StudentFeaturesForClustering(BaseModel):
    comprehension: float = Field(..., ge=0, le=100, description="Comprehension score (0-100)")
    attention: float = Field(..., ge=0, le=100, description="Attention score (0-100)")
    focus: float = Field(..., ge=0, le=100, description="Focus score (0-100)")
    retention: float = Field(..., ge=0, le=100, description="Retention score (0-100)")
    engagement_time: int = Field(..., ge=0, le=300, description="Engagement time in minutes")

class BatchStudentFeaturesForClustering(BaseModel):
    students: List[StudentFeaturesForClustering] = Field(..., max_items=100, description="List of students (max 100 for free tier)")
    
    @validator('students')
    def validate_batch_size(cls, v):
        if len(v) == 0:
            raise ValueError("At least one student required")
        if len(v) > 100:
            raise ValueError("Maximum 100 students allowed per batch")
        return v

class StudentClusterPrediction(BaseModel):
    student_index: int
    cluster_label: int
    persona_name: str
    confidence: str
    cached: bool = False

class BatchClusterPredictionResponse(BaseModel):
    predictions: List[StudentClusterPrediction]
    total_processed: int
    cache_hits: int
    processing_time_ms: float
    available_personas: List[str]

@router.post('/cluster/batch', response_model=BatchClusterPredictionResponse)
def predict_batch_student_clusters_endpoint(
    batch: BatchStudentFeaturesForClustering, 
    user = Depends(get_current_user), 
    _=Depends(get_api_key)
):
    """Predict student clusters/personas for multiple students with caching optimization"""
    try:
        result = predict_batch_student_clusters([s.model_dump() for s in batch.students])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch clustering prediction failed: {str(e)}")

@router.get('/personas')
def get_available_personas(user = Depends(get_current_user), _=Depends(get_api_key)):
    """Get list of available student personas from clustering model"""
    from app.services.clustering_service import PERSONA_MAPPING
    return {
        "personas": list(PERSONA_MAPPING.values()),
        "cluster_mapping": PERSONA_MAPPING,
        "total_clusters": len(PERSONA_MAPPING)
    }
