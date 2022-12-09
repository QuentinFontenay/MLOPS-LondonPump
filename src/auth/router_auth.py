import json
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from .constants import RESPONSES

router = APIRouter()

@router.post('/token', name="Connexion à l'API", tags=['authentification'], responses=RESPONSES)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authentification à l'api vous permettant de pouvoir utiliser les différentes routes
    """
    identifiants = open('./public/identifiants.json')
    data = json.load(identifiants)
    limited_list = [element for element in data if element['username'] == form_data.username and element['password'] == form_data.password]
    if not limited_list:
        raise HTTPException(status_code=400, detail="Identifiants incorrect")
    
    return { "access_token": limited_list[0]['username'], "token_type": "bearer" }
