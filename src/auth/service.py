import json
from fastapi import Depends, HTTPException, status
from .constants import OAUTH2_SCHEMA

def fake_decode_token(token):
    identifiants = open('./public/identifiants.json')
    data = json.load(identifiants)
    limited_list = [element for element in data if element['username'] == token]

    return limited_list

async def get_current_user(token: str = Depends(OAUTH2_SCHEMA)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user[0]
