import pytest

# Define test functions for each route
# def test_register(test_client, user):
#     response = test_client.post("/register", data=user)
#     assert response.status_code == 201

# def test_login(test_client):
#     response = test_client.post("/login", data={"username": "test", "password": "test-password"})
#     assert response.status_code == 200

def test_get_info_user(test_client, user_authentication_headers):
    response = test_client.get("/me", headers=user_authentication_headers)
    assert response.status_code == 200
