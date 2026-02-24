from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_premium = Column(Boolean, default=False)
    preferences = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con preferencias de ciudades
    city_preferences = relationship("UserCityPreference", back_populates="user")

class UserCityPreference(Base):
    __tablename__ = "user_city_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    city_name = Column(String, nullable=False)
    action = Column(String, nullable=False)  # "like" o "dislike"
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="city_preferences")

# Crear tablas si no existen (conserva datos)
Base.metadata.create_all(bind=engine)
