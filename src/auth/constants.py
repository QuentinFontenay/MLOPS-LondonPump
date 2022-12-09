from fastapi.security import OAuth2PasswordBearer

OAUTH2_SCHEMA = OAuth2PasswordBearer(tokenUrl="token")

RESPONSES = {
    200: {"description": "Vous êtes connectés"},
    400: {"description": "Identifiants incorrect"},
    422: {"description": "L'un des paramètres de la requete est incorrect"},
}
