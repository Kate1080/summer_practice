from fastapi import Depends, FastAPI, HTTPException, Cookie, Request
from sqlalchemy.orm import Session

from fastapi.security import OAuth2PasswordRequestForm

from fastapi.responses import JSONResponse

from typing import Union

import crud
import models
import schemas
import constant

import uvicorn

from database import engine, connection
# from database import SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
# def get_db():
#     db = connection()
#     try:
#         yield db
#     finally:
#         db.close()

db_session = connection()


@app.post("/sign-up/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate):
    db_user = crud.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(user=user)


@app.post("/sign-in/")
async def auth(user_data: OAuth2PasswordRequestForm = Depends()):
    db_user = crud.get_user_by_email(email=user_data.username)
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not crud.validate_password(password=user_data.password, hashed_password=db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    content = {'message': 'session created'}
    response = JSONResponse(content=content)
    session_id = crud.create_token_for_user(user_id=db_user.id)
    response.set_cookie(key="session_id", value=session_id, httponly=True, secure=True)
    return response


@app.get("/users/", response_model=list[schemas.UserOut])
def read_users(skip: int = 0, limit: int = 100, session_id: Union[str, None] = Cookie(default=None)):
    if session_id is None:
        raise HTTPException(status_code=401, detail="You do not have session id")
    db_user = crud.get_current_user(session_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    users = crud.get_users(skip=skip, limit=limit)
    return users


# @app.get("/users/{user_id}", response_model=schemas.UserOut)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_id(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


@app.post("/article/", response_model=schemas.ArticleOut)
def create_article(article: schemas.ArticleCreate, session_id: Union[str, None] = Cookie(default=None)):
    if session_id is None:
        raise HTTPException(status_code=401, detail="You do not have session id")
    db_author = crud.get_current_user(session_id)
    if db_author is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_author.role == constant.reader:
        raise HTTPException(status_code=403, detail="Permission denied")
    else:
        return crud.create_article(article=article)


@app.post("/article/add/", response_model=schemas.AddAuthorOut)
def add_author(article_id: int, id_user_new: int, session_id: Union[str, None] = Cookie(default=None)):
    if session_id is None:
        raise HTTPException(status_code=401, detail="You do not have session id")
    db_user = crud.get_current_user(session_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role & constant.writer != constant.writer:
        raise HTTPException(status_code=403, detail="Permission denied")
    db_article = crud.get_article_by_id(article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    db_check = crud.check_author_article(article_id=article_id, user_id=db_user.id)
    if db_check is None:
        raise HTTPException(status_code=403, detail="Permission denied")
    db_user_new = crud.get_user_by_id(user_id=id_user_new)
    if db_user_new is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user_new.role & constant.writer != constant.writer:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.add_author(id_user_new=id_user_new, article_id=article_id)


@app.post("/article/publish", response_model=schemas.ArticleOut)
def change_draft_published(article_id: int, session_id: Union[str, None] = Cookie(default=None)):
    if session_id is None:
        raise HTTPException(status_code=401, detail="You do not have session id")
    db_user = crud.get_current_user(session_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role & constant.writer != constant.writer:
        raise HTTPException(status_code=403, detail="Permission denied")
    db_article = crud.get_article_by_id(article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    db_check = crud.check_author_article(article_id=article_id, user_id=db_user.id)
    if db_check is None:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.change_draft_published(article_id=article_id)


@app.post("/article/draft", response_model=schemas.ArticleOut)
def change_approved_draft(article_id: int, session_id: Union[str, None] = Cookie(default=None)):
    if session_id is None:
        raise HTTPException(status_code=401, detail="You do not have session id")
    db_user = crud.get_current_user(session_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_article = crud.get_article_by_id(article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.status != constant.approved:
        raise HTTPException(status_code=404, detail="Permission denied")
    db_check = crud.check_author_article(article_id=article_id, user_id=db_user.id)
    if db_check is None:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.change_approved_draft(article_id=article_id)


@app.post("/article/edit", response_model=schemas.ArticleEditingOut)
def edit_draft(article: schemas.ArticleEditingIn, session_id: Union[str, None] = Cookie(default=None)):
    if session_id is None:
        raise HTTPException(status_code=401, detail="You do not have session id")
    db_user = crud.get_current_user(session_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role & constant.writer != constant.writer:
        raise HTTPException(status_code=403, detail="Permission denied")
    db_article = crud.get_article_by_id(article_id=article.id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.status != constant.draft:
        raise HTTPException(status_code=404, detail="Permission denied")
    db_check = crud.check_author_article(article_id=article.id, user_id=db_user.id)
    if db_check is None:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.edit_draft(article=article)


@app.get("/article/{user_id}", response_model=list[schemas.ArticleReadOut])
def read_status_published(skip: int = 0, limit: int = 100, session_id: Union[str, None] = Cookie(default=None)):
    if session_id is None:
        raise HTTPException(status_code=401, detail="You do not have session id")
    db_user = crud.get_current_user(session_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role & constant.moderator != constant.moderator:
        raise HTTPException(status_code=403, detail="Permission denied")
    articles = crud.get_article_published(skip=skip, limit=limit)
    return articles


@app.post("/article/approve", response_model=schemas.ArticleOut)
def change_published_approved(article_id: int, session_id: Union[str, None] = Cookie(default=None)):
    if session_id is None:
        raise HTTPException(status_code=401, detail="You do not have session id")
    db_user = crud.get_current_user(session_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role & constant.moderator != constant.moderator:
        raise HTTPException(status_code=403, detail="Permission denied")
    db_article = crud.get_article_by_id(article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.status != constant.published:
        raise HTTPException(status_code=404, detail="Permission denied")
    return crud.change_published_approved(article_id=article_id)


@app.post("/article/reject", response_model=schemas.ArticleOut)
def change_published_rejected(article_id: int, session_id: Union[str, None] = Cookie(default=None)):
    if session_id is None:
        raise HTTPException(status_code=401, detail="You do not have session id")
    db_user = crud.get_current_user(session_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role & constant.moderator != constant.moderator:
        raise HTTPException(status_code=403, detail="Permission denied")
    db_article = crud.get_article_by_id(article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.status != constant.published:
        raise HTTPException(status_code=404, detail="Permission denied")
    return crud.change_published_rejected(article_id=article_id)


@app.post("/roles/approve", response_model=schemas.RolesOut)
def approved_change_role(user_id: int, role: int, session_id: Union[str, None] = Cookie(default=None)):
    if session_id is None:
        raise HTTPException(status_code=401, detail="You do not have session id")
    db_user = crud.get_current_user(session_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role & constant.admin != constant.admin:
        raise HTTPException(status_code=403, detail="Permission denied")
    db_user_another = crud.get_user_by_id(user_id=user_id)
    if db_user_another is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.approve_change_role(user_id=user_id, role=role)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

