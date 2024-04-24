# TODO: Use client.py to parse the JSON for the game name, game cover, and # downloads. 
    # We will use this for the game functionality
    # Organize the name, cover, and # downloads for each game as a tuple. Put these tuples in an array 

import requests

class Game(object):
    def __init__(self, omdb_json, detailed=False) -> None:
        if detailed:
            self.name = omdb_json["name"]
            self.rating = omdb_json["rating"]
            self.image = omdb_json["background image"]
            self.downloads = omdb_json["added"]

class GameClient(object):
    def __init__(self,api_key) -> None:
        self.sess = requests.Session()
        self.base_url = f"https://api.rawg.io/api/games?key={api_key}"

    