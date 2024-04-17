from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename
import io
import base64
from ..models import User
from ..forms import RegistrationForm, LoginForm, UploadPhotoForm
from .. import bcrypt

users = Blueprint("users", __name__)



@users.route('/user/<username>')
def user_route(username):
    user = User.objects(username=username).first()
    profile_pic_bytes = io.BytesIO(user.profile_pic.read())
    profile_pic_base64 = base64.b64encode(profile_pic_bytes.getvalue()).decode()
    scores = [-1] #TODO: Fix this so that it shows the high score
    return render_template('user.html', username=username, profile_pic_base64=profile_pic_base64, scores=scores)

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
    form = UploadPhotoForm()
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

