from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from app.core.dependencies import get_api_key,get_current_user
from app.services.model_service import predict_assignment_score, predict_batch_assignment_scores

router = APIRouter()

class StudentFeatures(BaseModel):
    comprehension: float = Field(..., ge=0, le=100, description="Comprehension score (0-100)")
    attention: float = Field(..., ge=0, le=100, description="Attention score (0-100)")
    focus: float = Field(..., ge=0, le=100, description="Focus score (0-100)")
    retention: float = Field(..., ge=0, le=100, description="Retention score (0-100)")
    engagement_time: int = Field(..., ge=0, le=300, description="Engagement time in minutes")

class BatchStudentFeatures(BaseModel):
    students: List[StudentFeatures] = Field(..., max_items=100, description="List of students (max 100 for free tier)")
    
    @validator('students')
    def validate_batch_size(cls, v):
        if len(v) == 0:
            raise ValueError("At least one student required")
        if len(v) > 100:
            raise ValueError("Maximum 100 students allowed per batch")
        return v

class StudentPrediction(BaseModel):
    student_index: int
    predicted_score: float
    cached: bool = False

class BatchPredictionResponse(BaseModel):
    predictions: List[StudentPrediction]
    total_processed: int
    cache_hits: int
    processing_time_ms: float

@router.post('/predict')
def predict_assignment_score_endpoint(student: StudentFeatures, user = Depends(get_current_user), _=Depends(get_api_key)):
    """Predict assignment score for a single student"""
    try:
        prediction = predict_assignment_score(student.model_dump())
        return {"predicted_score": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post('/predict/batch', response_model=BatchPredictionResponse)
def predict_batch_assignment_scores_endpoint(
    batch: BatchStudentFeatures, 
    user = Depends(get_current_user), 
    _=Depends(get_api_key)
):
    """Predict assignment scores for multiple students with caching optimization"""
    try:
        result = predict_batch_assignment_scores([s.model_dump() for s in batch.students])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")
