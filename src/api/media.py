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
    average_rating : float
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


# post show
@router.post("/shows{media_title}", status_code=status.HTTP_204_NO_CONTENT)
def post_show(media_title: str, director: str, seasons: int, episodes: int):
    pass


# review media
@router.post("/{media_title}/reviews", status_code=status.HTTP_204_NO_CONTENT)
def review_media(media_title: str, review: MediaReview):
    pass


# view reviews
@router.get("/{media_title}/reviews", response_model=List[MediaReview])
def view_reviews(media_title: str):
    pass

