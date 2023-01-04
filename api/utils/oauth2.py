from bson import ObjectId
from fastapi import Depends, HTTPException, status
from auth.serializers import userEntity
from .mongodb import User
from .config import settings
from jose import jwt
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def require_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        user = userEntity(User.find_one({ '_id': ObjectId(str(user_id)) }))

        if not user:
            raise 'UserNotFound'

    except Exception as e:
        error = e.__class__.__name__
        if error == 'JWTError':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='You are not logged in')
        if error == 'UserNotFound':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='User no longer exist')
        if error == 'ExpiredSignatureError':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='Token has expired')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is invalid or has expired')

    return user_id
