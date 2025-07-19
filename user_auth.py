# user_auth.py

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from passlib.context import CryptContext

# Setup DB and password hashing
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
engine = create_engine("sqlite:///users.db")
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_user_by_username(db, username):
    return db.query(User).filter(User.username == username).first()

def create_user(db, username, password):
    hashed = pwd_context.hash(password)
    user = User(username=username, hashed_password=hashed)
    db.add(user)
    db.commit()

def verify_password(plain_password, hashed):
    return pwd_context.verify(plain_password, hashed)
