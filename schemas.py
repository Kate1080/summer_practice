from pydantic import BaseModel


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


class Article(ArticleBase):
    id: int
    status: str


class Reference(BaseModel):
    id_us: str
    id_art: int

