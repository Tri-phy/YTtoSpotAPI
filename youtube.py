from json import dumps
import requests
from ytmusicapi import YTMusic

class CreatePlaylist:

    def __init__(self):
        self.yt_playlist = YTMusic.get_user_playlists()
        self.migrate_playlists = {}

    #Gets all playlist on youtube music along with song and information in text
    def get_playlist(self):
        for playlist in self.yt_playlist:
            playlist_dic = YTMusic.get_playlist(playlist['playlistId'])
            self.migrate_playlists.append({
                'name': playlist_dic['title'],
                'description': playlist_dic['description'],
                'tracks': playlist_dic['tracks'],
                'spotify_page': []
            })

    #add songs to a playlist via a search on spotify    
    def transfer_playlist(self):
        for dic in self.migrate_playlists:
            for song in dic['track']:
                self.migrate_playlists['spotify_page'].append(self.find_song(song['title'], song['artist'][0]['name']))
        
        for dic in self.migrate_playlists:
            self.create_playlist(dic['name'], dic['description'])
            self.add_songs_to_playlist(dic['spotify_page'])

    def create_playlist(self, name, description):
        request_body = dumps({
            "name": name,
            "description": description,
            "public": True
        })
        query = "https://api.spotify.com/v1/users/{}/playlists".format()
        response = requests.post(
            query,
            data = request_body,
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(),
            })
        response_json = response.json()
        return response_json["id"]

    # Given song name and artist find the song via a query and return the url
    def find_song(self, song_name, artist):
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20&include_external=audio".format(
            song_name, artist
        )
        response = requests.get(
            query,
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(),
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]
        return songs[0]["url"]

    def add_songs_to_playlist(self, tracks):
        song_url = []
        for song in tracks:
            song_url.append(song)
        playlistId = self.create_playlist()
        request_data = dumps(song_url)
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlistId)
        response = requests.post(
            query,
            data = request_data,
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(),
            }            
        )
        return response.json()

if __name__ == '__main__':
    pass

