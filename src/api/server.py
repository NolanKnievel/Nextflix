from fastapi import FastAPI
from src.api import users, media
from starlette.middleware.cors import CORSMiddleware

description = """
Welcome to Nextlix!
"""
tags_metadata = [
    {"name": "users", "description": "Manage user accounts."}]


app = FastAPI(
    title="Nextflix",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Nolan Knievel",
        "email": "nknievel@calpoly.edu",
    },
    openapi_tags=tags_metadata,
)

origins = ["https://nextflix-mam5.onrender.com/"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(media.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Nextflix!"}
