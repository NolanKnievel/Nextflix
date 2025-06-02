import sqlalchemy
from src.api import auth
from src import database as db

def depopulate():
    """
    Depopulate the database by dropping all tables.
    """
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text("DELETE FROM watchlists")
        )
        connection.execute(
            sqlalchemy.text("DELETE FROM reviews")
        )
        connection.execute(
            sqlalchemy.text("DELETE FROM users")
        )
        connection.execute(
            sqlalchemy.text("DELETE FROM tv_shows")
        )
        connection.execute(
            sqlalchemy.text("DELETE FROM movies")
        )
        connection.execute(
            sqlalchemy.text("DELETE FROM media")
        )



if __name__ == "__main__":
    depopulate()
    print("Database has been depopulated")