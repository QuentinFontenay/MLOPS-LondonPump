from pydantic import BaseModel, Field, constr
from bson import ObjectId
# from utils.mongodb import PyObjectId
from datetime import datetime

class UserModelSchema(BaseModel):
    # id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str = Field(...)
    created_at: datetime = Field(...)

    class Config:
        orm_mode = True
        # allow_population_by_field_name = True
        # arbitrary_types_allowed = True
        # json_encoders = {ObjectId: str}
        # schema_extra = {
        #     "example": {
        #         "username": "Jane",
        #         "password": "toto",
        #     }
        # }

class CreateUserSchema(UserModelSchema):
    password: constr(min_length=6) = Field(...)
    passwordConfirm: str = Field(...)

class UserResponseSchema(UserModelSchema):
    id: str
    pass

class UserResponse(BaseModel):
    status: str
    user: UserResponseSchema