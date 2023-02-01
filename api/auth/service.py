from datetime import timedelta, datetime
from typing import Union
from jose import jwt
from dotenv import load_dotenv
import os

load_dotenv()

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv('JWT_SECRET_KEY'), algorithm=os.getenv('JWT_ALGORITHM'))

    return encoded_jwt, expire.strftime("%d/%m/%Y, %H:%M:%S")
