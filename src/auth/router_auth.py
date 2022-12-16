from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import Body, Depends, HTTPException, APIRouter, Response, status
from .constants import RESPONSES
from .schemas import CreateUserSchema, UserResponse
from fastapi.responses import JSONResponse
from utils.mongodb import User
from utils.bcrypt import hash_password, verify_password
from .serializers import userResponseEntity, userEntity
from utils.config import settings
from utils.oauth2 import AuthJWT, require_user
from fastapi.security import OAuth2PasswordRequestForm
from .service import create_access_token

router = APIRouter()

ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN

@router.post('/login', name="Connexion à l'API", tags=['authentification'], responses=RESPONSES)
def login(payload: OAuth2PasswordRequestForm = Depends()):
    """Authentification à l'api vous permettant de pouvoir utiliser les différentes routes
    """
    user = userEntity(User.find_one({ 'username': payload.username }))
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Incorrect Email or Password')

    if not verify_password(payload.password, user['password']):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Incorrect Email or Password')

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN)
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={'status': 'success', 'access_token': access_token})

@router.post("/register", response_description="Add new user", response_model=UserResponse, tags=['authentification'])
async def create_user(payload: CreateUserSchema):
    user = User.find_one({'username': payload.username})
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Account already exist')
    # Compare password and passwordConfirm
    if payload.password != payload.passwordConfirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')
    #  Hash the password
    payload.password = hash_password(payload.password)
    del payload.passwordConfirm
    payload.created_at = datetime.utcnow()
    new_user = User.insert_one(payload.dict())
    created_user = userResponseEntity(User.find_one({ "_id": new_user.inserted_id }))

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)

@router.get('/me', response_model=UserResponse)
def get_me(user_id: str = Depends(require_user)):
    user = userResponseEntity(User.find_one({'_id': ObjectId(str(user_id))}))
    return {"status": "success", "user": user}