# Add Media To Watchlist

## Workflow
    As a casual watcher, I want to keep a personal watchlist of shows/movies so I can easily find them later.

### Request
    *curl -X 'POST' \
    'http://127.0.0.1:3000/users/nolan/watchlist?title=Avatar&have_watched=false' \
    -H 'accept: */*' \
    -H 'access_token: brat' \
    -d ''*

### Response
    *204 NO CONTENT*


# Get Watchlist
## Workflow
    As a mom, I want to stay on track of all the movies my kids want to watch so I don't forget throughout my busy day.


### Request
    *curl -X 'GET' \
    'http://127.0.0.1:3000/users/nolan/watchlist?only_watched_media=false' \
    -H 'accept: application/json' \
    -H 'access_token: brat'*


### Response
    *[
    {
        "media_id": 259,
        "title": "Avatar",
        "director": "ME",
        "have_watched": true
    }
    ]*



# Mark As Watched

## Workflow
    As a mom, I want to stay on track of all the movies my kids want to watch so I don't forget throughout my busy day.


### Request
    *curl -X 'PATCH' \
    'http://127.0.0.1:3000/users/nolan/watchlist/Avatar' \
    -H 'accept: */*' \
    -H 'access_token: brat'*

### Response
    *204 NO CONTENT*