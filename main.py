from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = "http://example.com"

date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
PLAYLIST_NAME = f"{date} Billboard 100"

response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}")
website_html = response.text

soup = BeautifulSoup(website_html, "html.parser")
songs = soup.find_all("h3", class_="c-title")
song_text = [name.text.strip() for name in songs]


# removes last 6 items of list
del song_text[0:7]
# Slices every 4th item
final_list = song_text[0:400:4]
# Spotipy Authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope="playlist-modify-private"))


id = sp.current_user()["id"]

song_uris = []
year = date.split("-")[0]  # gives us first 4 numbers

for song in final_list:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    # print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

playlist = sp.user_playlist_create(id, PLAYLIST_NAME, public=False, collaborative=False, description=f"Top 100 Billboard tracks for {date}.")
playlist_id = playlist["id"]

sp.playlist_add_items(playlist_id, song_uris, position=None)
