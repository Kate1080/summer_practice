from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import crud
import models
import schemas
import constant

import uvicorn

from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user_s = crud.get_user_by_login(db, login=user.login)
    if db_user_s:
        raise HTTPException(status_code=400, detail="id already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_login}", response_model=schemas.User)
def read_user(user_login: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_login=user_login)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/article/", response_model=schemas.ArticleOut)
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    db_author = crud.get_user_by_login(db, login=article.login)
    if db_author is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_author.role == constant.reader:
        raise HTTPException(status_code=403, detail="Permission denied")
    else:
        return crud.create_article(db=db, article=article)


@app.post("/article/add/", response_model=schemas.AddAuthorOut)
def add_author(reference: schemas.AddAuthorIn, db: Session = Depends(get_db)):
    db_article = crud.get_article_by_id(db, article_id=reference.article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    db_user = crud.get_user_by_login(db, login=reference.id_user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role & constant.writer != constant.writer:
        raise HTTPException(status_code=403, detail="Permission denied")
    db_check = crud.check_author_article(db, article_id=reference.article_id, user_login=reference.id_user)
    if db_check is None:
        raise HTTPException(status_code=403, detail="Permission denied")
    db_user_new = crud.get_user_by_login(db, login=reference.id_user_new)
    if db_user_new is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user_new.role & constant.writer != constant.writer:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.add_author(db, reference=reference)


@app.post("/article/draft/{article_id}/{user_login}", response_model=schemas.ArticleOut)
def change_draft_published(article_id: int, user_login: str,  db: Session = Depends(get_db)):
    db_article = crud.get_article_by_id(db, article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    db_user = crud.get_user_by_login(db, login=user_login)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role & constant.writer != constant.writer:
        raise HTTPException(status_code=403, detail="Permission denied")
    db_check = crud.check_author_article(db, article_id=article_id, user_login=user_login)
    if db_check is None:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.change_draft_published(db, article_id=article_id)


@app.post("/article/approved/{article_id}/{user_id}", response_model=schemas.ArticleOut)
def change_approved_draft(article_id: int, user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_login(db, login=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_article = crud.get_article_by_id(db, article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.status != "Approved":
        raise HTTPException(status_code=404, detail="Permission denied")
    db_check = crud.check_author_article(db, article_id=article_id, user_login=user_id)
    if db_check is None:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.change_approved_draft(db, article_id=article_id)


@app.post("/article/edit/{article_id}/{user_id}", response_model=schemas.ArticleEditingOut)
def edit_draft(article_id: int, user_id: str, article: schemas.ArticleEditingIn, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_login(db, login=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_article = crud.get_article_by_id(db, article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.status != "Draft":
        raise HTTPException(status_code=404, detail="Permission denied")
    db_check = crud.check_author_article(db, article_id=article_id, user_login=user_id)
    if db_check is None:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.edit_draft(db, article_id=article_id, article=article)


@app.get("/article/{user_id}", response_model=list[schemas.ArticleReadOut])
def read_by_status(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_login(db, login=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role & constant.moderator != constant.moderator:
        raise HTTPException(status_code=403, detail="Permission denied")
    articles = crud.get_article_by_status(db, status="Published", skip=skip, limit=limit)
    return articles


@app.post("/article/published/{article_id}/{user_id}", response_model=schemas.ArticleOut)
def change_published_approved(article_id: int,  user_id: str, db: Session = Depends(get_db)):
    db_article = crud.get_article_by_id(db, article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    db_user = crud.get_user_by_login(db, login=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role & constant.moderator != constant.moderator:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.change_published_approved(db, art_id=article_id)


@app.post("/article/denied/{article_id}/{user_id}", response_model=schemas.ArticleOut)
def change_published_denied(article_id: int , user_id: str, db: Session = Depends(get_db)):
    db_article = crud.get_article_by_id(db, article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    db_user = crud.get_user_by_login(db, login=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role & constant.moderator != constant.moderator:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.change_published_denied(db, article_id=article_id)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

