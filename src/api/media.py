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
    average_rating : float # average rating must be between 0 and 5 inclusive
    def validate_average_rating(cls, r: float) -> float:
        if r < 0 or r > 5:
            raise ValueError("Average rating must be between 0 and 5.")
        return r
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
    with db.engine.begin() as connection:
        search_results = connection.execute(
            sqlalchemy.text(
                """
                SELECT title
                FROM media
                WHERE title LIKE :media_name AND media_type = :media_type
                """
            ),
            {"media_name": '%' + media_name + '%', "media_type": media_type}  # Corrected parameter passing
        ).fetchall()
        
        if not search_results:  # Use `not search_results` to check for empty results
            raise HTTPException(status_code=404, detail="Media not found")
        
        # Extract titles from the result set
        return [row.title for row in search_results]


# view media
@router.get("/{media_title}", response_model=MediaInfo)
def view_media(media_title: str):
    with db.engine.begin() as connection:
        media = connection.execute(
            sqlalchemy.text(
                """
                SELECT media.media_id, title, AVG(reviews.rating) as average_rating, director
                FROM media
                JOIN reviews on media.media_id = reviews.media_id
                WHERE title = :media_title
                GROUP BY media.media_id
                """
            ), [{"media_title": media_title}]
        ).fetchone()
        if media is None:
            raise HTTPException(status_code=404, detail="Media not found")
        return MediaInfo(id=media.media_id, title=media.title, average_rating=media.average_rating, director=media.director)


# post film
@router.post("/films{media_title}", status_code=status.HTTP_204_NO_CONTENT)
def post_film(media_title: str, director: str, length: int):
    pass


# post show
@router.post("/shows{media_title}", status_code=status.HTTP_204_NO_CONTENT)
def post_show(media_title: str, director: str, seasons: int, episodes: int):
    pass


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
    with db.engine.begin() as connection:
        reviews = connection.execute(
            sqlalchemy.text(
                """
                SELECT username, rating, review
                FROM reviews
                JOIN users on reviews.user_id = users.id
                JOIN media on reviews.media_id = media.media_id
                WHERE title = :media_title
                """
            ), [{"media_title": media_title}]
        ).fetchall()
        if not reviews:
            raise HTTPException(status_code=404, detail="No reviews found")
        return [MediaReview(username=row.username, rating=row.rating, review=row.review) for row in reviews]
    pass

