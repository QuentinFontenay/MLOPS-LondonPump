from fastapi import Depends, APIRouter, HTTPException, status
import pymongo
from utils.oauth2 import require_user
from .schemas import CreatePredictionSchema, HistorisationSchema
from fastapi.responses import JSONResponse
from .service import predict_time_pumps
from utils.mongodb import connect_to_mongo
from datetime import datetime
from bson import ObjectId
from auth.serializers import userResponseEntity
from .serializers import predictionResponseEntity

router = APIRouter()
db = connect_to_mongo()

@router.post('/predict/time_pump', name="Prédiction du temps d'intervention", tags=['prédiction'])
def prediction(payload: CreatePredictionSchema = Depends(), user_id: str = Depends(require_user)):
    """Prédiction du temps d'intervention des pompiers sur un incendie dans la ville de Londres
    """
    risk_stations = db.riskStations.find({}, { "stations": 1, "_id": 1 }).sort("created_at", pymongo.DESCENDING).limit(1)
    risk_stations = list(risk_stations)
    time, risk_underestimated = predict_time_pumps(payload.dict(), risk_stations)
    if time is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Error while predicting time pump')
    prediction = {"prediction": time, "risk_underestimated": risk_underestimated, "userId": ObjectId(user_id), "created_at": datetime.utcnow(), "stationId": ObjectId(risk_stations[0]['_id'])}
    db.predictions.insert_one(prediction)
    time_pump = str(time) + " secondes"

    return JSONResponse(status_code=status.HTTP_200_OK, content={"time_pump": time_pump, "risk_underestimated": risk_underestimated})

@router.get('/historique', name="Récupérer l'historique des prédictions", tags=['prédiction'])
def prediction_historique(payload: HistorisationSchema = Depends(), user_id: str = Depends(require_user)):
    """Récupérer l'historique des prédictions réalisées par les utilisateurs
    """
    query = {}
    if payload.username is not None:
        user = db.users.find_one({ 'username': payload.username })
        if user is not None:
            user = userResponseEntity(user)
            query.update({ 'userId': ObjectId(str(user['id'])) })
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No user found')
    if payload.created_at is not None:
        query.update({ 'created_at': payload.created_at })
    if payload.risk is not None:
        query.update({ 'risk_underestimated': payload.risk })

    predictions = list(db.predictions.find(query))
    prediction_array = []
    for prediction in predictions:
        prediction_array.append(predictionResponseEntity(prediction))
    if len(prediction_array) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No predictions found')
    
    return JSONResponse(status_code=status.HTTP_200_OK, content=prediction_array)
