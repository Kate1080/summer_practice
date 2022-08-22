import uuid

from sqlalchemy.orm import Session

import models
import schemas


def get_user(db: Session, user_login: str):
    return db.query(models.User).filter(models.User.login == user_login).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_login(db: Session, login: str):
    return db.query(models.User).filter(models.User.login == login).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password
    db_user = models.User(login=user.login, email=user.email, name=user.name, hashed_password=fake_hashed_password, role=10011)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_article(db: Session, article: schemas.ArticleCreate):
    db_article = models.Article(title=article.title, body=article.body, status="Draft")
    db.add(db_article)
    db.commit()
    db_reference = models.Reference(id_us=article.login, id_art=db_article.id, id=str(uuid.uuid4()))
    db.add(db_reference)
    db.commit()
    return db_article


def get_article_by_id(db: Session, article_id: int):
    return db.query(models.Article).filter(models.Article.id == article_id).first()


def check_author_article(db: Session, article_id: int, user_login: str):
    return db.query(models.Reference).filter(models.Reference.id_us == user_login, models.Reference.id_art == article_id).first()


def change_draft_published(db: Session, article_id):
    changed_art = get_article_by_id(db, article_id=article_id)
    changed_art.status = "Published"
    db.add(changed_art)
    db.commit()
    return changed_art


def change_published_approved(db: Session, art_id):
    changed_art = get_article_by_id(db, article_id=art_id)
    changed_art.status = "Approved"
    db.add(changed_art)
    db.commit()
    return changed_art
