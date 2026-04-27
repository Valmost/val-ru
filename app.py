from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from tools.pdf import *
from pycking_test import *
from io import BytesIO
import tempfile
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Создание таблиц
with app.app_context():
    db.create_all()


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        # Валидация
        if not username or not email or not password:
            flash('Все поля обязательны для заполнения', 'danger')
            return redirect(url_for('signup'))

        if password != password_confirm:
            flash('Пароли не совпадают', 'danger')
            return redirect(url_for('signup'))

        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким логином уже существует', 'danger')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash('Пользователь с такой почтой уже существует', 'danger')
            return redirect(url_for('signup'))

        # Создание пользователя
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        flash('Регистрация успешна! Войдите в систему.', 'success')
        return redirect(url_for('signin'))

    return render_template('signup.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'danger')

    return render_template('signin.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('signin'))


@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'pdf_file' not in request.files:
        flash('Файл не выбран', 'danger')
        return redirect(url_for('index'))

    file = request.files['pdf_file']

    if file.filename == '':
        flash('Файл не выбран', 'danger')
        return redirect(url_for('index'))

    if not file.filename.lower().endswith('.pdf'):
        flash('Пожалуйста, загрузите PDF файл', 'danger')
        return redirect(url_for('index'))

    # Получение других данных формы
    width = request.form.get('width')
    height = request.form.get('height')
    algorithm = request.form.get('algorithm')

    # Валидация числовых полей
    try:
        width = int(width)
        height = int(height)
    except (ValueError, TypeError):
        flash('Длина и ширина должны быть целыми числами', 'danger')
        return redirect(url_for('index'))

    if algorithm not in ['genetic', 'shelf', 'left-first-fit']:
        flash('Неверный алгоритм', 'danger')
        return redirect(url_for('index'))

    # Чтение файла в память (без сохранения на диск)
    file_data = file.read()

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_input:
        tmp_input.write(file_data)

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_output:
        output_path = tmp_output.name

    pypack(tmp_input.name, width, height, name=output_path)

    with open(output_path, 'rb') as f:
        processed_data = f.read()
    # ЗАГЛУШКА: Вместо реальной обработки просто возвращаем тот же файл
    # В будущем здесь будет реальная логика изменения PDF
    # Для демонстрации можно добавить watermark или что-то простое
    processed_pdf = BytesIO(processed_data)

    # Можно добавить простую "обработку" - например, метаданные
    # Но пока просто возвращаем как есть

    return send_file(
        processed_pdf,
        as_attachment=True,
        download_name=f'processed_{file.filename}',
        mimetype='application/pdf'
    )


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)