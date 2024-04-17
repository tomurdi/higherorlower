from flask import Blueprint, render_template

game = Blueprint('game', __name__)

@game.route('/play')
def play():
    return render_template('game.html')