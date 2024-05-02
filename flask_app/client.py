# TODO: Use client.py to parse the JSON for the game name, game cover, and # downloads. 
    # We will use this for the game functionality
    # Organize the name, cover, and # downloads for each game as a tuple. Put these tuples in an array 

import requests

class GameClient(object):
    def __init__(self,) -> None:
        self.sess = requests.Session()
        self.base_url = f"https://api.rawg.io/api/games?key=ae19bf1807254a92af216b11d467792b"

    def get_game_list(self):
        games = []
        # Update 5 if you want more/less games
        num_pages = 10
        for i in range(1,num_pages):
            resp = self.sess.get(self.base_url, params={'page': i})
            if resp.status_code == 200:
                for game_dict in resp.json()['results']:
                    tup = (game_dict["name"], 
                           game_dict["background_image"], 
                           game_dict["rating"], 
                           game_dict["added"])
                    games.append(tup)
            else:
                print(f"Failed to get data for page {i}, status code: {resp.status_code}")
        return games

if __name__ == '__main__':
    client = GameClient()
    l = client.get_game_list()
    print(l)