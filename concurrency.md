



### **CASE 1: Lost update phenomenon in post_show and post_film**
If two updates are made simultaneously to post the same media. A lost update phenomenon could occur, resulting in duplicate data in the media table.

**Example: Two attempts to insert the movie 'Dune' are made at the same time **
![Screenshot 2025-05-27 212641](https://github.com/user-attachments/assets/118873f5-5c26-4d34-9752-ecec2bef7e36)


### SOLUTION: Use an exclusive lock when reading from the media table

"""
BEGIN;

SELECT media_id

FROM media

WHERE 

title = :title AND

director = :director AND

media_type = 'movie'

FOR UPDATE;
"""

*conditional statement*

"""
INSERT INTO media (media_type,title,director)

VALUES ('movie',:title,:director)

RETURNING media_id

COMMIT;
"""

### **CASE 2: Potential read skew in get_recommendations can lead to inconsistent data**

If one user calls the get_recommendations endpoint while that users' friend alters their watchlist, get_recommendations will return stale data.

**Example: A user edits their watchlist while their friend gets their recommendations**
![Screenshot 2025-05-27 230003](https://github.com/user-attachments/assets/4f1f7901-58d3-41ac-ac32-ae97070a75cb)

### Solution: use serializable isolation level

with db.engine.begin() as connection:
    connection.execute(sqlalchemy.text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))


*** CASE 3: get_suggested_friends could return stale data ***

Similar to the last case, if a user changes adds/removes friends while another user calls the get_suggested_friends, it could lead to an incorrect "friend tree".

** Example: User 1 calls get_suggested_friends, simultaneously- User 2 removes User 3 as a friend**


![Screenshot 2025-05-27 233909](https://github.com/user-attachments/assets/91dc6d9e-a25f-4636-9afe-be1e9d9333bf)

### Solution: Use a shared lock to handle concurrent requests

*in fetch friends* 
        result = connection.execute(
            sqlalchemy.text(
                """
                BEGIN;
                SELECT friends
                FROM users
                WHERE id = :user_id
                FOR SHARE;
                """
            ), [{"user_id": user_id}]
        ).fetchone()




