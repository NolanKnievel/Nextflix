# API Specification for Nextflix Site

## 1. Media

### 1.1. Search Media - `/media?media_name=<media_name>&media_type=<media_type>` (GET)

Retrieve a list of media that match search parameters. Can search by media name and type.

**Response**:
```json
[
  {
    "id": "integer", /* Greater than 0 */
    "media_name": "string"
  },
  {
    ...
  }
]
```

### 1.2. View Media - `/media/{media_title}` (GET)

Retrieve info about a piece of media, including title, director, and rating.

**Response**:
```json
{
  "id": "integer", /* Greater than 0 */
  "name": "string",
  "average_rating": "integer", /* Between 1 and 5 */
  "director": "string" /* Optional, may be null */
}
```

### 1.3. Post Media - `/media` (POST)

Add a media to the site that does not exist. Users provide title, director, and media type.

**Request**:
```json
{
  "title": "string",
  "director": "string",
  "media_type": "string" /* can be either show or movie */
}
```

**Response**:
```json
{
  "success": "boolean"
}
```

### 1.4. Reviewing Media - `/media/{media_title}/reviews/` (POST)

Users can post a review for an existing media.

**Request**:
```json
{
  "username": "string",
  "rating": "integer", /* must be between 1 and 5 inclusive */
  "review": "string"
}
```

**Response**:
```json
{
  "success": "boolean"
}
```

### 1.5. View Reviews - `/media/{media_title}/reviews` (GET)

Retrieve reviews about a specified piece of media.

**Response**:
```json
[
  {
    "username": "string",
    "rating": "integer", /* must be between 1 and 5 inclusive */
    "review": "string"
  },
  {
    ...
  }
]
```

---

## 2. Users

### 2.1. Posting to Watchlist - `/users/{username}/watchlist` (POST)

Users can add existing media to their watchlist. If media does not exist on the site, users are prompted to post the media to the site.

**Request**:
```json
{
  "title": "string",
  "director": "string",
  "media_type": "string",
  "is_watched": false
}
```

**Response**:
```json
{
  "success": "boolean"
}
```

### 2.2. Mark as Watched - `/users/{username}/watchlist/{media_name}` (PATCH)

Update the watchlist to mark a movie as viewed.

**Request**:
```json
{
  "is_viewed": true
}
```

**Response**:
```json
{
  "success": "boolean",
  "watched": {
    "title": "string",
    "director": "string",
    "media_type": "string",
    "is_watched": true
  }
}
```

### 2.3. Get Watchlist - `/users/{username}/watchlist` (GET)

Returns the watchlist of a specified user.

**Response**:
```json
{
  "username": "string",
  "results": [
    {
      "id": "integer", /* Greater than 0 */
      "name": "string",
      "average_rating": "integer", /* Between 1 and 5 */
      "director": "string" /* Optional, may be null */
    }
  ]
}
```

### 2.4. Searching Users - `/users?username=<username>` (GET)

Retrieve a list of users that match search parameters.

**Response**:
```json
[
  {
    "username": "string"
  },
  {
    ...
  }
]
```

### 2.5. View User - `/users/{username}` (GET)

**Response**:
```json
{
  "username": "string",
  "date_joined": "Date",
  "size_of_watchlist": "integer"
}
```

### 2.6. Friend User - `/users/{your_username}/friends` (POST)

Add another user to a given user’s friends list.

**Response**:
```json
{
  "friend_username": "string",
  "success": "boolean"
}
```

---

## 3. Example Flows

### 3.1. User wants to find a new movie to watch/review

1. Look for a new movie by calling: **Search Media**  
   `GET /media?media_type=film`

2. Look up the reviews for a movie before watching by calling: **View Media**  
   `GET /media/<movie_title>/reviews`

3. After checking the reviews, add movie to personal watchlist: **Posting to Watchlist**  
   `POST /users/<username>/watchlist`

4. After watching the movie, mark the movie as watched on your watchlist: **Mark as Watched**  
   `PATCH /users/<username>/watchlist/<movie_name>`

5. After watching the movie, upload a review: **Reviewing Media**  
   `POST /media/<movie_title>/reviews/`

---

### 3.2. User wants to keep a personal watchlist of movies to find them later easily

1. Search for new movies: **Search Media**  
   `GET /media?media_type=movie`

2. View reviews of the search result: **View Media**  
   `GET /media/<movie_title>/reviews`

3. Add a movie to the watchlist: **Posting to Watchlist**  
   `POST /users/<username>/watchlist`

4. Remove a movie from the watchlist by marking it as watched: **Mark as Watched**  
   `PATCH /users/<username>/watchlist/<movie_title>`

---

### 3.3. User wants to follow another user to keep up with their reviews

1. Search users to follow: **Searching Users**  
   `GET /users?username=<username>`

2. Send a friend request: **Friend User**  
   `POST /users/<your_username>/friends`

3. After the friend request is accepted, view their watchlist: **Get Watchlist**  
   `GET /users/<friend_username>/watchlist`
