######## I M P O R T S ########

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
from app import mysql
from users_policy import UsersPolicy

######## V A R I A B L E S ########

bp = Blueprint('auth', __name__, url_prefix='/auth')

######## C L A S S E S ########

class User(UserMixin):
    def __init__(self, user_id, email, login, role_id):
        super().__init__()
        self.id = user_id
        self.email = email
        self.login = login
        self.role_id = role_id

    def can(self, action, record=None):
        policy = UsersPolicy(record=record)
        method = getattr(policy, action, None)
        if method:
            return method()
        return False

######## F U N C T I O N S ########

def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для доступа к этой странице необходимо авторизоваться.'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)

def load_user(user_id):
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM users WHERE id = %s;', (user_id,))  #запятая для создания tuple
    db_user = cursor.fetchone()
    cursor.close()
    if db_user:
        return User(user_id=db_user.id, email=db_user.email, login=db_user.login, role_id=db_user.role_id)
    return None

def load_record(user_id):
    if user_id is None:
        return None
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM users WHERE id = %s;', (user_id,))  #запятая для создания tuple
    record = cursor.fetchone()
    cursor.close()
    return record

def check_rights(action):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            record = load_record(kwargs.get('user_id'))
            if not current_user.can(action, record=record):
                flash('Недостаточно прав доступа', 'danger')
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        return wrapper
    return decorator

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'
        if login and password:
            cursor = mysql.connection.cursor(named_tuple=True)
            cursor.execute('SELECT * FROM users WHERE login = %s AND password_hash = SHA2(%s, 256);', (login, password))
            db_user = cursor.fetchone()
            cursor.close()
            if db_user:
                user = User(user_id=db_user.id, email=db_user.email, login=db_user.login, role_id=db_user.role_id)
                login_user(user, remember=remember_me)

                flash('Вы успешно авторизовались', 'success')

                next = request.args.get('next')

                return redirect(next or url_for('index'))
        flash('Неверно введены логин и\или пароль', 'danger')
    title = 'Вход'
    return render_template('login.html', title=title)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))