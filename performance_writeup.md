## Fake Data Modeling
    Data population code can be found at ./populate.py

    To create a million rows, we don't necessarily need a million users in our DB. We opted to create 100,000 users, each user having a random value of 0-10 reviews, friends, and items in their watchlist. With an average of 5 for these random values, we end up with 100,000 rows for users and about 500,000 rows for watchlists and reviews. 

    We'd argue that media won't scale the same as users, because media items are limited by Netflix's catalog. We estimate the posted netflix catalog with 1000 media rows, including 500 rows for shows and 500 rows for films. 


## Endpoint Timing

### Create new user
POST /users/{username}
    username=nolanK5
    32.00ms


### View user
GET /users/{username}
    username=user5000
    18.61ms

### Add to Watchlist
POST /users/{username}/watchlist
    username=user5000, title=show295, have_watched=true
    123.76ms

### Get Watchlist
GET /users/{username}/watchlist
    username=uesr500, only_watched_media=true
    20.06ms

### Mark as Watched
PATCH /users/{username}/watchlist/{media_title}
    username=user500
    media_title=show57
    21.82ms

### Search Users
GET /users/search
    username=nolan
    127.03ms

### Add Friend
POST /users/{username}/friends
    username=user300, username=user400
    26.54ms

### Get Suggested Friends
GET /users/{username}/suggested_friends
    username=user300
    22.32ms

### Search Media
GET /media/search
    media_name = show, media_type=show
    94.01ms

### View Media
GET /media/view
    meida_title=show11
    125.96ms


### Post Film
POST /media/films
    title=testtitle, director=ME, length=120
    25.53ms

### Post Show
POST /media/shows
    title=testtitle, director=ME, seasons=20, episodes=29
    22.08ms


### Review Media
POST /media/{media_title}/reviews
    media_title=show11, username=user7, review=GOOD, rating=3
    26.86ms


### View Reviews
GET /media/{media_title}/reviews
    media_title=show293
    90.06ms


### Get Recommendations
GET /media/{username}/recommendations
    username=user5
    18.95ms



**Of all our routes, the search users route, GET /users/search, took the longest at 127.03ms.**
**The next two slowest were add to watchlist POST /users/{username}/watchlist at 123.76ms and view media GET /media/view at 125.96ms**


## Adding index

### Explained query before: 
    Seq Scan on users  (cost=0.00..3083.00 rows=10 width=9)
    Filter: ((username)::text ~~* '%200%'::text)

    Seq scan - postgres is scanning every row in the users table
    cost= ...3083 - the cost to scan these rows
    rows=10 - how many rows it will return
    width=9 - how many chars in each row


### First index attempt:
    # (created this with alembic)
    op.create_index(
        'idx_users_username',
        'users',
        ['username'],
        unique=False,
        postgresql_using='btree'
    )

### Explain after first attempt:
    Seq Scan on users  (cost=0.00..3083.05 rows=10 width=9)

There is no change, so the index is not applying

### Second index attempt
    To fix this, we altered our query a bit from:
    WHERE username ILIKE :username

    to:
    WHERE LOWER(username) LIKE LOWER(:username)

    We were also wrapping username with '%' on either side, but are now only including this at the end of username. In this way, we can use an index, but can only search based on the start of a username



    CREATE INDEX index_users_username_lower_pattern
    ON users (LOWER(username) varchar_pattern_ops)


### Explain after second attempt:
    Bitmap Heap Scan on users  (cost=13.54..1134.32 rows=500 width=9)

    The second cost value is about 66% lower! This is a marked improvement.

    Running the search on username=nolan, the route now only takes 58.75ms.



