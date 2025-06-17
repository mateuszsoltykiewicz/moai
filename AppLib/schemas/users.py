from pydantic import BaseModel, Field, EmailStr, SecretStr
from typing import Optional, List
from datetime import datetime

class PostBase(BaseModel):
    title: str = Field(..., max_length=100, description="Title of the post")
    content: str = Field(..., description="Post content")

    class Config:
        schema_extra = {
            "example": {
                "title": "My First Post",
                "content": "This is the content of my first post."
            }
        }

class UserSchema(BaseModel):
    id: Optional[int] = Field(None, description="User ID (auto-generated)")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., max_length=120, description="User email address")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")

    class Config:
        schema_extra = {
            "example": {
                "id": 42,
                "username": "alice",
                "email": "alice@example.com",
                "created_at": "2025-06-11T17:00:00Z"
            }
        }

class UserWithPostsSchema(UserSchema):
    posts: List[PostBase] = Field(default_factory=list, description="List of user's posts")

    class Config:
        schema_extra = {
            "example": {
                "id": 42,
                "username": "alice",
                "email": "alice@example.com",
                "created_at": "2025-06-11T17:00:00Z",
                "posts": [
                    {
                        "title": "My First Post",
                        "content": "This is the content of my first post."
                    }
                ]
            }
        }

class UserCreateSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., max_length=120, description="User email address")
    password: SecretStr = Field(..., min_length=8, description="User password (min 8 characters)")

    class Config:
        schema_extra = {
            "example": {
                "username": "bob",
                "email": "bob@example.com",
                "password": "supersecret123"
            }
        }
