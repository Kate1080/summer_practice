from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import crud
import models
import schemas

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


@app.post("/article/", response_model=schemas.Article)
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    db_author = crud.get_user_by_login(db, login=article.login)
    if db_author is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_author.role == 10001:
        raise HTTPException(status_code=403, detail="Permission denied")
    else:
        return crud.create_article(db=db, article=article)


@app.post("/article/draft/{article_id}/{user_login}", response_model=schemas.Article)
def change_draft_published(article_id: int, user_login: str,  db: Session = Depends(get_db)):
    db_article = crud.get_article_by_id(db, article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    db_user = crud.get_user_by_login(db, login=user_login)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role == 10001:
        raise HTTPException(status_code=403, detail="Permission denied")
    db_check = crud.check_author_article(db, article_id=article_id, user_login=user_login)
    if db_check is None:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.change_draft_published(db, article_id=article_id)


@app.post("/article/published/{us_login}/{art_id}", response_model=schemas.Article)
def change_published_approved(us_login: str,  art_id: int, db: Session = Depends(get_db)):
    db_article = crud.get_article_by_id(db, article_id=art_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    db_user = crud.get_user_by_login(db, login=us_login)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role == 10001 or 10011:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.change_published_approved(db, art_id=art_id)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
