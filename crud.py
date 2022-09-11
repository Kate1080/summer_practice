import uuid

from sqlalchemy.orm import Session

import models
import schemas
import constant
import main

import hashlib

from datetime import datetime, timedelta
from sqlalchemy import and_


# соль для пароля
# def get_random_string(length=12):
#     return "".join(random.choice(string.ascii_letters) for _ in range(length))


# хэш пароля + соль
def hash_password(password: str):
    salt = ""
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return enc.hex()


# проверка: хэш пароля == хэш из БД
def validate_password(password: str, hashed_password: str):
    password_in = hash_password(password=password)
    return hashed_password == password_in


def get_current_user(session_id):
    current_token = main.db_session.query(models.Token).filter(models.Token.token == session_id).first()
    current_user = main.db_session.query(models.User).filter(models.User.id == current_token.user_id).first()
    return current_user


def get_user_by_email(email: str):
    return main.db_session.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(user_id: int):
    return main.db_session.query(models.User).filter(models.User.id == user_id).first()


def get_users(skip: int = 0, limit: int = 100):
    return main.db_session.query(models.User).offset(skip).limit(limit).all()


def create_user(user: schemas.UserCreate):
    hashed_password = hash_password(password=user.password)
    db_user = models.User(email=user.email, name=user.name, hashed_password=hashed_password, role=constant.reader)
    main.db_session.add(db_user)
    main.db_session.commit()
    # db_token = models.Token(token=str(uuid.uuid4()), expires=datetime.now() + timedelta(weeks=2), user_id=db_user.id)
    # db.add(db_token)
    # db.commit()
    return db_user


def create_token_for_user(user_id: int):
    db_token = models.Token(token=str(uuid.uuid4()), expires=datetime.now() + timedelta(weeks=1), user_id=user_id)
    main.db_session.add(db_token)
    main.db_session.commit()
    return db_token.token


def create_article(article: schemas.ArticleCreate):
    db_article = models.Article(title=article.title, body=article.body, status=constant.draft)
    main.db_session.add(db_article)
    main.db_session.commit()
    db_reference = models.Reference(id_us=article.id, id_art=db_article.id)
    main.db_session.add(db_reference)
    main.db_session.commit()
    return db_article


def get_article_by_id(article_id: int):
    return main.db_session.query(models.Article).filter(models.Article.id == article_id).first()


def check_author_article(article_id: int, user_id: int):
    return main.db_session.query(models.Reference).filter(models.Reference.id_us == user_id, models.Reference.id_art == article_id).first()


def change_draft_published(article_id):
    changed_art = get_article_by_id(article_id=article_id)
    changed_art.status = constant.published
    main.db_session.add(changed_art)
    main.db_session.commit()
    return changed_art


def get_article_published(skip: int = 0, limit: int = 100):
    return main.db_session.query(models.Article).filter(models.Article.status == constant.published).offset(skip).limit(limit).all()


def change_published_approved(article_id):
    changed_art = get_article_by_id(article_id=article_id)
    changed_art.status = constant.approved
    main.db_session.add(changed_art)
    main.db_session.commit()
    return changed_art


def change_approved_draft(article_id):
    changed_art = get_article_by_id(article_id=article_id)
    changed_art.status = constant.draft
    main.db_session.add(changed_art)
    main.db_session.commit()
    return changed_art


def edit_draft(article: schemas.ArticleEditingIn):
    edited_draft = get_article_by_id(article_id=article.id)
    edited_draft.body = article.body
    main.db_session.add(edited_draft)
    main.db_session.commit()
    return edited_draft


def change_published_rejected(article_id):
    changed_art = get_article_by_id(article_id=article_id)
    changed_art.status = constant.rejected
    main.db_session.add(changed_art)
    main.db_session.commit()
    return changed_art


def add_author(id_user_new, article_id):
    db_article_new = models.Reference(id_us=id_user_new, id_art=article_id)
    main.db_session.add(db_article_new)
    main.db_session.commit()
    return db_article_new


def approve_change_role(user_id, role):
    db_user = get_user_by_id(user_id=user_id)
    db_user.role = role
    main.db_session.add(db_user)
    main.db_session.commit()
    return db_user

