from fastapi import APIRouter, Depends, status, HTTPException
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset():
    """
    Reset DB, clear all users and media
    """

    # clear all data in the database
    print("Resetting state...")
    try:
        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM users         
                    """
                ) 
            )
            connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM media         
                    """
                ) 
            )
            connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM movies         
                    """
                ) 
            )
            connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM reviews         
                    """
                ) 
            )
            connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM tv_shows         
                    """
                ) 
            )
            connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM watchlists         
                    """
                ) 
            )
    except Exception as e:
        raise HTTPException(500,detail = "Could not reset")