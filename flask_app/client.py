# TODO: Use client.py to parse the JSON for the game name, game cover, and # downloads. 
    # We will use this for the game functionality
    # Organize the name, cover, and # downloads for each game as a tuple. Put these tuples in an array 

import requests

# class Game(object):
#     def __init__(self, omdb_json, detailed=False) -> None:
#         if detailed:
#             self.name = omdb_json["results"]["name"]
#             self.rating = omdb_json["results"]["rating"]
#             self.image = omdb_json["results"]["background_image"]
#             self.downloads = omdb_json["results"]["added"]

class GameClient(object):
    def __init__(self,) -> None:
        self.sess = requests.Session()
        self.base_url = f"https://api.rawg.io/api/games?key=ae19bf1807254a92af216b11d467792b"

    def get_game_list(self):
        games = []
        resp = self.sess.get(f'{self.base_url}')
        # return resp.json()['results']
        for game_dict in resp.json()['results']:
            tup = (game_dict["name"],game_dict["rating"],game_dict["added"],game_dict["background_image"])
            games.append(tup)
        return games

if __name__ == '__main__':
    client = GameClient()
    l = client.get_game_list()
    print(l)