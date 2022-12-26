from fastapi import Depends, APIRouter, status
from utils.oauth2 import require_user
from .schemas import CreatePredictionSchema
from fastapi.responses import JSONResponse
from .service import predict_time_pumps

router = APIRouter()

@router.post('/predict/time_pump', name="Prédiction du temps d'intervention", tags=['prediction'])
def prediction(payload: CreatePredictionSchema = Depends(), user_id: str = Depends(require_user)):
    """Prédiction du temps d'intervention des pompiers sur un incendie dans la ville de Londres
    """
    print(payload.dict())
    time = predict_time_pumps(payload.dict())
    
    return JSONResponse(status_code=status.HTTP_200_OK)
