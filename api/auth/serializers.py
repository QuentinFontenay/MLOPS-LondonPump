def userEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "password": user["password"],
        "created_at": user["created_at"],
    }

def userResponseEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": str(user["username"]),
        "created_at": str(user["created_at"]),
    }
