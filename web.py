import json, os, sys
import spotipy, requests

from spotipy.oauth2 import SpotifyOAuth

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError 
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client.client import flow_from_clientsecrets

from s import s_token, s_id, client_id, yt_key

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl'] 
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
  

def get_songs():

    end = 'https://api.spotify.com/v1/users/me/tracks'

    parameters = {'market': 'ES', 'limit': 50, 'offset':50}

    r = requests.get(end, params = parameters, headers={'Authorization': 'Bearer '+s_token})

    songs = {}

    for i in (r.json()['items']):
        artist = ''
        for v in i['track']['artists']:
            artist += v['name'] + ' '
        songs[i['track']['name']]= artist

    return songs

#api key needed
youtube_object = build(API_SERVICE_NAME, API_VERSION, developerKey = yt_key) 

def get_video_id(songs):

    video_id = []

    for title, artist in songs.items():

        search_keyword = youtube_object.search().list(q = title + artist, part = 'id, snippet', maxResults = 1).execute() 
        results = search_keyword.get('items', [])
          
        for i in results: 
            video_id.append(i['id']['videoId'])
        
    return video_id


def get_authenticated_service(): 
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES) 
    credentials = flow.run_console() 
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials) 


def add_to_playlist(video_ids):
    p_id = input('Enter playlist id: ')
    
    p_id = 'PLBUXQsEUG0eKsD1DUV2T1tRwjd2BpkseP'

    youtube = get_authenticated_service()
    batch = youtube.new_batch_http_request()

    for video_id in video_ids:
        batch.add(youtube.playlistItems().insert(
            part="snippet",
            body={
            "snippet": {
                "playlistId": p_id,
                "position": 0,
                "resourceId": {
                "kind": "youtube#video",
                "videoId": video_id
                }
            }
        }))
    batch.execute()


if __name__=='__main__':
    songs = get_songs()
    v_ids = get_video_id(songs)
    add_to_playlist(v_ids)