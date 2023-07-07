from flask import Flask, render_template, url_for, request

app = Flask(__name__)
message = 'Наполнение сайта'
menu = [{"name": "Установка", "url": "install-flask"},
        {"name": "Первое приложение", "url": "first-app"},
        {"name": "Обратная связь", "url": "contact"}]
@app.route('/')
def index():
    return render_template('index.html', title='Сайт', menu=menu, message=message)
# @app.route('/contact')
# def contact():
#     return render_template('contact.html', title='Контакты')
# @app.route('/username/<path>')
# def username(path):
#
#     return f'{path}'
#1
if __name__ == '__main__':
    app.run(debug=True)

# with app.test_request_context():
#     print(url_for('index'))