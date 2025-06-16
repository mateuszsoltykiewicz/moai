from pydantic import BaseModel, Field, EmailStr, List
from typing import Optional
from datetime import datetime


class PostBase(BaseModel):
    title: str = Field(..., max_length=100)
    content: str = Field(..., description="Post content")

class UserWithPostsSchema(UserSchema):
    posts: List[PostBase] = Field(default_factory=list, description="List of user's posts")

class UserSchema(BaseModel):
    id: Optional[int] = Field(None, description="User ID (auto-generated)")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., max_length=120, description="User email address")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 42,
                    "username": "alice",
                    "email": "alice@example.com",
                    "created_at": "2025-06-11T17:00:00Z"
                }
            ]
        }
    }

class UserCreateSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=120)
    password: str = Field(..., min_length=8)