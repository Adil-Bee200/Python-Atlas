
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from typing import Annotated
from pydantic import BaseModel, Field


class User(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    email: EmailStr
    id: int
    created_at: datetime

class Token(BaseModel):
    access_token : str
    token_type : str


class TokenData(BaseModel):
    id : Optional[str] = None


class Post(BaseModel):
    title: str
    content: str 
    published: bool = True 

class PostReturn(Post):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponse

    class Config:
        orm_mode = True

class PostWithVotes(BaseModel):
    post: PostReturn
    votes: int

    class Config:
        orm_mode = True

class Vote(BaseModel):
    post_id: int
    dir: Annotated[int, Field(strict=True, ge=0, le=1)]