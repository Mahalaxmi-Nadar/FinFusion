from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# SQLite database file
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class PortfolioEntry(Base):
    __tablename__ = "portfolio_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    feature_input = Column(String)
    recommendation = Column(String)
    term = Column(String)
    risk = Column(String)
    confidence = Column(Float)
    asset_type = Column(String)
    amount = Column(Float)
    current_value = Column(Float, default=0.0)
    asset_name = Column(String, default="BTCUSDT")
    date = Column(DateTime, default=datetime.utcnow)
