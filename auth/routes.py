# auth/routes.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from auth.models import User
from auth.utils import hash_password, verify_password
from database import SessionLocal
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})

@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="user", value=user.email)
    return response

@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": ""})

@router.post("/register", response_class=HTMLResponse)
async def register_post(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "User already exists"})
    new_user = User(email=email, hashed_password=hash_password(password))
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/login", status_code=302)
