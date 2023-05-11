import openai
import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import json
import datetime
import requests
from config3 import OPEN_API_KEY, PLAYLIST_ENGINE, DJ_SYSTEM, WEATHER_API_KEY, SPOTIFY_CID, SPOTIFY_SECRET, SPOTIFY_USER, QUESTION0, QUESTION1

openai.api_key = OPEN_API_KEY

# sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

scope = "playlist-modify-public user-modify-playback-state user-read-playback-state"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

current_datetime = datetime.datetime.now()

def get_desire():

	desire = input(QUESTION0)
	length = input(QUESTION1)
	
	return desire, length
	

def process_prompt(engine, prompt, system, m_tokens):

	response = openai.ChatCompletion.create(
		model=engine,
		messages=[
			{"role": "system", "content": system},
			{"role": "user", "content": prompt},
			],
			max_tokens=m_tokens,
			n=1,
			stop=None,
			temperature=0.7,
		)
	
	answer = response['choices'][0]['message']['content'].strip()
	
	return answer
	

def get_playlist(desire, length):
	
	system = ""
	
	time = current_datetime.strftime("%-I:%M %p on a %A")
	
	prompt = f"Generate a {length} song playlist based on the following prompt: '{desire}'. Give the playlist a clever title. Format your output as 'Title:[Title] followed by a JSON list with keys for artist and song."

	answer = process_prompt(PLAYLIST_ENGINE, prompt, system, 2000)
	lines = answer.splitlines()
	title_line = lines[0]
	title_prefix = "Title: "
	playlist_title = title_line[len(title_prefix):]
	json_part = "\n".join(lines[1:])
	playlist_tracks = json.loads(json_part)
	return playlist_title, playlist_tracks

def build_playlist(playlist_title, tracks):
	playlist = sp.user_playlist_create(user=SPOTIFY_USER, name=playlist_title)
	playlist_id = playlist['id']
	playlist_uri = 'spotify:playlist:' + playlist_id
	
	for track in tracks:
		print(f"{track['song']} by {track['artist']}")
		query = f"artist:{track['artist']} track:{track['song']}"
		results = sp.search(q=query, type='track')
		try:
			track_id = results['tracks']['items'][0]['id']
			sp.user_playlist_add_tracks(user=SPOTIFY_USER, playlist_id=playlist_id, tracks=[track_id])
		except IndexError:
			print("Track Not Found")
			continue
		
	return playlist_uri

def play_playlist(playlist_uri):
	
	devices = sp.devices()
	device_id = devices['devices'][0]['id']
	sp.start_playback(context_uri=playlist_uri, device_id=device_id)
	
def anylist():
	
	desire, length = get_desire()
	playlist_title, playlist_tracks = get_playlist(desire, length)
	playlist_uri = build_playlist(playlist_title, playlist_tracks)
	play_playlist(playlist_uri)
	print(f"Enjoy your playlist, {playlist_title}")
	
def main():
	anylist()

if __name__ == "__main__":
	main()