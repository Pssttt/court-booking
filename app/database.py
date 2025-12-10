"""
Database connection and session management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
SessionLocal = None
Base = declarative_base()


def get_db_engine():
    global engine
    if engine is None and DATABASE_URL:
        url = DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)

        try:
            engine = create_engine(url)
        except Exception as e:
            print(f"Failed to create database engine: {e}")
            return None

    return engine


def get_db_session():
    global SessionLocal
    if SessionLocal is None:
        eng = get_db_engine()
        if eng:
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=eng)

    if SessionLocal:
        return SessionLocal()
    return None
