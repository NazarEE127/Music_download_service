from flask import Flask, render_template, request, redirect, flash, send_file, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
from instance.DataBase import *
import requests
import time
import json


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = '79d77d1e7f9348c59a384d4376a9e53f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = 'static/img'
db.init_app(app)
manager = LoginManager(app)


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/profile')
def profile():
    user = User.query.get(current_user.id)
    return render_template("profile.html", user=user)


"""РЕГИСТРАЦИЯ, ВХОД И ВЫХОД"""


@app.route('/sign-up', methods=["POST", "GET"])
def sign_up():
    if request.method == "GET":
        return render_template("sign-up.html")
    email = request.form.get('email')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    user = User.query.filter_by(email=email).first()
    file = request.files['file']
    if allowed_file(file.filename):
        file.save(os.path.join('static/img', file.filename))
    else:
        flash("неправильный формат файла")
        return render_template("sign-up.html")
    if len(email) > 50:
        flash("Слишком длинный логин")
        return render_template("sign-up.html")
    if user is not None:
        flash('Имя пользователя занято!')
        return render_template("sign-up.html")

    if password != password2:
        flash("Пароли не совпадают!")
        return render_template("sign-up.html")
    try:
        hash_pwd = generate_password_hash(password)
        new_user = User(email=email, password=hash_pwd, ava=file.filename)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/")

    except:
        flash("Возникла ошибка при регистрации")
        return render_template("sign-up.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user is not None:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect('/')
            else:
                flash('Неверный логин или пароль')
        else:
            flash('Такого пользователя не существует')
    return render_template("login.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")


@app.route('/find_album', methods=['GET', 'POST'])
def find_album():
    return render_template("find_album.html")


@app.route('/download_track_api/<string:track>', methods=['GET', 'POST'])
def download_track_api(track):
    req = f"http://127.0.0.1:5000/api/v1/track/{track}"
    response = requests.get(req).json()
    filename = os.path.basename(response["filename"])
    file_path = os.path.join('..', 'temp', filename)
    abs_file_path = os.path.abspath(file_path)
    if not os.path.exists(abs_file_path):
        print(f"Файл не найден: {abs_file_path}")
        abort(404, description="Файл не найден")
    return send_file(abs_file_path, as_attachment=True)


@app.route('/download_track', methods=['GET', 'POST'])
def download_track():
    return render_template("download_track.html")


@app.route('/find_album_api/<string:album>', methods=['GET', 'POST'])
def find_album_api(album):
    req = f"http://127.0.0.1:5000/api/v1/album/{album}"
    response = requests.get(req).json()
    return response


@app.route('/ai_tracks', methods=['GET', 'POST'])
def ai_tracks():
    return render_template("ai_tracks.html")


@app.route('/ai_tracks_api/<string:tracks>')
def ai_tracks_api(tracks):
    try:
        req = f"http://127.0.0.1:5000/api/v1/AI_tracks/{tracks}"
        response = requests.get(req)
        
        if response.status_code != 200:
            return jsonify({"error": f"Ошибка API: {response.status_code}"}), response.status_code
            
        try:
            data = response.json()
        except json.JSONDecodeError:
            return jsonify({"error": "Некорректный ответ от API"}), 500
            
        if not isinstance(data, dict) or "recommendations" not in data:
            return jsonify({"error": "Некорректная структура ответа"}), 500
            
        return jsonify(data)
        
    except requests.RequestException as e:
        return jsonify({"error": f"Ошибка при запросе к API: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Неожиданная ошибка: {str(e)}"}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=80)
