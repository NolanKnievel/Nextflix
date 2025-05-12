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