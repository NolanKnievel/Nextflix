from src.api.users import create_new_user

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
        assert str(e.detail) == "Username already exists. Please try again."

    create_new_user("testuser3")
    create_new_user("testuser4")
    create_new_user("testuser5")


    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("SELECT username FROM users")
        ).fetchall()

    usernames = set([row.username for row in result])

    assert usernames == {"testuser", "testuser3", "testuser4", "testuser5"}
    

    