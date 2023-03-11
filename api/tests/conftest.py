import pytest
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.mongodb import connect_to_mongo

@pytest.fixture(scope="session")
def user():
    return {
        "username": "test",
        "password": "test-password",
        "passwordConfirm": "test-password",
    }

@pytest.fixture(scope="session")
def prediction():
    return {
        "DeployedFromLocation": "Home Station",
        "Appliance": "Pump Ladder",
        "PropertyCategory": "Other Residential",
        "AddressQualifier": "Correct incident location",
        "IncidentType": "Fire",
        "Distance": 0.608,
        "TotalOfPumpInLondon_Out": 3,
        "Station_Code_of_ressource": "G30",
        "IncidentStationGround_Code": "G30",
        "PumpAvailable": "2",
        "month": 1,
        "temp": 2.6,
        "precip": 0.0,
        "cloudcover": 0.0,
        "visibility": 28.3,
        "conditions": "Clear",
        "workingday": 1,
        "school_holidays": 0,
        "congestion_rate": 0.04,
    }

@pytest.fixture(scope="session")
def historique_prediction():
    return {
        "username": "test",
    }

@pytest.fixture(scope="session", autouse=True)
def test_client(user, prediction, historique_prediction):
    import main
    application = main.api
    with TestClient(application) as test_client:
        yield test_client
    db = connect_to_mongo()
    db.users.delete_one({"username": user["username"]})
    db.predictions.delete_one({"userId": prediction["userId"]})

@pytest.fixture(scope="session")
def user_authentication_headers(test_client, user):
    data = {"username": user['username'], "password": user['password']}
    r = test_client.post("/login", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    return headers
