from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    name: str
    password: str

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: int
    name: str
    role: int

    class Config:
        orm_mode = True


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


class ArticleReject(BaseModel):
    comment: str


class AddAuthorOut(BaseModel):
    id_us: int

    class Config:
        orm_mode = True


class RolesOut(BaseModel):
    id: int
    role: int

    class Config:
        orm_mode = True


class BlockedOut(BaseModel):
    id: int
    blocked: str

    class Config:
        orm_mode = True


class CommentIn(BaseModel):
    body: str


class CommentOut(CommentIn):
    id: int
    body: str

    class Config:
        orm_mode = True


class ArticleRatingOut(BaseModel):
    id: int
    rating: int

    class Config:
        orm_mode = True


class NewArticleOut(BaseModel):
    title: str
    body: str

    class Config:
        orm_mode = True

