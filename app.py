# imports
from flask import Flask, render_template, g, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey, insert, delete
from config import Config
import random
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import urllib
from urllib.parse import urlparse


# https://www.youtube.com/watch?v=RHu3mQodroM - Login system help
# https://www.youtube.com/watch?v=F0UP2jQL_AA - youtube background help
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

import models #importing model file

# https://jinja.palletsprojects.com/en/3.0.x/templates/

@app.route('/', methods=["GET", "POST"])#homepage/landing page
def home():
    username = ""
    logged = False
    # if user is in the session, they will be greeted by the welcome text and change login button to logout
    if "user" in session:
        username = session["user"]
        logged = True
        id = session.get("user_id")
        return render_template("home.html", title="Home", username=username, logged=logged, id=id)
    return render_template("home.html", title="Home", logged=logged)



@app.route('/randomiser')
def randomiser():
    # number of songs within database
    id_list = len(models.Recommendation.query.all())# gets how many songs there are to recommend
    id_song = random.randint(1,id_list)# picks random id
    print(id_song) # debug

    return redirect(url_for("recommendation", id=id_song))

@app.route('/recommendation/<int:id>', methods=["GET", "POST"])#selects random music then recommends to user
def recommendation(id):
    logged= False
    # ADD VIEWCOUNT IF CAN
    recommend = models.Recommendation.query.filter_by(id=id).first_or_404() #retrivees the randomly picked song/id

    # detecting the type of the song(spotify or youtube link)
    if recommend.songType == 1:
        type_link = 1   
    if recommend.songType == 2:
        type_link = 2
    if "user" in session:
        username = session["user"]
        logged = True
        id = session.get("user_id")
        return render_template("recommendation.html", recommend = recommend, type_link = type_link, title="Recommendation", username=username, logged=logged, id=id)
    print(recommend)
    return render_template("recommendation.html", recommend = recommend, type_link = type_link, title="Recommendation", logged=logged)


@app.route('/profile/<int:id>', methods=["GET", "POST"])
def profile(id):
    logged= False
    # if not logged in, rediredct to login
    if "user" in session:
        #id = session.get("user_id")
        username = session["user"]
        logged = True
    # retrieves userinfo such as; bio and name

    # html comment<!-- Favourite Genres: {% for genre in userinfo.favGenre %}<a href="/genre/{{ genre.id }}">{{ genre }}</a>,&nbsp;{% endfor %} -->
        userinfo = models.User.query.filter_by(id=id).first_or_404()
        return render_template("profile.html", userinfo = userinfo, title="Profile", username = username, logged=logged)
    return redirect(url_for("login"))

@app.route('/genre/<int:id>', methods=["GET","POST"])
def genre(id):
    logged= False
    if "user" in session:
        #id = session.get("user_id") - disabled due to id variable overlapping
        username = session["user"]
        logged = True
        genreinfo = models.Genre.query.filter_by(id=id).first_or_404()
        return render_template("genre.html", logged=logged, username = username, genreinfo=genreinfo)
    
    genreinfo = models.Genre.query.filter_by(id=id).first_or_404()
    return render_template("genre.html", logged=logged, genreinfo=genreinfo)


@app.route('/login', methods=["GET", "POST"])
def login():
    # no error
    error = None
    if "user" in session:
        session.pop("user", None)
    # when html retrieves input it compares input to existing credentials from the database
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        results = models.User.query.filter_by(userName=username).first() 
        # if the credentials match, redirects user to home, if not display error message
        if results and check_password_hash(results.passWord, password):
            session["user"] = username
            session["user_id"] = results.id
            print (session["user_id"])
            return redirect(url_for("home"))
        else:
            error = "Invalid credentials, please try again"

    return render_template('login.html', error = error, title="Login")


@app.route('/signup')
def signup():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = models.User(userName=username, passWord = generate_password_hash(password))
        # commit shit
    return render_template("signup.html")

# logging out of session
@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

# error message for no url make
@app.route('/upload', methods=["GET", "POST"])
def upload():
    error= None
    logged=False
    if "user" in session:
        id = session.get("user_id")
        username = session["user"]
        logged = True
        if request.method == 'POST':
            id_list = len(models.Recommendation.query.all())# gets how many songs there are in recommendation database
            # retrieves the form data from the upload url
            

            re_u = models.RecommendationUser
            re_u.rId = (id_list + 1)
            re_u.uId = session.get("user_id")

            rec = models.Recommendation()
            rec.name = request.form.get("videotitle")
            rec.description = request.form.get("description")
            rec.songType = request.form.get("urltype")
            print(rec.name +" "+ rec.description +" "+ rec.songType)
            # https://stackoverflow.com/questions/31170220/python-split-url-into-its-components
            # https://stackoverflow.com/questions/449775/how-can-i-split-a-url-string-up-into-separate-parts-in-python/449782
            # https://stackoverflow.com/questions/63093132/regex-string-to-capture-a-tracks-spotify-uri-or-web-link

            if len(rec.name) > 30 or len(rec.description) > 100:
                error = "Title or Description too long, please shorten to under 50 characters"
            elif len(rec.name) == 0 or len(rec.description) == 0:
                error = "Title or Description too short, please enter something into the bar"
            else:

                parsed = urllib.parse.urlparse(request.form.get("url"))
                # print (parsed.path)
                # youtube
                if rec.songType == "1":
                    rec.songUrl = urllib.parse.parse_qs(parsed.query).get('v', [None])[0]
                # spotify
                if rec.songType == "2":
                    
                    rec.songUrl = parsed.path[7:]
                # print (rec.songUrl)
                
                    
                
                # print(rec.name +" "+ rec.songUrl+" "+ rec.description +" "+ rec.songType+" "+str(re_u.rId))

                # return str(v)
                if rec.songUrl:

                    # adds and commits the information to the recommendation table
                    db.session.add(rec)
                    # db.session.add(re_u)
                    db.session.commit()
                else:
                    error = "invalid URL"
            return render_template("upload.html", error = error, logged=logged, id=id, username = username)
        return render_template("upload.html", logged=logged, id=id, username = username)
    else:
        return redirect(url_for("login"))


@app.route('/delete', methods=["GET", "POST"])
def delete():
    return render_template("delete.html")


@app.route('/about')
def about():
    if "user" in session:
        username = session["user"]
        logged = True
        id = session.get("user_id")
        return render_template("about.html", username=username, logged=logged, id=id)
    return render_template("about.html")


if __name__ == '__main__' :
    app.run(debug=True)

