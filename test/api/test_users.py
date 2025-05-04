from src.api.users import create_new_user

import sqlalchemy
from src.api import auth
from src import database as db



def test_users():
    response = create_new_user("testuser")

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("SELECT username FROM users WHERE username = :username"),
            {"username": "testuser"}
        ).one()

    assert result.username == "testuser"
    assert response.status_code == 204

    response = create_new_user("testuser")
    assert response.status_code == 409

    create_new_user("testuser3")
    create_new_user("testuser4")
    create_new_user("testuser5")


    with db.engine.begin() as connection:
    result = connection.execute(
        sqlalchemy.text("SELECT username FROM users")
    ).fetchall()

    usernames = set([row.username for row in result])

    assert usernames == {"testuser", "testuser3", "testuser4", "testuser5"}
    

    