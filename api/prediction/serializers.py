def predictionEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "prediction": user["prediction"],
        "created_at": user["created_at"],
    }

def predictionResponseEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "prediction": user["prediction"],
        "created_at": str(user["created_at"]),
    }
