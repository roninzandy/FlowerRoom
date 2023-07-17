import datetime
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from FDataBase import FDataBase
from UserLogin import UserLogin

#конфигурация
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'rnnz12345'
#для генерации ключа - os.urandom(20).hex()

app = Flask(__name__)
app.config.from_object(__name__) #загружаем конфигурацию из приложения. (from_object)
#app.permanent_session_lifetime = datetime.timedelta(days=10) #устаналиваем срок жизни сессии

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db'))) #переопределяем путь к БД

login_manager = LoginManager(app)
@login_manager.user_loader #выполняется при каждом запросе от сайта (клиента) для идентификации сессии пользователя
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row  #отображение в виде словаря вместо кортежа
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        cursor = db.cursor()
        cursor.executescript(f.read())
        results = cursor.fetchall()  # Не имеет смысла для операторов типа CREATE, INSERT, UPDATE, DELETE
    db.commit() #сохрание БД
    db.close() #закрытие БД

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

@app.teardown_appcontext
def close_db(error):
    #разрыв соединения в конце запроса
    if hasattr(g, 'link_db'):
        g.link_db.close()

dbase = None
@app.before_request
def before_request():
    #Установка соединения с БД перед выполнением запроса
    global dbase
    db = get_db()
    dbase = FDataBase(db)

@app.route("/") #обработчик запросов
def index(): #функция представления
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


@app.route('/contact', methods=["POST", "GET"])
def contact():

    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')

    return render_template('contact.html', title='Контакты', menu=dbase.getMenu())

@app.errorhandler(404)
def pageNotFound(error):

    return render_template('page404.html', title='Страница не найдена', menu=dbase.getMenu()), 404 #писать 404 необязательно (только если хотим контректную ошибку)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user) #заносит в сессию информацию о текущем пользователе
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm) #авторизация пользователя
            return redirect(url_for('profile'))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Авторизация")

#старый login
# @app.route('/login', methods=['POST', 'GET'])
# def login():

    ##session.permanent = True #срок жизни сессии 31 день
    # if 'username' in session: #куки сессии существуют пока пользователь не закроет браузер
    #     return redirect(url_for('profile', username=session['userLogged']), 302)
    # elif request.method == 'POST' and request.form['username'] == 'selfedu' and request.form['psw'] == '123':
    #     session['userLogged'] = request.form['username']
    #     return redirect(url_for('profile', username=session['userLogged']))
    ##Добавил 'Неверный логин или пароль' в случае неудачной авторизации
    # elif request.method == 'POST' and (request.form['username'] != 'selfedu' or request.form['psw'] != '123'):
    #     flash('Неверный логин или пароль', category='error')
    # res = render_template('login.html', title='Авторизация', menu=dbase.getMenu())
    ## Добавление куков (нужно интегрировать):
    ## log = ''
    ## if request.cookies.get('logged'):
    ##     log = request.cookies.get('logged')
    ## res = make_response(f'<h1>Форма авторизации</h1><p>logged: {log}')
    ## res.set_cookie("logged", "yes")
    # return res


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session.pop('_flashes', None)
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация")

@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')

    return render_template('add_post.html', menu=dbase.getMenu(), title="Добавление статьи")


@app.route("/post/<alias>")
@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)


@app.route('/logout')
@login_required
def logout():
    logout_user() #вся сессионнная информация будет очищена
    flash('Вы вышли из аккаунта', 'success')
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return f"""<p><a href="{url_for('logout')}">Выйти из профиля</a>
            <p>user info {current_user.get_id()}"""

#старый profile
# @app.route('/profile/<username>')
# def profile(username):
#     #session.permanent = True
#     if 'userLogged' not in session or session['userLogged'] != username:
#         abort(401)
#     return f'Профиль пользователя: {username}'

# with app.test_request_context():
#     print(url_for('index'))

if __name__ == "__main__":
    app.run()

