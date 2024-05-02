from flask import Blueprint, render_template, request, session
import base64, io
import random
from io import BytesIO
from flask_login import current_user
from ..models import User
from ..client import GameClient

game = Blueprint('game', __name__)
game_client = GameClient()
global global_current_score
global_current_score = 0

@game.route('/play')
def play(username=None):
    user = User.objects(username=username).first() if username else None
    games_lst = sorted(game_client.get_game_list(),key=lambda x:x[3])
    selected_games = random.sample(games_lst, 2)
    session['selected_games'] = selected_games
    return render_template('game.html',user=user,game_list=selected_games,game_client=game_client,score=global_current_score)

@game.route('/process_selection', methods=['POST'])
def process_selection():
    selected_game_name = request.form.get('selected_game')
    
    # Retrieve the selected games from the session or another data source
    selected_games = session.get('selected_games')
    
    # Find the selected game object based on its name
    selected_game = next((game for game in selected_games if game[0] == selected_game_name), None)
    
    # Find the game that wasn't selected
    non_selected_game = [game for game in selected_games if game != selected_game]

    if selected_game:
        if selected_game[3] >= non_selected_game[0][3]:
            global global_current_score
            global_current_score += 1
            games_lst = [game for game in game_client.get_game_list() if game not in selected_games]
            session.pop('selected_games', None)
            games_lst = sorted(games_lst, key=lambda x: x[3])
            new_selected_games = random.sample(games_lst, 2)
            session['selected_games'] = new_selected_games
            if not(current_user.highScore):
                current_user.highScore = global_current_score
            else:
                current_user.highScore = max(current_user.highScore,global_current_score)          
            return render_template('game.html',user=current_user,game_list=new_selected_games,game_client=game_client,score=global_current_score)
        else:
            current_user.scores.append(global_current_score)
            global_current_score = 0
            current_user.save()
            if not(current_user.highScore):
                current_user.highScore = max(current_user.scores)
            else:
                current_user.highScore = max(current_user.highScore,current_user.scores)
            current_user.save()
            return render_template('loss.html',user=current_user,lastScore=current_user.scores[-1])


@game.route('/leaderboard')
def leaderboard():
    # we need a way to iterate through each user, grabbing their highest score
    # we then can sort (in reverse) the scores and then pass it into the leaderboard html
    # the reason why we should do reverse is when we iterate through the list in the template,
    # it outputs the highest score first, and so on
    all_users = User.objects()
    user_scores = []
    for user in all_users:
        user_scores.append((user.username,user.highScore if user.highScore else 0 ))
    user_scores.sort(key= lambda x: x[1])
    return render_template('leaderboard.html',scores=user_scores)

