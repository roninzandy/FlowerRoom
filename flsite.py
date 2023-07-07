from flask import Flask, render_template, url_for, request

app = Flask(__name__)

@app.route('/')
def index():

    return render_template('index.html', title='Сайт')

# @app.route('/username/<path>')
# def username(path):
#
#     return f'{path}'

if __name__ == '__main__':
    app.run(debug=True)

# with app.test_request_context():
#     print(url_for('index'))