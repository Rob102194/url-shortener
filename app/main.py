from fastapi import FastAPI
from app.api import auth

app = FastAPI(title="URL Shortener API")
app.include_router(auth.router)

@app.get("/")
def root():
    return {"status": "ok"}
