from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.dependencies import get_api_key,get_current_user
from app.services.model_service import predict_assignment_score

router = APIRouter()

class StudentFeatures(BaseModel):
    comprehension : float
    attention: float
    focus : float
    retention : float
    engagement_time : int


@router.post('/predict')
def predict_assignment_score_endpoint(student : StudentFeatures , user = Depends(get_current_user),_=Depends(get_api_key)):
    prediction = predict_assignment_score(student.model_dump())
    return {"predicted_score": prediction}
