from dataclasses import dataclass
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List

import sqlalchemy
from src.api import auth
from src import database as db


router = APIRouter(
    prefix="/media",
    tags=["media"],
    dependencies=[Depends(auth.get_api_key)],
)

class MediaInfo(BaseModel):
    id : int
    title : str
    director : str

class MediaType(BaseModel):
    title: str
    media_type: str

    # media type must be movie or show
    @field_validator("media_type")
    @classmethod
    def validate_media_type(cls, s: str) -> str:
        if s not in ["movie", "show"]:
            raise ValueError("Media type must be either 'movie' or 'show'.")
        return s

class MediaReview(BaseModel):
    username: str
    review: str
    rating: float = Field(..., gt=0, lt=6) # review must be between 1 and 5 inclusive


# search media
@router.get("/search", response_model=List[str])
def search_media(media_name: str, media_type: str):
    pass


# view media
@router.get("/{media_title}", response_model=MediaInfo)
def view_media(media_title: str):
    pass


# post film
@router.post("/films{media_title}", status_code=status.HTTP_204_NO_CONTENT)
def post_film(media_title: str, director: str, length: int):
    pass
    with db.engine.begin() as connection:
        existing_media = connection.execute(
            sqlalchemy.text(
                """
                SELECT media_id
                FROM media
                WHERE 
                title = :title AND
                director = :director AND
                media_type = 'movie'
                """
            ),[{'title':media_title,'director':director}]
        ).fetchone()
        if existing_media:
            raise HTTPException(status_code=409, detail="Movie already exists in database. Please try again")
        else: 
            media_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO media (media_type,title,director)
                    VALUES ('movie',:title,:director)
                    RETURNING media_id
                    """
                ),[{'title':media_title,'director':director}]
            ).scalar()
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO movies (media_id,length)
                    VALUES (:media_id,:length)
                    """
                ),[{'media_id':media_id,'length':length}]
            )


# post show
@router.post("/shows{media_title}", status_code=status.HTTP_204_NO_CONTENT)
def post_show(media_title: str, director: str, seasons: int, episodes: int):
    pass
    with db.engine.begin() as connection:
        existing_media = connection.execute(
            sqlalchemy.text(
                """
                SELECT media_id
                FROM media
                WHERE 
                title = :title AND
                director = :director AND
                media_type = 'show'
                """
            ),[{'title':media_title,'director':director}]
        ).fetchone()
        if existing_media:
            raise HTTPException(status_code=409, detail="Show already exists in database. Please try again")
        else: 
            media_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO media (media_type,title,director)
                    VALUES ('show',:title,:director)
                    RETURNING media_id
                    """
                ),[{'title':media_title,'director':director}]
            ).scalar()
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO tv_shows (media_id,total_episodes,total_seasons)
                    VALUES (:media_id,:total_episodes,:total_seasons)
                    """
                ),[{'media_id':media_id,'total_episodes':episodes,'total_seasons':seasons}]
            )


# review media
@router.post("/{media_title}/reviews", status_code=status.HTTP_204_NO_CONTENT)
def review_media(media_id: int, review: MediaReview):
    pass
    with db.engine.begin() as connection:
        user_id = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM users
                WHERE username = :username
                """
            ), [{"username":review.username}]
        ).scalar()
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO reviews (user_id, media_id, rating, review)
                VALUES (:user_id, :media_id, :rating, :review)
                ON CONFLICT (user_id, media_id)
                DO UPDATE SET
                rating = EXCLUDED.rating,
                review = EXCLUDED.review
                """
            ), [{"user_id": user_id,"media_id": media_id,"rating":review.rating,"review":review.review}]
        )


# view reviews
@router.get("/{media_title}/reviews", response_model=List[MediaReview])
def view_reviews(media_title: str):
    pass

