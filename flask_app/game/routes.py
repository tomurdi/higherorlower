from flask import Blueprint, render_template, request, session
import base64, io
import random
from io import BytesIO
from flask_login import current_user, login_required
from ..models import User
from ..client import GameClient
from .. import bcrypt

game = Blueprint('game', __name__)
game_client = GameClient()
global global_current_score
global length
global_current_score = 0
length = len(game_client.get_game_list())

def get_b64_img(username):
    user = User.objects(username=username).first()
    if user.profile_pic is None:
        return None
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image


@game.route('/hard')
@login_required
def hard(username=None):
    user = User.objects(username=username).first() if username else None
    games_lst = sorted(game_client.get_game_list(),key=lambda x:x[3])
    easy = games_lst[0:(length // 3)]
    selected_games = random.sample(easy, 2)
    session['selected_games'] = easy
    return render_template('game.html',user=current_user,game_list=selected_games,game_client=game_client,score=global_current_score)


@game.route('/medium')
@login_required
def medium(username=None):
    user = User.objects(username=username).first() if username else None
    games_lst = sorted(game_client.get_game_list(),key=lambda x:x[3])
    medium = games_lst[(length // 3):(2*length)//3]
    selected_games = random.sample(medium, 2)
    session['selected_games'] = selected_games
    return render_template('game.html',user=current_user,game_list=selected_games,game_client=game_client,score=global_current_score)

@game.route('/easy')
@login_required
def easy(username=None):
    user = User.objects(username=username).first() if username else None
    games_lst = sorted(game_client.get_game_list(),key=lambda x:x[3])
    hard = games_lst[(2*length) // 3:]
    selected_games = random.sample(hard, 2)
    session['selected_games'] = selected_games
    return render_template('game.html',user=current_user,game_list=selected_games,game_client=game_client,score=global_current_score)

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
            new_selected_games = random.choices(games_lst, k=2)
            session['selected_games'] = new_selected_games
            if not(current_user.highScore):
                current_user.highScore = global_current_score
            else:
                current_user.highScore = max(current_user.highScore,global_current_score)          
            return render_template('game.html',user=current_user,game_list=new_selected_games,game_client=game_client,score=global_current_score)
        else:
            session.pop('selected_games', None)
            current_user.scores.append(global_current_score)
            global_current_score = 0
            current_user.save()
            if not(current_user.highScore):
                current_user.highScore = max(max(current_user.scores),global_current_score)
            else:
                current_user.highScore = max(current_user.highScore,max(current_user.scores),global_current_score)
            current_user.save()
            return render_template('loss.html',user=current_user,lastScore=current_user.scores[-1])
    else:
        session.pop('selected_games', None)
        global_current_score = 0


@game.route('/leaderboard')
def leaderboard():
    # we need a way to iterate through each user, grabbing their highest score
    # we then can sort (in reverse) the scores and then pass it into the leaderboard html
    # the reason why we should do reverse is when we iterate through the list in the template,
    # it outputs the highest score first, and so on
    all_users = User.objects()
    user_scores = []
    for user in all_users:
        user_scores.append((user.username,get_b64_img(user.username),user.highScore if user.highScore else 0 ))
    user_scores.sort(key= lambda x: -x[2])
    return render_template('leaderboard.html',scores=user_scores)

