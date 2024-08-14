from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str
    email: str

class UserInDB(BaseModel):
    username: str
    email: str
    hashed_password: str

class BlogModel(BaseModel):
    title: str
    sub_title: str
    content: str
    author: str
    tags: List[str]

class UpdateBlogModel(BaseModel):
    title: Optional[str] = None
    sub_title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None

class CommentModel(BaseModel):
    post_id: str
    content: str
    author: str

class UpdateCommentModel(BaseModel):
    content: Optional[str] = None
    author: Optional[str] = None
