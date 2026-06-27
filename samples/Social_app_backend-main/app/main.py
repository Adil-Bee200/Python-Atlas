from fastapi import FastAPI
from app.routers import auth
from .routers import users, posts, votes
from . import models
from .database import engine
from fastapi.middleware.cors import CORSMiddleware

import logging
logging.basicConfig(level=logging.DEBUG)
print("🔥 App startup initiated...")

## models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from Railway Boy"}


app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]    
)


app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(votes.router)

print("helloworld")
