from pydantic import BaseModel, field_validator

class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def valid_email(cls, v):
        v = v.strip().lower()
        if "@" not in v:
            raise ValueError("Invalid email")
        return v

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    model_config = {"from_attributes": True}

class LoginResponse(BaseModel):
    token: str
    user: UserOut
