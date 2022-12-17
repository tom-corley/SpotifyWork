# Title TBC

A Python application to beform basic operations on a users spotify account programmatically, automating playlist creation, as well as implementing spotifys reccomendation algorithm, to allow users to discover new music.

## Documentation

### *User* class
- `__init__`: a constructor, uses client_id, client_secret and a redirect uri to peform OAuth2 authentication on the spotify web API, these should be stored securely as enviroment variables.

- `get_artist_id`: fetches artist id from the API for a inputted artist name.

- `get_track_id`: fetches track id form the API for an inputted song.

- `get_tracks_from_album`: returns an array of track ids for a given album id.

- `create_playlist`: creates a playlist on the users account, inputs are playlist name and an array of track ids, to be added to the playlist (can be empty).

- `create_artist_playlist`: creates a playlist of an artists top 10 songs.

- `artist_playlist_for_top50_artists`: creates a playlist of 500 tracks consisting of the top 10 tracks from each of the users top 50 artists.

- `playlist_top50_alltime`: creates a playlist of users all time top 50 tracks.

- `delete_newest_playlist`: deletes the newest playlist on the users profile.

- `currently_playing`: prints the currently playing song to the terminal.

- `short_50`: creates a playlist of the users recent top 50 tracks.

- `top_artists`: prints each of the users top 50 artists to the terminal.


