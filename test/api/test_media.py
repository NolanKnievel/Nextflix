import pytest
from src.api.users import create_new_user, add_to_watchlist, get_watchlist, mark_as_watched
from src.api.media import *
import sqlalchemy
from src.api import auth
from src import database as db

def test_post_review() -> None:
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE media RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("INSERT INTO media VALUES (1,'movie','media1','director1')"))
        connection.execute(sqlalchemy.text("INSERT INTO media VALUES (2,'movie','media2','director2')"))
    create_new_user("USER1")
    create_new_user("USER2")    
    review1 = MediaReview(username = "USER1",review = "good",rating = 4)
    review2 = MediaReview(username = "USER2",review = "bad",rating = 1)
    review3 = MediaReview(username = "USER2",review = "changed mind",rating = 5)
    review_media(1,review1)
    review_media(1,review2)
    review_media(1,review3)

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("SELECT * FROM reviews")
        ).fetchall()

    ratings = [row.rating for row in result]
    reviews = [row.review for row in result]
    assert ratings == [4.0,5.0]
    assert reviews == ['good', 'changed mind']

def test_post_film() -> None:
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("TRUNCATE TABLE media RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE movies RESTART IDENTITY CASCADE"))
    post_film("MOVIE1","DIRECTOR1",60)
    post_film("MOVIE2","DIRECTOR2",120)
    with db.engine.begin() as connection:
        media_result = connection.execute(
            sqlalchemy.text("SELECT * FROM media")
        ).fetchall()
        movie_result = connection.execute(
            sqlalchemy.text("SELECT * FROM movies")
        ).fetchall()

    media_ids = [row.media_id for row in media_result]
    media_titles = [row.title for row in media_result]
    movie_lengths = [row.length for row in movie_result]

    assert media_ids == [1,2]
    assert media_titles == ["MOVIE1","MOVIE2"]
    assert movie_lengths == [60,120]
    with pytest.raises(HTTPException) as exception:
        post_film("MOVIE1","DIRECTOR1",60)
    assert exception.value.status_code == 409


def test_post_show() -> None:
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("TRUNCATE TABLE media RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE tv_shows RESTART IDENTITY CASCADE"))
    post_show("TVSHOW1","DIRECTOR1",5,100)
    post_show("TVSHOW2","DIRECTOR2",1,12)
    with db.engine.begin() as connection:
        media_result = connection.execute(
            sqlalchemy.text("SELECT * FROM media")
        ).fetchall()
        tv_result = connection.execute(
            sqlalchemy.text("SELECT * FROM tv_shows")
        ).fetchall()

    media_ids = [row.media_id for row in media_result]
    media_titles = [row.title for row in media_result]
    tv_seasons = [row.total_seasons for row in tv_result]
    tv_episodes = [row.total_episodes for row in tv_result]
    assert media_ids == [1,2]
    assert media_titles == ["TVSHOW1","TVSHOW2"]
    assert tv_seasons == [5,1]
    assert tv_episodes == [100,12]

    with pytest.raises(HTTPException) as exception:
        post_show("TVSHOW1","DIRECTOR1",5,100)
    assert exception.value.status_code == 409
    