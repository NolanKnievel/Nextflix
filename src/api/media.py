from dataclasses import dataclass
from fastapi import APIRouter, Depends, status, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

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
    director : str

    @field_validator("average_rating")
    @classmethod
    def validate_average_rating(cls, r: float) -> float:
        if r < 0 or r > 5:
            raise ValueError("Average rating must be between 0 and 5.")
        return r

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

class MediaRecommendation(BaseModel):
    id: int
    title: str
    media_type: str

    # media type must be movie or show
    @field_validator("media_type")
    @classmethod
    def validate_media_type(cls, s: str) -> str:
        if s not in ["movie", "show"]:
            raise ValueError("Media type must be either 'movie' or 'show'.")
        return s

class FilmSubmission(BaseModel):
    title: str = Field(..., min_length=1, max_length=100) 
    director: str = Field(..., min_length=1, max_length=100) 
    length: int = Field(..., gt=0, lt=1000)

class ShowSubmission(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    director: str = Field(..., min_length=1, max_length=100) 
    seasons: int = Field(..., gt=0, lt=100)
    episodes: int = Field(..., gt=0, lt=1000)



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
@router.get("/view", response_model=List[MediaInfo])
def view_media(media_title: Optional[str] = None):
    with db.engine.begin() as connection:

        # If media_title is provided, fetch media with that similar titles and their average ratings
        if media_title:
            media = connection.execute(
                sqlalchemy.text(
                    """
                    WITH avgs AS (
                        SELECT media_id, AVG(rating) as avg_rev
                        FROM reviews
                        GROUP BY media_id
                    )
                    SELECT media.media_id, media.title, COALESCE(avgs.avg_rev, 0) as average_rating, media.director
                    FROM media
                    LEFT JOIN avgs ON media.media_id = avgs.media_id
                    WHERE media.title ILIKE :media_title
                    ORDER BY average_rating DESC, media.title
                    """
                ), [{'media_title': f'%{media_title}%'}]  # Use ILIKE for case-insensitive search
            ).fetchall()

        # If media_title is None, fetch all media with their average ratings
        elif media_title is None:
            media = connection.execute(
                sqlalchemy.text(
                    """
                    WITH avgs AS (
                        SELECT media_id, AVG(rating) as avg_rev
                        FROM reviews
                        GROUP BY media_id
                    )
                    SELECT media.media_id, media.title, COALESCE(avgs.avg_rev, 0) as average_rating, media.director
                    FROM media
                    LEFT JOIN avgs ON media.media_id = avgs.media_id
                    ORDER BY average_rating DESC, media.title
                    """
                )).fetchall()
        if not media:
            raise HTTPException(status_code=404, detail="Media not found")
        
        # Convert the result set to a list of MediaInfo objects
        return [MediaInfo(id=row.media_id, title=row.title, average_rating=row.average_rating, director=row.director) for row in media]


# post film
@router.post("/films", response_model=FilmSubmission, status_code=status.HTTP_201_CREATED)
def post_film(film: FilmSubmission):
    with db.engine.begin() as connection:
        existing_media = connection.execute(
            sqlalchemy.text(
                """
                SELECT media_id
                FROM media
                WHERE title = :title AND
                media_type = 'movie'
                """
            ),[{'title':film.title,'director':film.director}]
        ).fetchone()
        if existing_media:
            raise HTTPException(status_code=409, detail="Movie already exists in database. Please try again")
        else: 
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO media (media_type,title,director)
                    VALUES ('movie',:title,:director)
                    RETURNING media_id
                    """
                ),[{'title':film.title,'director':film.director}]
            )
            # get the media_id of the newly inserted movie
            media_id = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT media_id
                    FROM media
                    WHERE title = :title AND
                    director = :director AND
                    media_type = 'movie'
                    """
                ),[{'title':film.title,'director':film.director}]
            ).one().media_id

            # insert into movies table
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO movies (media_id,length)
                    VALUES (:media_id,:length)
                    """
                ),[{'media_id':media_id,'length':film.length}]
            )
    return film


# post show
@router.post("/shows", response_model=ShowSubmission, status_code=status.HTTP_201_CREATED)
def post_show(show: ShowSubmission):
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
            ),[{'title':show.title,'director':show.director}]
        ).fetchone()
        if existing_media:
            raise HTTPException(status_code=409, detail="Show already exists in database. Please try again")
        else: 
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO media (media_type,title,director)
                    VALUES ('show',:title,:director)
                    RETURNING media_id
                    """
                ),[{'title':show.title,'director':show.director}]
            )
            # get the media_id of the newly inserted show
            media_id = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT media_id
                    FROM media
                    WHERE title = :title AND
                    director = :director AND
                    media_type = 'show'
                    """
                ),[{'title':show.title,'director':show.director}]
            ).one().media_id
            # insert into shows table
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO tv_shows (media_id,total_episodes,total_seasons)
                    VALUES (:media_id,:total_episodes,:total_seasons)
                    """
                ),[{'media_id':media_id,'total_episodes':show.episodes,'total_seasons':show.seasons}]
            )
    return show


# review media
@router.post("/{media_title}/reviews", response_model=MediaReview, status_code=status.HTTP_201_CREATED)
def review_media(media_id: int, review: MediaReview):
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
    return review

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




# COMPLEX ENDPOINT
@router.get("/{username}/recommendations", response_model=List[MediaRecommendation])
def get_recommendations(username: str):
    with db.engine.begin() as connection:
        # get target user id
        user_data = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, friends
                FROM users
                WHERE username = :username
                """
            ),
            {"username": username}
        ).fetchone()

        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        user_id = user_data.id
        friend_ids = user_data.friends

        print(f'user id: {user_id} friend_ids: {friend_ids}')

        if not friend_ids:
            return []

        # get target user watchlist
        user_watchlist_media_ids = connection.execute(
            sqlalchemy.text(
                """
                SELECT media_id
                FROM watchlists
                WHERE user_id = :user_id
                """
            ),
            {"user_id": user_id}
        ).fetchall()
        

        user_watchlist_media_ids = {row.media_id for row in user_watchlist_media_ids}

        print(f'user watchlist media ids: {user_watchlist_media_ids}')

        # fetch recommendations from friends' watchlists
        recommendations = []
        for friend_id in friend_ids:
            friend_recommendations = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT DISTINCT m.media_id, m.title, m.media_type, m.director
                    FROM watchlists w
                    JOIN media m ON w.media_id = m.media_id
                    WHERE w.user_id = :friend_id
                      AND w.media_id NOT IN ( SELECT media_id
                                                FROM watchlists
                                                WHERE user_id = :user_id
                                                ) 
                    LIMIT 1
                    """
                ),
                {"friend_id": friend_id, "user_id" : user_id}
            ).fetchall()

            recommendations.extend(friend_recommendations)

            # stop if at 10 recommendations
            if len(recommendations) >= 10:
                break

        print(f'recommendations: {recommendations}')


        return [
            MediaRecommendation(
                id=row.media_id,
                title=row.title,
                media_type=row.media_type,
                director=row.director
            )
            for row in recommendations[:10] 
        ]