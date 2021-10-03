######## I M P O R T S ########

from flask import Flask, render_template, request, session, redirect, url_for, flash, json
from flask_login import login_required
from mysql_db import MySQL
from datetime import datetime

import mysql.connector as connector

######## V A R I A B L E S ########

app = Flask(__name__)
app.config.from_pyfile('config.py')

mysql = MySQL(app)

from auth import bp as auth_bp, init_login_manager, check_rights
init_login_manager(app)
app.register_blueprint(auth_bp)

images_ids = ['1c84377ab9536a6c735cebf38754ce4e8599925e_full',
'eMYYT004AwI',
'derkberm',
'-5zjrpFD8mg',
'1c84377ab9536a6c735cebf38754ce4e8599925e_full',
'eMYYT004AwI',
'derkberm',
'-5zjrpFD8mg',
'1c84377ab9536a6c735cebf38754ce4e8599925e_full',
'eMYYT004AwI',
'derkberm',
'-5zjrpFD8mg',
'1c84377ab9536a6c735cebf38754ce4e8599925e_full',
'eMYYT004AwI',
'derkberm',
'-5zjrpFD8mg']

######## F U N C T I O N S ########

def load_roles():
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT id, name FROM roles;')  
    roles = cursor.fetchall()
    cursor.close()
    return roles

def load_genres():
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM genres;')  
    genres = cursor.fetchall()
    cursor.close()
    return genres

def load_game_genres(game_id):  # для загрузки жанров, имеющихся у игры в форму
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM game_has_genre WHERE game_id=%s;', (game_id,))
    gamegenres = cursor.fetchall()
    cursor.close()
    return gamegenres

@app.route('/')
def index():
    with mysql.connection.cursor(named_tuple=True) as cursor:   
        cursor.execute('''
            SELECT games.id, games.name, main_picture, release_date, discount, price, platform, GROUP_CONCAT(
                genres.name SEPARATOR ', ') AS genre_names FROM games 
            JOIN game_has_genre ON games.id = game_has_genre.game_id
            INNER JOIN genres ON genres.id = game_has_genre.genre_id 
            where games.is_bestseller = 1 group by games.id LIMIT 5;
        ''')
        populargames = cursor.fetchall()
        cursor.execute('''
            SELECT games.id, games.name, main_picture, release_date, discount, price, platform, GROUP_CONCAT(
                genres.name SEPARATOR ', ') AS genre_names FROM games 
            JOIN game_has_genre ON games.id = game_has_genre.game_id
            INNER JOIN genres ON genres.id = game_has_genre.genre_id 
            where games.is_new = 1 group by games.id ORDER BY release_date DESC LIMIT 5;
        ''')
        newgames = cursor.fetchall()
        cursor.execute('''
            SELECT games.id, games.name, main_picture, release_date, discount, price, platform, GROUP_CONCAT(
                genres.name SEPARATOR ', ') AS genre_names FROM games 
            JOIN game_has_genre ON games.id = game_has_genre.game_id
            INNER JOIN genres ON genres.id = game_has_genre.genre_id 
            where games.is_onsale = 1 group by games.id LIMIT 5;
        ''')
        salegames = cursor.fetchall()

        cursor.execute('''
            SELECT games.id, games.name, main_picture, release_date, discount, price, small_description, platform, GROUP_CONCAT(
                genres.name SEPARATOR ', '
            ) AS genre_names FROM games 
            JOIN slidergames ON slidergames.game_id = games.id
            JOIN game_has_genre ON games.id = game_has_genre.game_id
            INNER JOIN genres ON genres.id = game_has_genre.genre_id GROUP BY games.id ORDER BY release_date DESC;
        ''')
        slider = cursor.fetchall()
        jsonslider = json.dumps(slider)
        
    return render_template('index.html', populargames=populargames, newgames=newgames, salegames=salegames, slider=slider, jsonslider=jsonslider, genres=load_genres())

@app.route('/catalog')
def catalog():
    title = 'Каталог'

    with mysql.connection.cursor(named_tuple=True) as cursor:   
        cursor.execute('''
            SELECT games.id, games.name, main_picture, release_date, discount, price, platform, GROUP_CONCAT(
                genres.name SEPARATOR ', ') AS genre_names FROM games 
            JOIN game_has_genre ON games.id = game_has_genre.game_id
            INNER JOIN genres ON genres.id = game_has_genre.genre_id 
            GROUP BY games.id;
        ''')
        games = cursor.fetchall()

    return render_template('catalog.html', title=title, games=games, genres=load_genres())

@app.route('/guarantees')
def guarantees():
    title = 'О нас'
    return render_template('guarantees.html', title=title)

@app.route('/help')
def help():
    title = 'Помощь'
    return render_template('help.html', title=title)

@app.route('/signup')
def signup():
    title = 'Регистрация'
    return render_template('users/new.html', title=title, user={})

@app.route('/tos')
def tos():
    title = 'Пользовательское соглашение'
    return render_template('tos.html', title=title)

@app.route('/cart/<int:game_id>')
def cart(game_id):
    title = 'Корзина'

    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('''
        SELECT games.*, GROUP_CONCAT(
        genres.name SEPARATOR ', ') AS genre_names FROM games 
        JOIN game_has_genre ON games.id = game_has_genre.game_id
        INNER JOIN genres ON genres.id = game_has_genre.genre_id 
        WHERE games.id = %s group by games.id;
        ''', (game_id,))
    game = cursor.fetchone()
    cursor.close()
    return render_template('cart.html', title=title, game=game)

@app.route('/cart/<int:game_id>/buy', methods=['POST'])
def buy(game_id):
    title = 'Оплата'

    boughtgame_id = game_id
    order_price = request.form.get('order_price') or None
    order_date = datetime.now()
    email = request.form.get('email') or None
    promocode = request.form.get('promocode') or None

    with mysql.connection.cursor(named_tuple=True) as cursor: 
        try:
            cursor.execute('INSERT INTO orders (boughtgame_id, order_price, order_date, customer_email, usedpromo_id) VALUES (%s, %s, %s, %s, %s)', (boughtgame_id, order_price, order_date, email, promocode))
            cursor.execute('UPDATE games SET quantity=quantity-1 WHERE id=%s;', (boughtgame_id,))
        except Exception as e:
            flash(f'Не удалось купить игру: {e}', 'danger')
            return redirect(url_for('cart', game_id=boughtgame_id))
        mysql.connection.commit()
        flash(f'Игра {boughtgame_id} успешно куплена', 'success')
    return redirect(url_for('index'))
    
@app.route('/cart/buy_failure')
def buy_failure():
    flash('Оплата провалена!', 'danger')
    return redirect(url_for('index'))

@app.route('/game/<int:game_id>')
def gamepage(game_id):
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('''
        SELECT games.*, GROUP_CONCAT(
        genres.name SEPARATOR ', ') AS genre_names FROM games 
        JOIN game_has_genre ON games.id = game_has_genre.game_id
        INNER JOIN genres ON genres.id = game_has_genre.genre_id 
        WHERE games.id = %s group by games.id;
        ''', (game_id,))
    game = cursor.fetchone()
    cursor.close()

    title = f'{game.name}'
    return render_template('gamepage.html', title=title, game=game)

@app.route('/users/<int:user_id>')
@login_required
@check_rights('show')
def userpage(user_id):
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM users WHERE id = %s;', (user_id,))  #запятая для создания tuple
    user = cursor.fetchone()
    cursor.execute('''SELECT games.name as game_name, orders.order_price, orders.customer_email, orders.order_date FROM orders
        INNER JOIN games ON orders.boughtgame_id = games.id
        WHERE orders.customer_email = (SELECT email FROM users WHERE users.id = %s);''', (user_id,))
    orders = cursor.fetchall()
    cursor.close()

    title = 'Личный кабинет'
    return render_template('users/userpage.html', title=title, user=user, orders=orders)

@app.route('/users/createuser', methods=['POST'])
def createuser():
    login = request.form.get('login') or None
    password = request.form.get('password') or None
    role_id = 2
    email = request.form.get('email') or None
    
    query = '''
        INSERT INTO users (login, password_hash, role_id, email)
        VALUES (%s, SHA2(%s, 256), %s, %s);
    '''
    cursor = mysql.connection.cursor(named_tuple=True)
    try:
        cursor.execute(query, (login, password, role_id, email))
    except connector.errors.IntegrityError as e:
        if (e.errno == 1048):
            flash(f'Не все поля были заполнены, заполните поля: {e.msg}', 'danger')
        elif (e.errno != 1062):
            flash(f'Такие логин и\или почта уже существуют: {e}', 'danger')
        user = {
            'login': login,
            'password': password,
            'role_id': role_id,
            'email': email
        }
        return render_template('users/new.html', user=user)
    
    mysql.connection.commit()
    cursor.close()

    flash(f'Пользователь {login} успешно зарегистрирован', 'success')
    return redirect(url_for('index'))

@app.route('/users/<int:user_id>/edit')
@login_required
@check_rights('edit')
def edit(user_id):
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM users WHERE id = %s;', (user_id,))  #запятая для создания tuple
    user = cursor.fetchone()
    cursor.close()

    title = 'Редактировать пользователя'
    return render_template('users/edit.html', title=title, user=user, roles=load_roles())

@app.route('/users/<int:user_id>/updateuser', methods=['POST'])
@login_required
@check_rights('edit')
def updateuser(user_id):
    login = request.form.get('login') or None
    try:
        role_id = int(request.form.get('role_id'))
    except ValueError:
        role_id = None
    email = request.form.get('email') or None
    
    query = '''
        UPDATE users SET login=%s, role_id=%s, email=%s
        WHERE id = %s;
    '''
    cursor = mysql.connection.cursor(named_tuple=True)
    try:
        cursor.execute(query, (login, role_id, email, user_id))
    except connector.errors.DatabaseError:
        flash('Не все поля были корректно заполнены, заполните поля правильно!', 'danger')
        user = {
            'id': user_id,
            'login': login,
            'role_id': role_id,
            'email': email
        }
        return render_template('users/edit.html', user=user, roles=load_roles())
    mysql.connection.commit()
    cursor.close()

    flash(f'Пользователь {login} успешно обновлён', 'success')
    return redirect(url_for('users'))

@app.route('/users/<int:user_id>/deleteuser', methods=['POST'])
@login_required
@check_rights('delete')
def deleteuser(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        try:
            cursor.execute('DELETE FROM users WHERE id = %s;', (user_id,))  #запятая для создания tuple
        except connector.errors.DatabaseError:
            flash('Не удалось удалить пользователя!', 'danger')
            return redirect(url_for('users'))
        mysql.connection.commit()
        flash('Запись успешно удалена', 'success')
    return redirect(url_for('users'))

######## A D M I N P A N E L ########
######## A D M I N P A N E L ########
######## A D M I N P A N E L ########

@app.route('/admin/id<int:user_id>')
@login_required
@check_rights('admin_rights')
def admin(user_id):
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM users WHERE id = %s;', (user_id,))  #запятая для создания tuple
    user = cursor.fetchone()
    cursor.execute('SELECT * FROM roles WHERE id = %s;', (user.role_id,))  #запятая для создания tuple
    role = cursor.fetchone()
    cursor.close()

    title = 'Панель администратора'
    return render_template('admin/panel.html', title=title, user=user, role=role)

@app.route('/admin/orders', methods=['GET', 'POST'])
@login_required
@check_rights('admin_rights')
def orders():
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM orders;')
    orders = cursor.fetchall() 
    cursor.close()

    title = 'Все заказы'
    return render_template('admin/orders.html', title=title, orders=orders)

@app.route('/admin/users')
@login_required
@check_rights('admin_rights')
def users():
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT users.*, roles.name AS role_name FROM users LEFT OUTER JOIN roles ON users.role_id = roles.id;')
    users = cursor.fetchall()
    cursor.close()
    title = 'Пользователи'
    return render_template('admin/users.html', title=title, users=users)

@app.route('/admin/products', methods=['GET', 'POST'])
@login_required
@check_rights('admin_rights')
def products():
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT id, name, default_price, discount, price, quantity FROM games;')
    games = cursor.fetchall() 
    cursor.close()

    title = 'Все товары'
    return render_template('admin/products.html', title=title, games=games)

@app.route('/admin/slider', methods=['GET', 'POST'])
@login_required
@check_rights('admin_rights')
def slider():
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT games.id, games.name, games.main_picture FROM games JOIN slidergames ON slidergames.game_id = games.id;')
    slider = cursor.fetchall()
    cursor.execute('SELECT id, name, main_picture FROM games WHERE id NOT IN (SELECT game_id FROM slidergames);')
    games = cursor.fetchall() 
    cursor.close()

    title = 'Слайдер'
    return render_template('admin/slider.html', title=title, games=games, slider=slider)

@app.route('/admin/products/<int:game_id>/newslider', methods=['GET', 'POST'])
@login_required
@check_rights('admin_rights')
def newslider(game_id):
    with mysql.connection.cursor(named_tuple=True) as cursor: 
        try:
            cursor.execute('INSERT INTO slidergames (game_id) VALUES (%s)', (game_id, ))
        except connector.errors.DatabaseError:
            flash('Не удалось добавить игру в слайдер!', 'danger')
            return redirect(url_for('slider'))
        mysql.connection.commit()
        flash(f'Игра {game_id} успешно добавлена в слайдер', 'success')
    return redirect(url_for('slider'))

@app.route('/admin/products/<int:game_id>/deleteslider', methods=['POST'])
@login_required
@check_rights('admin_rights')
def deleteslider(game_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        try:
            cursor.execute('DELETE FROM slidergames WHERE game_id = %s;', (game_id,))  #запятая для создания tuple
        except connector.errors.DatabaseError:
            flash(f'Не удалось удалить товар из слайдера! id{game_id}', 'danger')
            return redirect(url_for('slider'))

        mysql.connection.commit()
        flash(f'Товар id{game_id} успешно удален из слайдера', 'success')
    return redirect(url_for('slider'))

@app.route('/admin/newgame')
@login_required
@check_rights('admin_rights')
def newgame():
    title = 'Создать товар'
    return render_template('admin/newproduct.html', title=title, game={}, genres=load_genres())

@app.route('/admin/newgame_commit', methods=['POST'])
@login_required
@check_rights('admin_rights')
def newgame_commit():
    name = request.form.get('name') or None

    try:
        default_price = int(request.form.get('default_price'))
    except ValueError:
        default_price = None

    try:
        discount = int(request.form.get('discount'))
    except ValueError:
        discount = None

    price = round(default_price-default_price*(discount/100)) or None
    small_description = request.form.get('small_description') or None
    big_description = request.form.get('big_description') or None
    release_date = request.form.get('release_date') or None

    try:
        quantity = int(request.form.get('quantity'))
    except ValueError:
        quantity = None

    try:
        if (len(request.form.get('main_picture'))):
            main_picture = 'images/games/' + request.form.get('main_picture')
        else:
            if (request.form.get('prev_main_picture') != 'images/games/'):
                main_picture = request.form.get('prev_main_picture')
            else:
                flash(f'Выберите картинку!', 'danger')
                return redirect(url_for('newgame', game_id=game_id))
    except TypeError:
        main_picture = ''
        raise

    chosengenres = request.form.getlist('genres') or None
    platform = request.form.get('platform') or None
    sysrequirements = request.form.get('sysrequirements') or None
    activation = request.form.get('activation') or None
    is_new = request.form.get('is_new') == 'on'
    is_bestseller = request.form.get('is_bestseller') == 'on'
    is_onsale = request.form.get('is_onsale') == 'on'
    
    query = '''
        INSERT INTO games (name, default_price, discount, price, small_description, big_description, release_date, quantity, main_picture, platform, sysrequirements, activation, is_new, is_bestseller, is_onsale)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    '''
    cursor = mysql.connection.cursor(named_tuple=True)
    try:
        cursor.execute(query, (name, default_price, discount, price, small_description, big_description, release_date, quantity, main_picture, platform, sysrequirements, activation, is_new, is_bestseller, is_onsale))
    except connector.errors.DatabaseError or TypeError:
        flash('Не все поля были корректно заполнены, заполните поля правильно!', 'danger')
        game = {
            'name': name,
            'default_price': default_price,
            'discount': discount,
            'price': price,
            'small_description': small_description,
            'big_description': big_description,
            'release_date': release_date,
            'quantity': quantity,
            'main_picture': main_picture,
            'platform': platform,
            'sysrequirements': sysrequirements,
            'activation': activation,
            'is_new': is_new,
            'is_bestseller': is_bestseller,
            'is_onsale': is_onsale
        }
        return render_template('admin/newproduct.html', game=game, genres=load_genres(), gamegenres=chosengenres)

    cursor.execute('SELECT id FROM games WHERE games.name=%s;', (name, ))
    game_id = cursor.fetchone()
    for i in range(len(chosengenres)):
        try:
            cursor.execute('INSERT INTO game_has_genre (game_id, genre_id) VALUES (%s, %s);', (game_id.id, int(chosengenres[i])))
        except connector.errors.DatabaseError:
            flash(f'Жанры не заполнились: ошибка! id={game_id.id}, genre={int(chosengenres[i])}', 'danger')
            game = {
            'name': name,
            'default_price': default_price,
            'discount': discount,
            'price': price,
            'small_description': small_description,
            'big_description': big_description,
            'release_date': release_date,
            'quantity': quantity,
            'main_picture': main_picture,
            'platform': platform,
            'sysrequirements': sysrequirements,
            'activation': activation,
            'is_new': is_new,
            'is_bestseller': is_bestseller,
            'is_onsale': is_onsale
            }
            return render_template('admin/newproduct.html', game=game, genres=load_genres(), gamegenres=chosengenres)

    mysql.connection.commit()
    cursor.close()

    flash(f'Товар {name} успешно создан {chosengenres}', 'success')
    return redirect(url_for('products'))

@app.route('/admin/products/<int:game_id>')
@login_required
@check_rights('editgame')
def editgame(game_id):
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM games WHERE id = %s;', (game_id,))  #запятая для создания tuple
    game = cursor.fetchone()
    cursor.close()

    title = 'Редактировать товар'
    return render_template('admin/editproduct.html', title=title, game=game, genres=load_genres(), gamegenres=load_game_genres(game.id))

@app.route('/admin/products/<int:game_id>/editgame', methods=['POST'])
@login_required
@check_rights('editgame')
def editgame_commit(game_id):
    name = request.form.get('name') or None

    try:
        default_price = int(request.form.get('default_price'))
    except ValueError:
        default_price = None

    try:
        discount = int(request.form.get('discount'))
    except ValueError:
        discount = None

    price = round(default_price-default_price*(discount/100)) or None
    small_description = request.form.get('small_description') or None
    big_description = request.form.get('big_description') or None
    release_date = request.form.get('release_date') or None
    
    try:
        quantity = int(request.form.get('quantity'))
    except ValueError:
        quantity = None

    try:
        if (len(request.form.get('main_picture'))):
            main_picture = 'images/games/' + request.form.get('main_picture')
        else:
            if (request.form.get('prev_main_picture') != 'images/games/'):
                main_picture = request.form.get('prev_main_picture')
            else:
                flash(f'Выберите картинку!', 'danger')
                return redirect(url_for('editgame', game_id=game_id))
    except TypeError:
        main_picture = ''
        raise
    
    chosengenres = request.form.getlist('genres') or None
    platform = request.form.get('platform') or None
    sysrequirements = request.form.get('sysrequirements') or None
    activation = request.form.get('activation') or None
    is_new = request.form.get('is_new') == 'on'
    is_bestseller = request.form.get('is_bestseller') == 'on'
    is_onsale = request.form.get('is_onsale') == 'on'
    
    query = '''
            UPDATE games SET name=%s, default_price=%s, discount=%s, price=%s, small_description=%s, big_description=%s, release_date=%s, quantity=%s, main_picture=%s, platform=%s, sysrequirements=%s, activation=%s, is_new=%s, is_bestseller=%s, is_onsale=%s
            WHERE id = %s;
    '''
    cursor = mysql.connection.cursor(named_tuple=True)
    try:
        cursor.execute(query, (name, default_price, discount, price, small_description, big_description, release_date, quantity, main_picture, platform, sysrequirements, activation, is_new, is_bestseller, is_onsale, game_id))
    except Exception as e:
        flash(f'Не все поля были корректно заполнены, заполните поля правильно: {e}', 'danger')
        game = {
            'id': game_id,
            'name': name,
            'default_price': default_price,
            'discount': discount,
            'price': price,
            'small_description': small_description,
            'big_description': big_description,
            'release_date': release_date,
            'quantity': quantity,
            'main_picture': main_picture,
            'platform': platform,
            'sysrequirements': sysrequirements,
            'activation': activation,
            'is_new': is_new,
            'is_bestseller': is_bestseller,
            'is_onsale': is_onsale
        }
        return render_template('admin/editproduct.html', game=game, genres=load_genres(), gamegenres=load_game_genres(game_id))

    cursor.execute('DELETE FROM game_has_genre WHERE game_id = %s;', (game_id,))

    try:
        for i in range(len(chosengenres)):
            try:
                cursor.execute('INSERT INTO game_has_genre (game_id, genre_id) VALUES (%s, %s);', (game_id, int(chosengenres[i])))
            except connector.errors.DatabaseError:
                flash(f'Жанры не заполнились: ошибка! id={game_id}, genre={int(chosengenres[i])}', 'danger')
                game = {
                'id': game_id,
                'name': name,
                'default_price': default_price,
                'discount': discount,
                'price': price,
                'small_description': small_description,
                'big_description': big_description,
                'release_date': release_date,
                'quantity': quantity,
                'main_picture': main_picture,
                'platform': platform,
                'sysrequirements': sysrequirements,
                'activation': activation,
                'is_new': is_new,
                'is_bestseller': is_bestseller,
                'is_onsale': is_onsale
                }
                return render_template('admin/editproduct.html', game=game, genres=load_genres(), gamegenres=load_game_genres(game_id))
    except Exception as e:
        flash('Заполните жанры!', 'danger')
        game = {
            'id': game_id,
            'name': name,
            'default_price': default_price,
            'discount': discount,
            'price': price,
            'small_description': small_description,
            'big_description': big_description,
            'release_date': release_date,
            'quantity': quantity,
            'main_picture': main_picture,
            'platform': platform,
            'sysrequirements': sysrequirements,
            'activation': activation,
            'is_new': is_new,
            'is_bestseller': is_bestseller,
            'is_onsale': is_onsale
            }
        return render_template('admin/editproduct.html', game=game, genres=load_genres(), gamegenres=load_game_genres(game_id))

    mysql.connection.commit()
    cursor.close()

    flash(f'Товар {name} успешно обновлён', 'success')
    return redirect(url_for('products'))

@app.route('/admin/products/<int:game_id>/deletegame', methods=['POST'])
@login_required
@check_rights('delete')
def deletegame(game_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        try:
            cursor.execute('DELETE FROM games WHERE id = %s;', (game_id,))  #запятая для создания tuple
        except connector.errors.DatabaseError:
            flash('Не удалось удалить товар!', 'danger')
            return redirect(url_for('products'))
        try:
            cursor.execute('DELETE FROM game_has_genre WHERE game_id = %s;', (game_id,))  #запятая для создания tuple
        except connector.errors.DatabaseError:
            flash('Не удалось удалить товар!', 'danger')
            return redirect(url_for('products'))
        mysql.connection.commit()
        flash(f'Товар id{game_id} успешно удален', 'success')
    return redirect(url_for('products'))