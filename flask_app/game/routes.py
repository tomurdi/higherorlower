from flask import Blueprint, render_template
import base64, io
from io import BytesIO
from flask_login import current_user
from ..models import User
from ..client import GameClient

game = Blueprint('game', __name__)
game_client = GameClient()

@game.route('/play')
def play():
    return render_template('game.html', 
                           game_list=sorted(game_client.get_game_list(),key=lambda x:x[3]))

@game.route('/leaderboard')
def leaderboard():
    # we need a way to iterate through each user, grabbing their highest score
    # we then can sort (in reverse) the scores and then pass it into the leaderboard html
    # the reason why we should do reverse is when we iterate through the list in the template,
    # it outputs the highest score first, and so on
    all_users = User.objects()
    user_scores = []
    for user in all_users:
        user_scores.append((user.username,user.highScore))
    user_scores.sort(key= lambda x: x[1])
    return render_template('leaderboard.html',scores=user_scores)

