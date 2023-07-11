import os
import sqlite3

from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g

from FDataBase import FDataBase

#конфигурация
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'rnnz12345'

app = Flask(__name__)
app.config.from_object(__name__) #загружаем конфигурацию из приложения. (from_object)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db'))) #переопределяем путь к БД

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
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.route("/")
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html', menu = dbase.getMenu(), posts=dbase.getPostsAnonce())


@app.route('/contact', methods=["POST", "GET"])
def contact():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')

    return render_template('contact.html', title='Контакты', menu=dbase.getMenu())

@app.errorhandler(404)
def pageNotFound(error):
    db = get_db()
    dbase = FDataBase(db)
    return render_template('page404.html', title='Страница не найдена', menu=dbase.getMenu()), 404 #писать 404 необязательно (только если хотим контректную ошибку)

@app.route('/login', methods=['POST', 'GET'])
def login():
    db = get_db()
    dbase = FDataBase(db)
    if 'username' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == 'selfedu' and request.form['psw'] == '123':
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))

    return render_template('login.html', title='Авторизация', menu=dbase.getMenu())

@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    db = get_db()
    dbase = FDataBase(db)

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
def showPost(alias):
    db = get_db()
    dbase = FDataBase(db)
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)



@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'Профиль пользователя: {username}'

# with app.test_request_context():
#     print(url_for('index'))

if __name__ == "__main__":
    app.run()
