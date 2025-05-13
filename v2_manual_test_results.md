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

# View Reviews

## Workflow

    As a teenager, I care about what others think about a movie before I decide if I want to watch it or not.

### Request

    *curl -X 'GET' \
    'http://127.0.0.1:3000/media/Thunderbolts%2A/reviews' \
    -H 'accept: application/json' \
    -H 'access_token: brat'*

### Response

    *[
    {
        "username": "bob",
        "review": "it was cool",
        "rating": 4
    },
    {
        "username": "yelena",
        "review": "it was sick",
        "rating": 5
    },
    {
        "username": "ghost",
        "review": "i hated it",
        "rating": 1
    }
    ]*

# Media Search

## Workflow

    As a teacher, I want to find a film that is educational and entertaining to show my students.

### Request

    *curl -X 'GET' \
    'http://127.0.0.1:3000/media/search?media_name=Thunderbolts&media_type=movie' \
    -H 'accept: application/json' \
    -H 'access_token: brat'*

### Response

    *[
    "Thunderbolts*"
    ]*

# View Media

## Workflow

    As a teacher, I want to find a film that is educational and entertaining to show my students.

### Request

    *curl -X 'GET' \
    'http://127.0.0.1:3000/media/Thunderbolts%2A' \
    -H 'accept: application/json' \
    -H 'access_token: brat'*

### Response

    *{
      "id": 2,
      "title": "Thunderbolts*",
      "average_rating": 3.3333333333333335,
      "director": "Jake Schreier"
    }*

# Add Friend

## Workflow

    As a teen, I want to add my friends to see what they have been watching.

### Request

    curl -X 'POST' \
        'http://127.0.0.1:3000/users/nickc/friends' \
        -H 'accept: */*' \
        -H 'access_token: brat' \
         -H 'Content-Type: application/json' \
        -d '{
        "username": "nick"
        }'

### Response

    *204 NO CONTENT*

# View User

## Workflow

    As a teenager trying to find a friend, I want to see if my friend has an account

### Request

    curl -X 'GET' \
        'http://127.0.0.1:3000/users/nickc' \
        -H 'accept: application/json' \
        -H 'access_token: brat'

### Response

    {
    "username": {
    "username": "nickc"
    },
    "date_joined": "2025-05-12 00:01:05.755006",
    "size_of_watchlist": 1
    }

# Search Users

## Worflow

    As a curious individual, I want to see if people have a similar username to me

## Request

    curl -X 'GET' \
        'http://127.0.0.1:3000/users/search?username=nick' \
        -H 'accept: application/json' \
        -H 'access_token: brat'

## Response

    [
        {
        "username": "nick"
        },
        {
        "username": "nickchau"
        },
        {
        "username": "nickchauu"
        },
        {
        "username": "nickc"
        }
    ]
