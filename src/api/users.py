from dataclasses import dataclass
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List

from src.api.media import MediaInfo

import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# username - must be alphanumeric, 3-20 characters long, and start with a letter
class Username(BaseModel): 
    username: str = Field(..., min_length=3, max_length=20
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, s: str) -> str:
        if not s.isalnum() or not s[0].isalpha():
            raise HTTPException(status_code=400, detail="Username must be alphanumeric and start with a letter.")
            # raise ValueError("Username must be alphanumeric and start with a letter.")
        return s
    
class UserInfo(BaseModel):
    username: Username
    date_joined: str
    size_of_watchlist: int

class WatchlistItem(BaseModel):
    media_id : int
    title : str
    director : str
    have_watched : bool



# create user
@router.post("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def create_new_user(username: str):
    validated_username = Username.validate_username(username)

    # Check if username is correct length
    if len(validated_username) < 3 or len(validated_username) > 20:
        raise HTTPException(status_code=400, detail="Username must be between 3 and 20 characters long.")

    with db.engine.begin() as connection:

        user_existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT username
                FROM users
                WHERE username = :username
                """
            ), [{"username": username}]
        ).fetchone()
        if user_existing is None:
            connection.execute(
                sqlalchemy.text(
                """
                INSERT INTO users (username)
                VALUES (:username)
                """
                ), [{"username": username}]
            )
        else:
            raise HTTPException(status_code=409, detail="Username already exists. Please try again.")


# Post to watchlist
@router.post("/{username}/watchlist", status_code=status.HTTP_204_NO_CONTENT)
def add_to_watchlist(username: str, title: str, have_watched: bool=False):
    
    with db.engine.begin() as connection:
        # fetch user_id
        user_id = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM users
                WHERE username = :username"""
            ), [{"username": username}]
        ).scalar()

        if not user_id:
            raise HTTPException(status_code=404, detail="User not found. Please try again.")

        # fetch media_id
        media_id = connection.execute(
            sqlalchemy.text(
                """
                SELECT media_id FROM media
                WHERE title = :title
                """
            ), [{"title": title}]
        ).scalar()
        
        if not media_id:
            raise HTTPException(status_code=404, detail="Media not found. Please try again.")

        # check if entry already exists
        existing_entry = connection.execute(
            sqlalchemy.text(
                """
                SELECT * FROM watchlists
                WHERE user_id = :user_id AND media_id = :media_id
                """
            ), [{"user_id": user_id, "media_id": media_id}]
        ).fetchone()

        if existing_entry:
            raise HTTPException(status_code = 409, detail = "Media already in watchlist")
        
        # add to watchlist
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO watchlists (user_id, media_id, have_watched)
                VALUES (:user_id, :media_id, :have_watched)
                """
            ), [{"user_id": user_id, "media_id": media_id, "have_watched": have_watched}]
        )
      



# Mark as watched
@router.patch("/{username}/watchlist/{media_title}", status_code=status.HTTP_204_NO_CONTENT)
def mark_as_watched(username: str, media_title: str):
    with db.engine.begin() as connection:
        # check that entry exists
        row = connection.execute(
            sqlalchemy.text(
                """
                SELECT * FROM watchlists
                WHERE user_id = (SELECT id FROM users WHERE username = :username)
                AND media_id = (SELECT media_id FROM media WHERE title = :title)
                """
            ), [{"username": username, "title": media_title}]
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Entry not found. Please try again.")

        # update entry
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE watchlists
                SET have_watched = TRUE
                WHERE user_id = (SELECT id FROM users WHERE username = :username)
                AND media_id = (SELECT media_id FROM media WHERE title = :title)
                """
            ), [{"username": username, "title": media_title}]
        )


# Get Watchlist
@router.get("/{username}/watchlist", response_model=List[WatchlistItem])  
def get_watchlist(username: str, only_watched_media: bool=False):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT * FROM watchlists
                JOIN users ON watchlists.user_id = users.id
                JOIN media ON watchlists.media_id = media.media_id
                WHERE users.username = :username
                """
            ), [{"username": username}]
        ).fetchall()
        print(f'result: {result}')
    
    watchlist = [WatchlistItem(media_id=entry.media_id, title=entry.title, director=entry.director, have_watched=entry.have_watched) for entry in result]
    if only_watched_media:
        watchlist = [entry for entry in watchlist if entry.have_watched]

    return watchlist
    



# Search for user, maybe return all users on empty search?
@router.get("/search", response_model=List[Username])
def search_users(username: str):
    with db.engine.begin() as connection:

        result = connection.execute(
            sqlalchemy.text(
            """
            SELECT username
            FROM users
            WHERE LOWER(username) LIKE LOWER(:username)
            """
            ), [{"username": f"{username}%"}]
            ).fetchall()

        

        if not result:
            raise HTTPException(status_code=404, detail="No users found. Please try again.")

        return [Username(username=row.username) for row in result]


# view user
@router.get("/{username}", response_model=UserInfo)
def view_user(username: str):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
            
                """
                SELECT *
                FROM users AS u
                WHERE u.username = :username
                """
            ), [{"username": username}]
        ).fetchone()


        if not result:
            raise HTTPException(status_code=404, detail="User not found. Please try again.")
        
        
        watchlist_count = connection.execute(
            sqlalchemy.text(
                """
                SELECT COUNT(*)
                FROM watchlists AS w
                WHERE w.user_id = (SELECT id FROM users WHERE username = :username)
                """
            ), [{"username": username}]        
            ).scalar_one()
        
        return UserInfo(username=Username(username=username), date_joined=str(result.date_joined), size_of_watchlist=watchlist_count)

        

# friend user
@router.post("/{username}/friends", status_code=status.HTTP_204_NO_CONTENT)
def add_friend(username: str, friend_username: Username):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
            
                """
                SELECT id 
                FROM users
                WHERE username = :username
                """
            ), [{"username": username}]
        ).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="User not found. Please try again.")
        
        user_id = result.id

        result2 = connection.execute(
            sqlalchemy.text(
            
                """
                SELECT id 
                FROM users
                WHERE username = :username
                """
            ), [{"username": friend_username.username}]
        ).fetchone()

        if not result2:
            raise HTTPException(status_code=404, detail="User not found. Please try again.")
        
        friend_id = result2.id

        # check if entry already exists
        existing_entry = connection.execute(
            sqlalchemy.text(
                """
                SELECT friends
                FROM users
                WHERE id = :user_id
                """
            ), [{"user_id": user_id}]
        ).one()

        friend_list = existing_entry.friends or []
        if friend_id in friend_list:
            raise HTTPException(status_code=409, detail="Already friends with this user.")
        else:
            friend_list.append(friend_id)
            # add to friend list
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE users
                    SET friends = :friend_list
                    WHERE id = :user_id
                    """
                ), [{"friend_list": friend_list, "user_id": user_id}]
            )

# Get suggested friends
@router.get("/{username}/suggested_friends", response_model=List[Username])
def get_suggested_friends(username: str):
    with db.engine.begin() as connection:
        # fetch user_id
        user_id = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM users
                WHERE username = :username
                """
            ), [{"username": username}]
        ).scalar()

        if not user_id:
            raise HTTPException(status_code=404, detail="User not found. Please try again.")

        # fetch friends
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT friends
                FROM users
                WHERE id = :user_id
                """
            ), [{"user_id": user_id}]
        ).fetchone()

        if not result or not result.friends:
            raise HTTPException(status_code=404, detail="No friends found. Please try again.")
        
        friends = result.friends

        # create dictionary of friends of friends
        friend_of_friends = {}
        for friend in friends:
            friend_friends = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT friends
                    FROM users
                    WHERE id = :friend_id
                    """
                ), [{"friend_id": friend}]
            ).fetchone()
            
            if friend_friends:
                for ff in friend_friends.friends:
                    if ff not in friends and ff != user_id:
                        if ff not in friend_of_friends:
                            friend_of_friends[ff] = 1
                        else:
                            friend_of_friends[ff] += 1
        # sort by number of mutual friends
        suggested_friends = sorted([(user_id, count) for user_id, count in friend_of_friends.items() if count >= 3], key=lambda x: x[1], reverse=True)
        # return usernames of suggested friends


        suggested_usernames = []
        for friend in suggested_friends:
            friend_usernames = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT username
                    FROM users
                    WHERE id = :friend_id
                    """
                ), [{"friend_id": friend[0]}]
            ).scalar_one()

            suggested_usernames.append(Username(username=friend_usernames))



        if not suggested_usernames:
            raise HTTPException(status_code=404, detail="No suggested friends found. Please try again.")
        return suggested_usernames
