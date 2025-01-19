from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

import json

class YouTubePlaylistFetcher:
    def __init__(self, client_secrets_file):
        """
        Initialize the YouTube API client
        
        Args:
            client_secrets_file (str): Path to client secrets JSON file from Google Cloud Console
        """
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.readonly', 'https://www.googleapis.com/auth/youtube']
        self.client_secrets_file = client_secrets_file
        self.youtube = None
    
    def authenticate(self):
        """Authenticate with YouTube API using OAuth 2.0"""
        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, self.SCOPES)
        credentials = flow.run_local_server(port=0)
        self.youtube = build('youtube', 'v3', credentials=credentials)
    
    def get_playlists(self, channel_id=None):
        """
        Fetch all playlists for a channel. If no channel_id is provided,
        fetches playlists for authenticated user.
        
        Args:
            channel_id (str, optional): YouTube channel ID
            
        Returns:
            list: List of playlist information dictionaries
        """
        if not self.youtube:
            raise Exception("Please authenticate first by calling authenticate()")
            
        playlists = []
        next_page_token = None
        
        # import pdb
        # pdb.set_trace()
        while True:
            
            request = self.youtube.playlists().list(
                part='snippet,contentDetails',
                channelId=channel_id,
                mine=True if not channel_id else None,
                maxResults=50,
                pageToken=next_page_token
            )
            
            response = request.execute()
            
            for playlist in response['items']:
                playlist_info = {
                    'id': playlist['id'],
                    'title': playlist['snippet']['title'],
                    'description': playlist['snippet']['description'],
                    'itemCount': playlist['contentDetails']['itemCount'],
                    'publishedAt': playlist['snippet']['publishedAt']
                }
                playlists.append(playlist_info)
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
                
        return playlists
    
    def get_playlist_items(self, playlist_id):
        """
        Fetch all videos in a specific playlist
        
        Args:
            playlist_id (str): YouTube playlist ID
            
        Returns:
            list: List of video information dictionaries
        """
        if not self.youtube:
            raise Exception("Please authenticate first by calling authenticate()")
            
        videos = []
        next_page_token = None
        
        while True:
            request = self.youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            
            response = request.execute()
            
            for item in response['items']:
                video_info = {
                    'videoId': item['contentDetails']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'position': item['snippet']['position'],
                    'publishedAt': item['snippet']['publishedAt']
                }
                videos.append(video_info)
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
                
        return videos

    def get_channel_id_from_username(self, username):
        """
        Get channel ID from a YouTube username
        
        Args:
            username (str): YouTube username or channel name
            
        Returns:
            str: Channel ID if found, None otherwise
        """
        try:
            response = self.youtube.channels().list(
                part='id',
                forUsername=username
            ).execute()
            
            if response.get('items'):
                return response['items'][0]['id']
            return None
            
        except HttpError as e:
            print(f"Error fetching channel ID: {str(e)}")
            return None


# Example usage
if __name__ == "__main__":
    # Initialize and authenticate
    fetcher = YouTubePlaylistFetcher('/home/akshay/code/mplayer/client_secret_98724144011-mkds6bvbhc1ta4va8hu8hqenqjead8k1.apps.googleusercontent.com.json')
    fetcher.authenticate()
    
    # Get authenticated user's playlists
    my_playlists = fetcher.get_playlists()
    print("My Playlists:", json.dumps(my_playlists, indent=2))
    
    # Get playlists for a specific channel
    #channel_playlists = fetcher.get_playlists(channel_id='CHANNEL_ID_HERE')
    #print("Channel Playlists:", json.dumps(channel_playlists, indent=2))
    
    # Get videos from a specific playlist
    for playlist in my_playlists:
        playlist_videos = fetcher.get_playlist_items(playlist['id'])
        print("Playlist Videos:", json.dumps(playlist_videos, indent=2))