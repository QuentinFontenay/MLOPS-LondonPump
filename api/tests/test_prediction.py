import pytest

# Define test functions for each route
def test_prediction(test_client, prediction, user_authentication_headers):
    response = test_client.post("/predict/time_pump", data=prediction, headers=user_authentication_headers)
    assert response.status_code == 200

def test_historique_prediction(test_client, user_authentication_headers):
    response = test_client.get(f"/historique?username=test", headers=user_authentication_headers)
    assert response.status_code == 200

def test_historique_prediction_with_user_not_exist(test_client, user_authentication_headers):
    response = test_client.get(f"/historique?username=test2", headers=user_authentication_headers)
    assert response.status_code == 404
