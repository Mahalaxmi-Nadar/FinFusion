from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal, engine, Base, User, PortfolioEntry
from datetime import datetime

import joblib, pandas as pd, bcrypt, requests

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
Base.metadata.create_all(bind=engine)

models, encoders = {}, {}
for label in ["Recommendation", "Term_Suggested", "Risk_Level"]:
    models[label] = joblib.load(f"models/{label}_model.pkl")
    encoders[label] = joblib.load(f"models/{label}_encoder.pkl")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_get(request: Request):
    fields = ["BTC_Boll_lower","BTC_Boll_upper","BTC_Change","BTC_MACD","BTC_MACD_signal","BTC_RSI","BTC_EMA_20","BTC_Volume"]
    return templates.TemplateResponse("dashboard.html", {"request":request,"result":{},"fields": fields})

@app.post("/dashboard", response_class=HTMLResponse)
def dashboard_post(request: Request, BTC_Boll_lower: float = Form(...), BTC_Boll_upper: float = Form(...),
                   BTC_Change: float = Form(...), BTC_MACD: float = Form(...), BTC_MACD_signal: float = Form(...),
                   BTC_RSI: float = Form(...), BTC_EMA_20: float = Form(...), BTC_Volume: float = Form(...),
                   db: Session = Depends(get_db)):
    features = {
        "BTC_Boll_lower": BTC_Boll_lower,
        "BTC_Boll_upper": BTC_Boll_upper,
        "BTC_Change": BTC_Change,
        "BTC_MACD": BTC_MACD,
        "BTC_MACD_signal": BTC_MACD_signal,
        "BTC_RSI": BTC_RSI,
        "BTC_EMA_20": BTC_EMA_20,
        "BTC_Volume": BTC_Volume
    }

    X = pd.DataFrame([features])
    result = {}
    confidences = {}
    probas = {}
    classes = {}

    for label in models:
        proba = models[label].predict_proba(X)[0]
        pred = models[label].predict(X)[0]
        decoded = encoders[label].inverse_transform([pred])[0]
        result[label] = f"{decoded} ({round(100 * max(proba), 2)}%)"
        confidences[label] = round(100 * max(proba), 2)
        probas[label] = [round(p * 100, 2) for p in proba]
        classes[label] = list(encoders[label].inverse_transform(range(len(proba))))

    # Add entry to portfolio
    entry = PortfolioEntry(
        user_id=1,
        feature_input="BTCUSDT",
        recommendation=encoders["Recommendation"].inverse_transform([models["Recommendation"].predict(X)[0]])[0],
        term=encoders["Term_Suggested"].inverse_transform([models["Term_Suggested"].predict(X)[0]])[0],
        risk=encoders["Risk_Level"].inverse_transform([models["Risk_Level"].predict(X)[0]])[0],
        confidence=confidences.get("Recommendation", 0),
        asset_type="crypto",
        amount=25000,
        date=datetime.utcnow()
    )
    db.add(entry)
    db.commit()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "result": result,
        "probas": probas,
        "classes": classes,
        "fields": features.keys()
    })

@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/signup", response_class=HTMLResponse)
def signup_get(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup", response_class=HTMLResponse)
def signup_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username taken"})
    pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    db.add(User(username=username, hashed_password=pw))
    db.commit()
    return RedirectResponse(url="/login", status_code=302)

@app.get("/logout")
def logout():
    return RedirectResponse(url="/")

@app.get("/portfolio", response_class=HTMLResponse)
async def portfolio(request: Request):
    db = SessionLocal()
    entries = db.query(PortfolioEntry).order_by(PortfolioEntry.date.desc()).all()
    db.close()
    return templates.TemplateResponse("portfolio.html", {
        "request": request,
        "entries": entries
    })

@app.get("/charts", response_class=HTMLResponse)
def charts(request: Request):
    return templates.TemplateResponse("charts.html", {"request":request})

@app.get("/news", response_class=HTMLResponse)
def news(request: Request):
    return templates.TemplateResponse("news.html", {"request":request})

@app.get("/trending", response_class=HTMLResponse)
def trending(request: Request):
    return templates.TemplateResponse("trending.html", {"request":request})

@app.get("/assets", response_class=HTMLResponse)
def assets(request: Request):
    return templates.TemplateResponse("assets.html", {"request": request})

@app.get("/assets/overview", response_class=HTMLResponse)
def asset_overview(request: Request, db: Session = Depends(get_db)):
    total_value = db.query(func.sum(PortfolioEntry.current_value)).scalar() or 0
    total_invested = db.query(func.sum(PortfolioEntry.amount)).scalar() or 0
    net_pnl = total_value - total_invested
    crypto_count = db.query(PortfolioEntry).filter(PortfolioEntry.asset_type == "crypto").count()
    stock_count = db.query(PortfolioEntry).filter(PortfolioEntry.asset_type == "stock").count()
    funding_wallet = db.query(func.sum(PortfolioEntry.amount)).filter(PortfolioEntry.asset_name == "INR").scalar() or 0
    inr_wallet = 5000
    usd_wallet = 200

    return templates.TemplateResponse("assets_overview.html", {
        "request": request,
        "total_value": round(total_value, 2),
        "net_pnl": round(net_pnl, 2),
        "crypto_count": crypto_count,
        "stock_count": stock_count,
        "funding_wallet": funding_wallet,
        "inr_wallet": inr_wallet,
        "usd_wallet": usd_wallet
    })
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/assets/spot", response_class=HTMLResponse)
def asset_spot(request: Request):
    return templates.TemplateResponse("assets_spot.html", {"request": request})

@app.get("/assets/earn", response_class=HTMLResponse)
def asset_earn(request: Request):
    return templates.TemplateResponse("assets_earn.html", {"request": request})

NEWS_API_KEY = "YOUR_NEWSAPI_KEY"
COINGECKO_API = "https://api.coingecko.com/api/v3/search/trending"

@app.get("/news-api")
def news_api():
    resp = requests.get(f"https://newsapi.org/v2/top-headlines?language=en&pageSize=5&apiKey={NEWS_API_KEY}")
    return JSONResponse(resp.json())

@app.get("/trending-api")
def trending_api():
    return JSONResponse(requests.get(COINGECKO_API).json())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

