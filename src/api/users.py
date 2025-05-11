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

class WatchlistItem(BaseModel):
    media_id : int
    title : str
    director : str
    have_watched : bool



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
    
    with db.engine.begin() as connection:
        # fetch user_id
        user_id = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM users
                WHERE username = :username"""
            ), [{"username": username}]
        ).scalar()

        if not user_id:
            raise HTTPException(status_code=404, detail="User not found. Please try again.")

        # fetch media_id
        media_id = connection.execute(
            sqlalchemy.text(
                """
                SELECT media_id FROM media
                WHERE title = :title
                """
            ), [{"title": title}]
        ).scalar()
        
        if not media_id:
            raise HTTPException(status_code=404, detail="Media not found. Please try again.")

        # check if entry already exists
        existing_entry = connection.execute(
            sqlalchemy.text(
                """
                SELECT * FROM watchlists
                WHERE user_id = :user_id AND media_id = :media_id
                """
            ), [{"user_id": user_id, "media_id": media_id}]
        ).fetchone()

        if existing_entry:
            return
        
        # add to watchlist
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO watchlists (user_id, media_id, have_watched)
                VALUES (:user_id, :media_id, :have_watched)
                """
            ), [{"user_id": user_id, "media_id": media_id, "have_watched": have_watched}]
        )
      



# Mark as watched
@router.patch("/{username}/watchlist/{media_title}", status_code=status.HTTP_204_NO_CONTENT)
def mark_as_watched(username: str, title: str):
    pass


# Get Watchlist
@router.get("/{username}/watchlist", response_model=List[WatchlistItem])  
def get_watchlist(username: str, only_watched_media: bool=False):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT * FROM watchlists
                JOIN users ON watchlists.user_id = users.id
                JOIN media ON watchlists.media_id = media.media_id
                WHERE users.username = :username
                """
            ), [{"username": username}]
        ).fetchall()
        print(f'result: {result}')
    
    watchlist = [WatchlistItem(media_id=entry.media_id, title=entry.title, director=entry.director, have_watched=entry.have_watched) for entry in result]
    if only_watched_media:
        watchlist = [entry for entry in watchlist if entry.have_watched]

    return watchlist
    



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

