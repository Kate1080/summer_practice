from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from sqlalchemy import text
import uuid

from database import Base


class Reference(Base):
    __tablename__ = "reference"
    id_us = Column(Integer, ForeignKey("users.id"), primary_key=True)
    id_art = Column(Integer, ForeignKey("article.id"), primary_key=True)

    users = relationship("User", back_populates="refer")
    articles = relationship("Article", back_populates="refers")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(Integer)

    refer = relationship("Reference", back_populates="users")
    tokens = relationship("Token", back_populates="users")


class Article(Base):
    __tablename__ = "article"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    body = Column(String)
    status = Column(String)

    refers = relationship("Reference", back_populates="articles")


class Token(Base):
    __tablename__ = "tokens"
    token = Column(String, primary_key=True, unique=True, nullable=False, index=True)
    expires = Column(DateTime())
    user_id = Column(ForeignKey("users.id"))

    users = relationship("User", back_populates="tokens")
