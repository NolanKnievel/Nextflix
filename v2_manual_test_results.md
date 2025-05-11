# Add Media To Watchlist

## Workflow
    ### 2.1. Posting to Watchlist - `/users/{username}/watchlist` (POST)

    Users can add existing media to their watchlist. If media does not exist on the site, users are prompted to post the media to the site.

    **Request**:
    ```json
    {
    "title": "string",
    "have_watched": false
    }
    ```

    **Response**:
    ```json
    HTTP_204_NO_CONTENT
    ```



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
    ### 2.3. Get Watchlist - `/users/{username}/watchlist` (GET)

    Returns the watchlist of a specified user.

    **Response**:
    ```json
    {
    [
        {
        "id": "integer", /* Greater than 0 */
        "title": "string",
        "average_rating": "integer", /* Between 1 and 5 */
        "director": "string" /* Optional, may be null */
        }
    ]
    }
    ```


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
    ### 2.2. Mark as Watched - `/users/{username}/watchlist/{media_title}` (PATCH)

    Update the watchlist to mark a movie as viewed.

    **Request**:
    ```json
    {}
    ```

    **Response**:
    ```json
    HTTP_204_NO_CONTENT
    ```


### Request
    *curl -X 'PATCH' \
    'http://127.0.0.1:3000/users/nolan/watchlist/Avatar' \
    -H 'accept: */*' \
    -H 'access_token: brat'*

### Response
    *204 NO CONTENT*