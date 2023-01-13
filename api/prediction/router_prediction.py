from fastapi import Depends, APIRouter, HTTPException, status
from utils.oauth2 import require_user
from .schemas import CreatePredictionSchema, HistorisationSchema
from fastapi.responses import JSONResponse
from .service import predict_time_pumps
from utils.mongodb import Predictions, User
from datetime import datetime
from bson import ObjectId
from auth.serializers import userResponseEntity
from .serializers import predictionResponseEntity

router = APIRouter()

@router.post('/predict/time_pump', name="Prédiction du temps d'intervention", tags=['prédiction'])
def prediction(payload: CreatePredictionSchema = Depends(), user_id: str = Depends(require_user)):
    """Prédiction du temps d'intervention des pompiers sur un incendie dans la ville de Londres
    """
    time, risk_underestimated = predict_time_pumps(payload.dict())
    prediction = {"prediction": time, "risk_underestimated": risk_underestimated, "userId": ObjectId(user_id), "created_at": datetime.utcnow()}
    Predictions.insert_one(prediction)
    time_pump = str(time) + " secondes"

    return JSONResponse(status_code=status.HTTP_200_OK, content={"time_pump": time_pump, "risk_underestimated": risk_underestimated})

@router.get('/historique', name="Récupérer l'historique des prédictions", tags=['prédiction'])
def prediction(payload: HistorisationSchema = Depends(), user_id: str = Depends(require_user)):
    """Récupérer l'historique des prédictions réalisées par les utilisateurs
    """
    if payload.username is not None:
        user = userResponseEntity(User.find_one({ 'username': payload.username }))
        predictions = list(Predictions.find({ 'userId': ObjectId(str(user['id'])) }))
    elif payload.created_at is not None:
        predictions = list(Predictions.find({ 'created_at': payload.created_at }))
    else:
        predictions = list(Predictions.find())
    prediction_array = []
    for prediction in predictions:
        prediction_array.append(predictionResponseEntity(prediction))
    if len(prediction_array) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No predictions found')
    
    return JSONResponse(status_code=status.HTTP_200_OK, content=prediction_array)
