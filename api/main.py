from fastapi import FastAPI
from auth import router_auth
from prediction import router_prediction

api = FastAPI(
    title="Prédire le temps d’intervention des pompiers de Londres",
    description="A partir de l’année 2022 et pour les 5 prochaines années, un nouveau plan d’action, London Pump.Py est mis en place. L’objectif principal sera d’analyser et prédire le temps d’intervention et de mobilisation de la brigade des pompiers de Londres.",
    version="1.0",
    openapi_tags=[
    {
        'name': 'authentification',
        'description': "Vous retrouverez dans cette partie les différentes routes liés à l'authentification"
    },
    {
        'name': 'prédiction',
        'description': 'Vous retrouverez dans cette partie les différentes routes liés aux prédiction de notre modèle'
    }
]
)

api.include_router(router_auth.router)
api.include_router(router_prediction.router)


@api.get('/', name="Statut de l'API")
def index():
    """Cette route vous permet de savoir si l'api est fonctionnelle
    """
    return { "message": "Bienvenue sur l'api", "statut": "Ready" }