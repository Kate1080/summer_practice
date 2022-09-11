from pydantic import UUID4, BaseModel, EmailStr, Field, validator
from typing import Optional
import datetime


class UserBase(BaseModel):
    email: EmailStr


#Sign-Up запрос
class UserCreate(UserBase):
    name: str
    password: str

    class Config:
        orm_mode = True


#Тело ответа
class UserOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


# class TokenBase(BaseModel):
#     token: UUID4 = Field(..., alias="access_token")
#     expires: datetime
#     token_type: Optional[str] = "bearer"
#
#     class Config:
#         allow_population_by_field_name = True


class ArticleBase(BaseModel):
    id: int


class ArticleCreate(BaseModel):
    title: str
    body: str

    class Config:
        orm_mode = True


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
    id: int
    body: str

    class Config:
        orm_mode = True


class ArticleEditingOut(BaseModel):
    title: str
    status: str

    class Config:
        orm_mode = True


# class AddAuthorIn(BaseModel):
#     id_user: int
#     id_user_new: int
#     article_id: int
#
#     class Config:
#         orm_mode = True


class AddAuthorOut(BaseModel):
    id_us: int

    class Config:
        orm_mode = True


# class Reference(BaseModel):
#     id_us: str
#     id_art: int
#


class RolesOut(BaseModel):
    name: str
    role: int

    class Config:
        orm_mode = True






