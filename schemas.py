from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    name: str
    login: str


class User(UserBase):
    login: str

    class Config:
        orm_mode = True


class ArticleBase(BaseModel):
    login: str


class ArticleCreate(ArticleBase):
    title: str
    body: str


class ArticleOut(BaseModel):
    title: str
    status: str

    class Config:
        orm_mode = True


class ArticleReadOut(BaseModel):
    title: str
    body: str
    status: str

    class Config:
        orm_mode = True


class ArticleEditingIn(BaseModel):
    body: str

    class Config:
        orm_mode = True


class ArticleEditingOut(BaseModel):
    title: str
    status: str

    class Config:
        orm_mode = True


class AddAuthorIn(BaseModel):
    id_user: str
    id_user_new: str
    article_id: int

    class Config:
        orm_mode = True


class AddAuthorOut(BaseModel):
    id_us: str

    class Config:
        orm_mode = True


class Reference(BaseModel):
    id_us: str
    id_art: int


