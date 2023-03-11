import pytest
import json
# Define test functions for each route
def test_register(test_client, user):
    test_client.headers["Content-Type"] = "application/json"
    response = test_client.post("/register", data=json.dumps(user))
    assert response.status_code == 201

def test_register_with_password_confirm_different(test_client):
    test_client.headers["Content-Type"] = "application/json"
    response = test_client.post("/register", data=json.dumps({"username": "test", "password": "test-password", "passwordConfirm": "test-password2"}))
    assert response.status_code == 400

def test_register_account_exist(test_client):
    test_client.headers["Content-Type"] = "application/json"
    response = test_client.post("/register", data=json.dumps({"username": "test", "password": "test-password", "passwordConfirm": "test-password"}))
    assert response.status_code == 409

def test_login(test_client):
    test_client.headers["Content-Type"] = "application/x-www-form-urlencoded"
    response = test_client.post("/login", data="username=test&password=test-password")
    assert response.status_code == 200

def test_login_incorrect(test_client):
    test_client.headers["Content-Type"] = "application/x-www-form-urlencoded"
    response = test_client.post("/login", data="username=test2&password=test-password")
    assert response.status_code == 400

def test_get_info_user(test_client, user_authentication_headers):
    response = test_client.get("/me", headers=user_authentication_headers)
    assert response.status_code == 200
