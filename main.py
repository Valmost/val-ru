import os

from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Моя страница, мой аккаунт, это мой дом, поэтому будь добр заходи в него с благими намерениями или"


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)

