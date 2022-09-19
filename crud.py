import uuid

import models
import schemas
import constant
import main

import hashlib

from datetime import datetime, timedelta


# Хэширование пароля:
def hash_password(password: str):
    salt = ""
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return enc.hex()


# Проверка пароля:
def validate_password(password: str, hashed_password: str):
    password_in = hash_password(password=password)
    return hashed_password == password_in


# Получение данных пользователя через токен:
def get_current_user(session_id):
    current_token = main.db_session.query(models.Token).filter(models.Token.token == session_id).first()
    current_user = main.db_session.query(models.User).filter(models.User.id == current_token.user_id).first()
    return current_user


# Получение данных пользователя по его почте:
def get_user_by_email(email: str):
    return main.db_session.query(models.User).filter(models.User.email == email).first()


# Получение данных пользователя по его id:
def get_user_by_id(user_id: int):
    return main.db_session.query(models.User).filter(models.User.id == user_id).first()


# def get_users(skip: int = 0, limit: int = 100):
#     return main.db_session.query(models.User).offset(skip).limit(limit).all()


# Добавление в бд нового пользователя:
def create_user(user: schemas.UserCreate):
    hashed_password = hash_password(password=user.password)
    db_user = models.User(email=user.email, name=user.name, hashed_password=hashed_password, role=constant.reader)
    main.db_session.add(db_user)
    main.db_session.commit()
    return db_user


# Создание сессии для авторизированного пользователя:
def create_token_for_user(user_id: int):
    db_token = models.Token(token=str(uuid.uuid4()), expires=datetime.now() + timedelta(weeks=1), user_id=user_id)
    main.db_session.add(db_token)
    main.db_session.commit()
    return db_token.token


# Добавление в бд новой статьи:
def create_article(article: schemas.ArticleCreate, user_id):
    db_article = models.Article(title=article.title, body=article.body, status=constant.draft)
    main.db_session.add(db_article)
    main.db_session.commit()
    db_reference = models.Reference(id_us=user_id, id_art=db_article.id, status=db_article.status)
    main.db_session.add(db_reference)
    main.db_session.commit()
    return db_article


# Получение информации о статьи по ее id:
def get_article_by_id(article_id: int):
    return main.db_session.query(models.Article).filter(models.Article.id == article_id).first()


# Проверка связи между пользователем и статьей:
def check_author_article(article_id: int, user_id: int):
    return main.db_session.query(models.Reference).filter(models.Reference.id_us == user_id, models.Reference.id_art == article_id).first()


# Изменение в бд статуса статьи: черновик -> опубликована:
def change_draft_published(article_id: int):
    changed_art = get_article_by_id(article_id=article_id)
    changed_art.status = constant.published
    main.db_session.add(changed_art)
    main.db_session.commit()
    return changed_art


# Вывод таблицы статей в статусе "опубликована":
def get_article_published(skip: int = 0, limit: int = 100):
    return main.db_session.query(models.Article).filter(models.Article.status == constant.published).offset(skip).limit(limit).all()


# Изменение в бд статуса статьи: опубликована -> одобрена:
def change_published_approved(article_id: int):
    changed_art = get_article_by_id(article_id=article_id)
    changed_art.status = constant.approved
    main.db_session.add(changed_art)
    main.db_session.commit()
    return changed_art


# Изменение в бд статуса статьи: одобрена -> черновик:
def change_approved_draft(article_id: int):
    changed_art = get_article_by_id(article_id=article_id)
    changed_art.status = constant.draft
    main.db_session.add(changed_art)
    main.db_session.commit()
    return changed_art


# Изменение тела статьи в бд:
def edit_draft(article: schemas.ArticleEditingIn):
    edited_draft = get_article_by_id(article_id=article.id)
    edited_draft.body = article.body
    main.db_session.add(edited_draft)
    main.db_session.commit()
    return edited_draft


# Изменение в бд статуса статьи: опубликована -> отклонена:
def change_published_rejected(article_id: int):
    changed_art = get_article_by_id(article_id=article_id)
    changed_art.status = constant.rejected
    main.db_session.add(changed_art)
    main.db_session.commit()


# Привязка автора к статье в бд:
def add_author(id_user_new: int, article_id: int):
    db_article_new = models.Reference(id_us=id_user_new, id_art=article_id, status=constant.draft)
    main.db_session.add(db_article_new)
    main.db_session.commit()
    return db_article_new


# Изменение роли автора в бд:
def approve_change_role(user_id: int, role: int):
    db_user = get_user_by_id(user_id=user_id)
    db_user.role = role
    main.db_session.add(db_user)
    main.db_session.commit()
    return db_user


# Указание блокировки пользователя в бд, удаление его комментариев:
def block_user(user_id: int):
    db_user = get_user_by_id(user_id=user_id)
    db_user.blocked = True
    main.db_session.add(db_user)
    main.db_session.commit()
    db_comment = main.db_session.query(models.Comment).filter(models.Comment.user_id == user_id).all()
    main.db_session.delete(db_comment)
    main.db_session.commit()
    block_articles(user_id=user_id)
    return db_user


# Изменение в статусе всех статей "опубликована" на "черновик" определенного автора:
def block_articles(user_id: int):
    refs = main.db_session.query(models.Reference).filter(models.Reference.id_us == user_id).all()
    for i in refs:
        article = main.db_session.query(models.Article).filter(models.Article.id == i.id_art, models.Article.status == constant.published).first()
        if article is None:
            continue
        article.status = constant.draft
        main.db_session.add(article)
        main.db_session.commit()


# Указание разблокировки пользователя:
def unblock_user(user_id: int):
    db_user = get_user_by_id(user_id=user_id)
    db_user.blocked = False
    main.db_session.add(db_user)
    main.db_session.commit()
    return db_user


# Добавление комментария в бд:
def make_comment(article_id: int, user_id, comment: schemas.CommentIn):
    db_comment = models.Comment(article_id=article_id, user_id=user_id, body=comment.body)
    main.db_session.add(db_comment)
    main.db_session.commit()
    return db_comment


# Получение информации о комментарии по его id:
def get_comment_by_id(comment_id: int):
    return main.db_session.query(models.Comment).filter(models.Comment.id == comment_id).first()


# Удаление комментария из бд
def delete_comment(comment_id: int):
    db_comment = main.db_session.query(models.Comment).filter(models.Comment.id == comment_id).first()
    main.db_session.delete(db_comment)
    main.db_session.commit()

