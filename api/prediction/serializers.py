def predictionEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "userId": str(user["userId"]),
        "prediction": user["prediction"],
        "risk_underestimated": user["risk_underestimated"],
        "created_at": user["created_at"],
    }

def predictionResponseEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "userId": str(user["userId"]),
        "prediction": user["prediction"],
        "risk_underestimated": user["risk_underestimated"],
        "created_at": str(user["created_at"]),
    }
