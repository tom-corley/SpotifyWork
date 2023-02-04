import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import os
import math
import base64
from PIL import Image, ImageDraw, ImageOps
import io
import random

# User Class - Used to interact with the spotify API
class User:
    def __init__(self):
        # Fetching Environment Variables
        self.cid = str(os.environ["CLIENT_ID"])
        self.secret = str(os.environ["CLIENT_SECRET"])
        self.URI = str(os.environ["REDIRECT_URI"])
        # Logging in user, and setting scopes
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            scope=[
                'playlist-modify-public', 
                'user-top-read', 
                'user-read-currently-playing', 
                'user-library-modify', 
                'ugc-image-upload',
                'streaming',
                'user-read-playback-state',
                'user-follow-modify',
                'user-follow-read',
                'user-read-playback-position',
                'user-library-read',
                'user-read-recently-played'],
            # Authentication details stored as environment vars for security
            client_id= self.cid,\
            client_secret= self.secret ,\
            redirect_uri= self.URI,))
        self.id = self.sp.me()['id']

    def random_image(self):
        # Create an image with random size and color
        width, height = (100, 100)
        image = Image.new('RGB', (width, height))
        pixels = image.load()

        # Assign a random color to each pixel
        for i in range(width):
            for j in range(height):
                pixels[i, j] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # Generate a random border color
        border_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # Add a border to the image
        image = ImageOps.expand(image, border=5, fill=border_color)

        # Create the smiley face
        draw = ImageDraw.Draw(image)
        center_x = width // 2
        center_y = height // 2

        # Draw two black dots for the eyes
        draw.ellipse((center_x - 20, center_y - 20, center_x - 10, center_y - 10), fill=(0, 0, 0))
        draw.ellipse((center_x + 10, center_y - 20, center_x + 20, center_y - 10), fill=(0, 0, 0))

        # Draw the smile
        draw.arc((center_x - 20, center_y - 5, center_x + 20, center_y + 20), 0, 180, fill=(0, 0, 0))




        # Convert the image to a byte array
        with io.BytesIO() as buffer:
            image.save(buffer, format="JPEG")
            byte_array = buffer.getvalue()

        # Encode the byte array in base64
        base64_encoded = base64.b64encode(byte_array).decode('utf-8')

        # Output the base64 string
        return base64_encoded

    # Gets artist id for a given artist passed as a string, useful for other functions
    def get_artist_id(self, search_input):
        results = self.sp.search(
            q="artist: "+search_input,
            type = 'artist'
        )
        top_result = results["artists"]["items"][0]
        return top_result['id']

    # Gets song id for a given song passed as a string, useful for other functions
    def get_track_id(self, search_input):
        results = self.sp.search(
            q="track: "+search_input,
            type = 'track'
        )
        top_result = results["tracks"]["items"][0]
        return top_result["id"]

    # Returns an array of track ids for each track on an album
    def get_tracks_from_album(self, album_id):
        results = self.sp.album(album_id)
        tracks = [track["id"] for track in results["tracks"]["items"]]
        return tracks
    
    # Creates a playlist given an array of track ids and a name as a string
    def create_playlist(self,tracks,name):
        # Creates an empty playlist, saves playlist id for later
        new_playlist_id = \
            self.sp.user_playlist_create(self.id, name)['id']
        self.sp.playlist_upload_cover_image(new_playlist_id, self.random_image())

        # The API can only add 100 tracks at a time
        # If there are > 100 to be added, done in several steps
        if len(tracks) == None:
            return
        if len(tracks) < 100:
            self.sp.user_playlist_add_tracks(
            user=self.id,
            playlist_id=new_playlist_id,
            tracks=tracks)
        else:
            num_of_adds = math.ceil(len(tracks) / 100)
            for i in range(num_of_adds):
                if i == num_of_adds - 1:
                    self.sp.user_playlist_add_tracks(
                    user=self.id,
                    playlist_id=new_playlist_id,
                    tracks=tracks[i*100:])
                else:
                    self.sp.user_playlist_add_tracks(
                    user=self.id,
                    playlist_id=new_playlist_id,
                    tracks=tracks[i*100:(i+1)*100])
    
    # Creates a playlist of the top 10 tracks given an artist
    def create_artist_playlist(self, name):
        artist_id = self.get_artist_id(name)
        artist_name = self.sp.artist(artist_id=artist_id)['name']
        artist_tracks = self.sp.artist_top_tracks(artist_id)
        track_ids = [i['id'] for i in artist_tracks['tracks']]
        self.create_playlist(tracks = track_ids, name = artist_name+" top tracks")

    # Creates artist playlists for each of the users top 50 artists
    def artist_playlist_for_top50_artists(self):
        results = self.sp.current_user_top_artists(time_range='long_term', limit=50)
        top_50 = [i for i in results["items"]]
        for i in top_50:
            self.create_artist_playlist(i["name"])

    # Creates playlist of users top-50 listened to songs
    def playlist_top50_alltime(self):
        results = self.sp.current_user_top_tracks(time_range='long_term', limit=50)
        top_50 = [i["id"] for i in results["items"]]
        self.create_playlist(tracks = top_50, name = "All-time top 50")

    # Deletes newest Playlist
    def delete_newest_playlist(self):
        playlists = self.sp.user_playlists(user=self.id)
        id = playlists["items"][0]['id']
        self.sp.user_playlist_unfollow(user=self.id, playlist_id=id) 

    # Prints track which is currently playing
    def currently_playing(self):
        try: 
            results = self.sp.current_user_playing_track()
            name = results["item"]["name"]
            artist = results["item"]["artists"][0]["name"]
            print("Currently Playing: "+name+" - "+artist)
        except Exception:
            print("No track currently playing")

    # Makes playlist of short-term top 50 songs
    def short_50(self):
        results = self.sp.current_user_top_tracks(time_range='short_term', limit=50)
        top_50 = [i["id"] for i in results["items"]]
        self.create_playlist(tracks = top_50, name = "Recent Top 50 (coded)")
    
    # Prints top 50 artists to terminal
    def top_artists(self):
        results = self.sp.current_user_top_artists(time_range='long_term', limit=25)
        top_50 = [i["name"] for i in results["items"]]
        for i, artist in enumerate(top_50):
            print(f"{i+1}. {artist}")
            
def write_to_json(input):
        json_input = json.dumps(input,indent=4)
        with open("test.json","w+") as f:
            f.write(json_input)

def main():
        me = User()
        me.currently_playing()
        #me.playlist_top50_alltime()
        #me.top_artists()
        me.artist_playlist_for_top50_artists()
        #for i in range(8):
            #me.delete_newest_playlist()

if __name__ == "__main__":
    main()


    