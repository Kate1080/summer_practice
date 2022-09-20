from sqlalchemy import Column, Integer, String, ForeignKey, BOOLEAN, Text
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from sqlalchemy import text
import uuid

from database import Base


# Связующая таблица: соотношение "many to many"
class Reference(Base):
    __tablename__ = "reference"
    id_us = Column(Integer, ForeignKey("users.id"), primary_key=True)
    id_art = Column(Integer, ForeignKey("article.id"), primary_key=True)

    users = relationship("User", back_populates="refer")
    articles = relationship("Article", back_populates="refers")


# Таблица пользователей
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, unique=True,)
    hashed_password = Column(String)
    role = Column(Integer)
    blocked = Column(BOOLEAN, default=False)

    refer = relationship("Reference", back_populates="users")
    tokens = relationship("Token", back_populates="users")
    comment = relationship("Comment", back_populates="users")
    rating = relationship("Rating", back_populates="users")


# Таблица статей
class Article(Base):
    __tablename__ = "article"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    time_approved = Column(String)

    refers = relationship("Reference", back_populates="articles")
    comments = relationship("Comment", back_populates="article")
    ratings = relationship("Rating", back_populates="articles")


# Таблица сессий
class Token(Base):
    __tablename__ = "tokens"
    token = Column(String, primary_key=True, nullable=False, index=True)
    expires = Column(DateTime())
    user_id = Column(ForeignKey("users.id"))

    users = relationship("User", back_populates="tokens")


# Таблица комментариев
class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("article.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    body = Column(String, nullable=False)

    users = relationship("User", back_populates="comment")
    article = relationship("Article", back_populates="comments")


# Таблица оценок
class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("article.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)

    articles = relationship("Article", back_populates="ratings")
    users = relationship("User", back_populates="rating")

