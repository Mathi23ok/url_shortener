from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
import time

from database import SessionLocal, engine, Base
from models import URL
from utils import generate_short_code

app = FastAPI()

Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")

# In-memory cache
cache = {}

# Rate limiting storage
rate_limit = {}
LIMIT = 5      # max requests
WINDOW = 10    # seconds


#Helper function
def render_home(request, short_url=None, error=None):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "short_url": short_url,
        "error": error
    })


# 🔧 Rate limiting logic
def is_rate_limited(ip):
    current_time = time.time()

    if ip not in rate_limit:
        rate_limit[ip] = []

    # remove old requests
    rate_limit[ip] = [
        t for t in rate_limit[ip] if current_time - t < WINDOW
    ]

    if len(rate_limit[ip]) >= LIMIT:
        return True

    rate_limit[ip].append(current_time)
    return False


# Home
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return render_home(request)


#Shorten URL
@app.post("/shorten")
def shorten_url(request: Request, url: str = Form(...)):

    # Rate limiting
    client_ip = request.client.host
    if is_rate_limited(client_ip):
        return render_home(request, error="Too many requests. Try later.")

    # Validation
    if not url or len(url.strip()) == 0:
        return render_home(request, error="URL cannot be empty")

    if not url.startswith(("http://", "https://")):
        return render_home(request, error="Invalid URL format")

    db = SessionLocal()

    for _ in range(5):
        short_code = generate_short_code()

        new_url = URL(short_code=short_code, long_url=url)

        try:
            db.add(new_url)
            db.commit()
            short_url = str(request.base_url) + short_code

            return render_home(request, short_url=short_url)

        except IntegrityError:
            db.rollback()
            continue

    raise HTTPException(status_code=500, detail="Could not generate unique URL")


# Redirect
@app.get("/{short_code}")
def redirect_url(short_code: str):

    #Cache check
    if short_code in cache:
        return RedirectResponse(cache[short_code])

    db = SessionLocal()

    url_entry = db.query(URL).filter(URL.short_code == short_code).first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found")

    
    cache[short_code] = url_entry.long_url

    url_entry.clicks += 1
    db.commit()

    return RedirectResponse(url_entry.long_url)