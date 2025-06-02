import sqlalchemy
from src.api import auth
from src import database as db
from depopulate import depopulate
import random

SIZE = 1000

def populate():
    """
    Populate the database with 1 million rows
    """
    depopulate()  

    with db.engine.begin() as connection:
        # create users
        for i in range(1, SIZE+1):
            username = f'user{i}'
            connection.execute(
                sqlalchemy.text(
                    "INSERT INTO users (username) VALUES (:username)"
                ),
                {"username": username}
            )

        # add friends to users
        min_id = connection.execute(
            sqlalchemy.text("SELECT MIN(id) FROM users")
        ).scalar()
        max_id = connection.execute(
            sqlalchemy.text("SELECT MAX(id) FROM users")
        ).scalar()

        for i in range(min_id, max_id + 1):
            # generate 0 to 10 random friends for each user
            friends = []
            for _ in range(random.randint(0, 10)):
                friends.append(random.randint(min_id, max_id))
            
            friends = list(set(friends))  # remove duplicates
            if i in friends:  # remove self friending
                friends.remove(i)

            if friends:
                connection.execute(
                    sqlalchemy.text(
                        f"""
                        UPDATE users SET friends = :friends WHERE id = :id
                        """
                    ),
                    {"friends": friends, "id": i}
                )
            

        # create media
        for i in range(1, 101):
            title = f'show{i}'
            director = f'director{i}'
            connection.execute(
                sqlalchemy.text(
                    "INSERT INTO media (title, media_type, director) VALUES (:title, 'show', :director)"
                ),
                {"title": title, "director": director}
            )
        for i in range(101, 201):
            title = f'movie{i}'
            director = f'director{i}'
            connection.execute(
                sqlalchemy.text(
                    "INSERT INTO media (title, media_type, director) VALUES (:title, 'movie', :director)"
                ),
                {"title": title, "director": director}
            )
        
        # create tv shows
        show_min_id = connection.execute(
            sqlalchemy.text("SELECT MIN(media_id) FROM media WHERE media_type = 'show'")
        ).scalar()
        show_max_id = connection.execute(
            sqlalchemy.text("SELECT MAX(media_id) FROM media WHERE media_type = 'show'")
        ).scalar()
        movie_min_id = connection.execute(
            sqlalchemy.text("SELECT MIN(media_id) FROM media WHERE media_type = 'movie'")
        ).scalar()
        movie_max_id = connection.execute(
            sqlalchemy.text("SELECT MAX(media_id) FROM media WHERE media_type = 'movie'")
        ).scalar()
        

        for i in range(show_min_id, show_max_id + 1):
            total_episodes = random.randint(1, 50)
            total_seasons = random.randint(1, 10)
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO tv_shows (media_id, total_episodes, total_seasons)
                    VALUES (:media_id, :total_episodes, :total_seasons)
                    """
                ),
                {"media_id": i, "total_episodes": total_episodes, "total_seasons": total_seasons}
            )
        for i in range(movie_min_id, movie_max_id + 1):
            length = random.randint(30, 230)
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO movies (media_id, length)
                    VALUES (:media_id, :length)
                    """
                ), 
                {"media_id": i, "length": length}
            )
        
        
        # create reviews
        for i in range(min_id, max_id + 1):
            for j in range(random.randint(0, 10)):
                media_id = random.randint(show_min_id, movie_max_id)
                rating = random.randint(1, 5)
                review_text = f'Review {j+1} for user {i} on media {media_id}'
                connection.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO reviews (user_id, media_id, rating, review)
                        VALUES (:user_id, :media_id, :rating, :review)
                        ON CONFLICT DO NOTHING -- to avoid duplicate reviews
                        """
                    ),
                    {"user_id": i, "media_id": media_id, "rating": rating, "review": review_text}
                )
        # create watchlists
        for i in range(min_id, max_id + 1):
            for j in range(random.randint(0, 10)):
                media_id = random.randint(show_min_id, movie_max_id)
                have_watched = random.choice([True, False])

                connection.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO watchlists (user_id, media_id, have_watched)
                        VALUES (:user_id, :media_id, :have_watched)
                        ON CONFLICT DO NOTHING -- to avoid duplicate watchlist entries
                        """
                    ),
                    {"user_id": i, "media_id": media_id, "have_watched": have_watched}
                )

if __name__ == "__main__":
    populate()
    print("Database has been populated")