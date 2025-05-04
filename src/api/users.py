from dataclasses import dataclass
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List

import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth.get_api_key)],
)

# username - must be alphanumeric, 3-20 characters long, and start with a letter
class Username(BaseModel): 
    username: str = Field(..., min_length=3, max_length=20
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, s: str) -> str:
        if not s.isalnum() or not s[0].isalpha():
            raise ValueError("Username must be alphanumeric and start with a letter.")
        return s
    
    
# create user
@router.post("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def create_new_user(username: str):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO users (username)
                VALUES (:username)

                """
            ), [{"username": username}]
        )
