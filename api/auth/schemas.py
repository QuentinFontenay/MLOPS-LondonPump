from pydantic import BaseModel, Field, constr
from datetime import datetime

class UserModelSchema(BaseModel):
    username: str
    created_at: datetime = datetime.now()

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
    password: constr(min_length=6)
    passwordConfirm: str

class UserResponseSchema(UserModelSchema):
    id: str
    pass

class UserResponse(BaseModel):
    status: str
    user: UserResponseSchema
