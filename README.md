
# URL Shortener (FastAPI)
A simple URL shortener built using FastAPI.  
Takes a long URL, generates a short code, and redirects back to the original link.

This project started as a basic backend exercise and was extended with caching, rate limiting, and UI improvements.

---

## What it does

- Converts long URLs into short links
- Redirects short links to the original URL
- Tracks number of clicks
- Prevents spam with basic rate limiting
- Uses caching to reduce database hits
- Provides a minimal UI for interaction

---

## Tech Stack

- FastAPI (backend)
- SQLite + SQLAlchemy (database)
- Jinja2 (templates)
- Uvicorn (server)

## How it works

1. User submits a URL  
2. Backend validates it  
3. A random short code is generated  
4. Mapping is stored in the database  
5. Short URL is returned  

For redirects:
- First checks cache  
- If not found, queries database  
- Stores result in cache for future requests  
---
## Key decisions
Random short codes + retry 
  Simple approach, avoids managing a global counter
Cache-aside pattern
  Reduces database load for repeated redirects
Rate limiting  
  Prevents abuse (basic IP-based control)
Running locally

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload
