from app import schema
import pytest
from jose import jwt
from app.config import settings


def test_create_user(client):
    res = client.post("/users/", json={"email" : "NoobMaster@gmail.com", "password" : "KingKong200"})

    new_user = schema.UserResponse(**res.json())
    assert new_user.email == "NoobMaster@gmail.com"
    assert res.status_code == 201

def test_user_login(client, test_user):
    res = client.post("/login", data= {"username": test_user["email"], "password": test_user["password"]})
    login_res = schema.Token(**res.json())

    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")
    assert id == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 201

@pytest.mark.parametrize("email, password", [
    ("WrongEmail@gmail.com", "WrongPass"),
    ("gglolo@gmail.com", "WrongPass"),
    (None, "Hello202"),                    ## Schemas will give 422 if validation fails
    ("gglolo@gmail.com", None),
    (None, None)
])
def test_incorrect_login(client, email, password):
    res = client.post("/login", data= {"username": email, "password": password})

    assert res.status_code == 403