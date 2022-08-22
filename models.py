from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

import uuid

from database import Base


class Reference(Base):
    __tablename__ = "reference"
    id_us = Column(String, ForeignKey("users.login"), primary_key=True)
    id_art = Column(Integer, ForeignKey("article.id"), primary_key=True)

    users = relationship("User", back_populates="refer")
    articles = relationship("Article", back_populates="refers")


class User(Base):
    __tablename__ = "users"
    login = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    role = Column(Integer)

    refer = relationship("Reference", back_populates="users")


class Article(Base):
    __tablename__ = "article"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    body = Column(String)
    status = Column(String)

    refers = relationship("Reference", back_populates="articles")
