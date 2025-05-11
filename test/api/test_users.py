from src.api.users import create_new_user, add_to_watchlist

import sqlalchemy
from src.api import auth
from src import database as db



def test_users():
    # clear users table before testing
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("DELETE FROM users"))


    response = create_new_user("testuser")

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("SELECT username FROM users WHERE username = :username"),
            {"username": "testuser"}
        ).one()

    assert result.username == "testuser"

    # should raise an HTTPException with status code 409
    try:
        create_new_user("testuser")
    except Exception as e:
        assert e.status_code == 409

    create_new_user("testuser3")
    create_new_user("testuser4")
    create_new_user("testuser5")


    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("SELECT username FROM users")
        ).fetchall()

    usernames = set([row.username for row in result])

    assert usernames == {"testuser", "testuser3", "testuser4", "testuser5"}
    

    
def test_add_to_watchlist():
    # create a new user
    create_new_user("testuser33")

    # insert a media item into the media table
    with db.engine.begin() as connection:
        media_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO media (media_type, title, director) VALUES (:media_type, :title, :director)
                RETURNING media_id
                """
            ),
            {
                "media_type": "movie",
                "title": "Test Movie",
                "director": "Test Director"
            }
        ).scalar_one()

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO movies (media_id, length) VALUES (:media_id, :length)
                """
            ),
            {
                "media_id": media_id,
                "length": 120
            }
        )

    # add to watchlist
    add_to_watchlist("testuser", "Test Movie", have_watched=False)

    # check if the entry was added to the watchlist
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT * FROM watchlists
                WHERE user_id = (SELECT id FROM users WHERE username = :username)
                AND media_id = :media_id
                """
            ),
            {
                "username": "testuser",
                "media_id": media_id
            }
        ).fetchone()

    assert result is not None

    # tear down
    # delete the movie from the movies table
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM movies WHERE media_id = :media_id
                """
            ),
            {
                "media_id": media_id
            }
        )
        # delete the movie watchlist
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM watchlists WHERE user_id = (SELECT id FROM users WHERE username = :username)
                AND media_id = :media_id
                """
            ),
            {
                "username": "testuser",
                "media_id": media_id
            }
        )
        # delete the user from the users table
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM users WHERE username = :username
                """
            ),
            {
                "username": "testuser"
            }
        )
        # delete the media from the media table
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM media WHERE media_id = :media_id
                """
            ),
            {
                "media_id": media_id
            }
        )

