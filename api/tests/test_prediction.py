import pytest

# Define test functions for each route
def test_prediction(test_client, prediction, user_authentication_headers):
    response = test_client.post("/predict/time_pump", data=prediction, headers=user_authentication_headers)
    assert response.status_code == 200
