from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename
import io
import base64
from ..models import User
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm, UpdateProfilePicForm, Up

from .. import bcrypt

users = Blueprint("users", __name__)



@users.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user_route(username):
    # Forms for updating the username and profile picture
    update_username_form = UpdateUsernameForm()
    update_profile_pic_form = UpdateProfilePicForm()

    # Get the current user's details
    user = User.objects(username=username).first()
    if not user:
        abort(404)

    if update_username_form.validate_on_submit():
        # Process the update of the username
        new_username = update_username_form.username.data
        existing_user = User.objects(username=new_username).first()
        if existing_user:
            flash("Username is taken")
        else:
            user.modify(username=new_username)
            user.save()
            flash("Username updated successfully")
            return redirect(url_for('users.user_route', username=new_username))

    if update_profile_pic_form.validate_on_submit():
        # Process the update of the profile picture
        image = update_profile_pic_form.picture.data
        filename = secure_filename(image.filename)
        content_type = f'image/{filename.rsplit('.', 1)[1].lower()}'
        if user.profile_pic.get() is None:
            user.profile_pic.put(image.stream, content_type=content_type)
        else:
            user.profile_pic.replace(image.stream, content_type=content_type)
        user.save()
        return redirect(url_for('users.user_route', username=username))

    if user.profile_pic:
        profile_pic_bytes = io.BytesIO(user.profile_pic.read())
        profile_pic_base64 = base64.b64encode(profile_pic_bytes.getvalue()).decode()
    else:
        profile_pic_base64 = None

    # TODO: Fix scores
    user = User.objects(username=username).first()
    scores = user.scores

    return render_template('user.html', 
                           user=user, 
                           update_username_form=update_username_form,
                           update_profile_pic_form=update_profile_pic_form, 
                           profile_pic_base64=profile_pic_base64, 
                           scores=scores,
                           highscore=max(scores))




@users.route('/register', methods=['GET', 'POST'])
def register_route():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if request.method == 'POST':
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


@users.route('/logout')
def logout_route():
    logout_user()
    return redirect(url_for('main.index'))


@users.route('/uploadphoto', methods=['GET', 'POST'])
@login_required
def uploadphoto_route():
    form = UpdateProfilePicForm()
    if form.validate_on_submit():
        image = form.photo.data
        filename = secure_filename(image.filename)
        content_type = f'images/{filename[-3:]}'
        if current_user.profile_pic.get() is None:
            current_user.profile_pic.put(image.stream, content_type=content_type)
        else:
            current_user.profile_pic.replace(image.stream, content_type=content_type)
        current_user.save()
        return redirect(url_for('users.user_route', username=current_user.username))
    return render_template('uploadphoto.html', form=form)


def add_score_to_user(username, new_score):
    user = User.objects(username=username).first()
    if user:
        user.scores.append(new_score)
        user.save()
        user.highScore = max(user.scores)
        user.save()
    else:
        return render_template('404.html')