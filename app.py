#imports
from flask import Flask, render_template, g, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from config import Config
import random
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import urllib


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

import models #importing model file

#https://jinja.palletsprojects.com/en/3.0.x/templates/

@app.route('/', methods=["GET", "POST"])#homepage/landing page
def home():
    
    #randomly pick an id(make) and deliver to /recommendation
    #number of songs within database
    id_list = len(models.Recommendation.query.all())
    id_song = random.randint(1,id_list)

    #id_lists = models.Recommendation.query.filter_by(id=id).first_or_404()
    
    return render_template("home.html", id_song = id_song)


@app.route('/recommendation/<int:id>')#selects random music then recommends to user
def recommendation(id):

    #ADD VIEWCOUNT IF CAN

    #number of songs within database
    id_list = len(models.Recommendation.query.all()) #gets how many songs there are to recommend
    id_song = random.randint(1,id_list) #picks random id
    song = models.Recommendation.query.filter_by(id=id_song).first_or_404() #retrivees the randomly picked song/id
    
    #detecting the type of the song(spotify or youtube link)
    if song.songType == 1:
        type_link = 1   
    if song.songType == 2:
        type_link = 2
       
    return render_template("recommendation.html", recommend = song, type_link = type_link)


@app.route('/profile/<int:id>')
def profile(id):

    #userinfo = models.User.query.filter_by(id=id_user)

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

