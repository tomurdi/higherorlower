from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename
import io
import base64
from ..models import User
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm, UpdateProfilePicForm
from .. import bcrypt

users = Blueprint("users", __name__)

def get_b64_img(username):
    user = User.objects(username=username).first()
    if user.profile_pic is None:
        return None
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image

@users.route('/register', methods=['GET', 'POST'])
def register_route():
    if current_user.is_authenticated: # essentially when the user is logged in we simply display the other
                                      # form of the main screen. 
        return redirect(url_for('main.index'))
    form = RegistrationForm() # getting an instance of the form. 
    if request.method == 'POST': # user has submitted the form with
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            user.save()
            return redirect(url_for('users.login_route'))
    return render_template('register.html', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login_route():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.objects(username=form.username.data).first()
            if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('users.user_route', username=user.username))
            else:
                flash("Failed to log in!")
    return render_template('login.html', form=form)

@users.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user_route(username):
    update_username_form = UpdateUsernameForm()
    update_profile_pic_form = UpdateProfilePicForm()
    if not (current_user):
        abort(404)
    if request.method == "POST":
        if update_username_form.submit_username.data and update_username_form.validate():
            current_user.modify(username=update_username_form.username.data)
            current_user.save()
            return redirect(url_for('users.login_route'))
        if update_profile_pic_form.submit_picture.data and update_profile_pic_form.validate():
            image = update_profile_pic_form.picture.data
            filename = secure_filename(image.filename) 
            content_type = f'images/{filename[-3:]}'
            if current_user.profile_pic is None: 
                current_user.profile_pic.put(image.stream, content_type=content_type)
            else:
                current_user.profile_pic.replace(image.stream, content_type=content_type)
            current_user.save()
            return redirect(url_for('users.user_route',username=current_user.username))
    scores = current_user.scores if current_user.scores else []
    return render_template('user.html',user=current_user, 
                           update_username_form=update_username_form,
                           update_profile_pic_form=update_profile_pic_form, 
                           profile_pic_base64=get_b64_img(current_user.username), 
                           scores=scores,
                           highscore=max(scores) if scores else 0)

@users.route('/logout')
def logout_route():
    logout_user()
    return redirect(url_for('main.index'))

# def add_score_to_user(username, new_score):
#     user = User.objects(username=username).first()
#     if user:
#         user.scores.append(new_score)
#         user.save()
#         user.highScore = max(user.scores)
#         user.save()
#     else:
#         return render_template('404.html')