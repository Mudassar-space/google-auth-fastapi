from pydantic import BaseModel, EmailStr

class User(BaseModel):
    email: EmailStr
    name: str
    picture: str
    sub: str  # Google user ID
