from flask import Flask, render_template, url_for, request, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rnnz12345'
message = 'Наполнение сайта'
menu = [{"name": "Установка", "url": "install-flask"},
        {"name": "Первое приложение", "url": "first-app"},
        {"name": "Обратная связь", "url": "contact"}]
@app.route('/')
def index():
    return render_template('index.html', title='Сайт', menu=menu, message=message)

@app.route('/contact', methods=["POST","GET"])
def contact():

    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')

    return render_template('contact.html', title='Контакты', menu=menu, message=message)


if __name__ == '__main__':
    app.run(debug=True)

# with app.test_request_context():
#     print(url_for('index'))