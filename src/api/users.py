from dataclasses import dataclass
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List

from src.api.media import MediaInfo

import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth.get_api_key)],
)

# username - must be alphanumeric, 3-20 characters long, and start with a letter
class Username(BaseModel): 
    username: str = Field(..., min_length=3, max_length=20
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, s: str) -> str:
        if not s.isalnum() or not s[0].isalpha():
            raise ValueError("Username must be alphanumeric and start with a letter.")
        return s
    
class UserInfo(BaseModel):
    username: Username
    date_joined: str
    size_of_watchlist: int


# create user
@router.post("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def create_new_user(username: str):
    validated_username = Username(username=username).username

    with db.engine.begin() as connection:

        user_existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT username
                FROM users
                WHERE username = :username
                """
            ), [{"username": username}]
        ).fetchone()
        if user_existing is None:
            connection.execute(
                sqlalchemy.text(
                """
                INSERT INTO users (username)
                VALUES (:username)

                """
                ), [{"username": username}]
            )
        else:
            raise HTTPException(status_code=409, detail="Username already exists. Please try again.")


# Post to watchlist
@router.post("/{username}/watchlist", status_code=status.HTTP_204_NO_CONTENT)
def add_to_watchlist(username: str, title: str, have_watched: bool=False):
    pass


# Mark as watched
@router.patch("/{username}/watchlist/{media_title}", status_code=status.HTTP_204_NO_CONTENT)
def mark_as_watched(username: str, title: str):
    pass


# Get Watchlist
@router.get("/{username}/watchlist", response_model=List[MediaInfo])  
def get_watchlist(username: str, only_watched_media: bool=False):
    pass



# Search for user, maybe return all users on empty search?
@router.get("/search", response_model=List[Username])
def search_users(username: str):
    pass


# view user
@router.get("/{username}", response_model=UserInfo)
def view_user(username: str):
    pass


# friend user
@router.post("/{username}/friends", status_code=status.HTTP_204_NO_CONTENT)
def add_friend(username: str, friend_username: Username):
    pass

