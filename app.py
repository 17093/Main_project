#imports
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

import models #importing model file


@app.route('/', methods=["GET", "POST"])#homepage/landing page
def home():
    #randomly pick an id(make) and deliver to /recommendation
    id_lists = models.Recommendation.query.filter_by(id=id).first_or_404()
    return render_template("home.html", recommendation = recommendation, recommend = results)


@app.route('/recommendation/<int:id>')#selects random music then recommends to user
def recommendation(id):
    results = models.Recommendation.query.filter_by(id=id).first_or_404()

    return render_template("recommendation.html", recommend = results)


@app.route('/profile')
def profile():
    return render_template("profile.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/signup')
def signup():
    return render_template("signup.html")


@app.route('/logout')
def logout():
    return render_template("logout.html")


@app.route('/upload')
def upload():
    return render_template("upload.html")


@app.route('/delete')
def delete():
    return render_template("delete.html")


@app.route('/about')
def about():
    return render_template("about.html")


if __name__ == '__main__' :
    app.run(debug=True)

