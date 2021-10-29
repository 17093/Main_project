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

@app.route('/recommendation/<int:id>', methods=["GET", "POST"])# selects random music then recommends to user
def recommendation(id):
    logged= False
    # ADD VIEWCOUNT IF CAN
    recommend = models.Recommendation.query.filter_by(id=id).first_or_404() # retrivees the randomly picked song/id

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
        username = session["user"]
        logged = True

    # retrieves userinfo such as; bio and name
        userinfo = models.User.query.filter_by(id=id).first_or_404()
        genre_id = userinfo.favGenre
        favGenre = models.Genre.query.filter_by(id=genre_id).first_or_404()
        return render_template("profile.html", userinfo = userinfo, title="Profile", username = username, logged=logged, favGenre=favGenre, genre_id=genre_id, id=id)

    return redirect(url_for("login"))

@app.route('/genre/<int:id>', methods=["GET","POST"])
def genre(id):
    logged= False
    if "user" in session:
        #id = session.get("user_id") - disabled due to id variable overlapping
        username = session["user"]
        logged = True
        # fetches all genretypes and translates them to genre.html
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


@app.route('/signup', methods=["GET", "POST"])
def signup():
    error = None
    # gathers all genre types
    genre_list = models.Genre.query.all()
    print (genre_list)
    
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        bio = request.form.get("bio")
        favGenre=request.form.get("genre_list")

        # When posted, compares username to already existing usernames
        check_name = models.User.query.filter_by(userName=(username)).first()

        # parameters for valid credentials
        if len(username) <= 0 or len(username) > 20:
            error = "username invalid. Please enter username with lettercount higher than 0 and lower than 20"
        elif len(password) <= 0 or len(password) > 20:
            error = "password invalid. Please enter password with lettercount higher than 0 and lower than 20"
        elif len(bio) > 50:
            error = "Bio invalid. Please enter Bio with lettercount lower than 50"
        elif check_name:
            error = "username already exists, please enter a different username"
            print (error)
        else:
            # commits
            user = models.User(userName=username, passWord = generate_password_hash(password), bio=bio, favGenre=favGenre)
            db.session.add(user)
            db.session.commit()
        return render_template("signup.html", error = error, genre_list = genre_list)

    return render_template("signup.html", genre_list=genre_list)

# logging out of session
@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.route('/upload', methods=["GET", "POST"])
def upload():
    error= None
    uploaded= None
    logged=False
    genre_list = models.Genre.query.all()
    # if user is in session, the website will gather the user's id
    if "user" in session:
        id = session.get("user_id")
        username = session["user"]
        logged = True
        if request.method == 'POST':
            id_list = len(models.Recommendation.query.all())# gets how many songs there are in recommendation database
            # retrieves the form data from the upload url
            
            #favGenre=request.form.get("genre_list")
            # RecommendationUser
            #re_u = models.RecommendationUser()
            #re_u.rId = (id_list + 1)
            #re_u.uId = session.get("user_id")

            # RecommendationGenre
            #re_g = models.RecommendationGenre()
            #re_g.gId = request.form.get("genre_list")
            #re_g.rId = (id_list + 1)

            # Recommendation
            rec = models.Recommendation()
            rec.name = request.form.get("videotitle")
            rec.description = request.form.get("description")
            rec.songType = request.form.get("urltype")

            #re_id = (id_list + 1)
            re_user = models.User.query.get(session.get("user_id"))
            re_genre = models.Genre.query.get(request.form.get("genre_list"))
                

            rec.users.append(re_user)
            rec.genres.append(re_genre)
            

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
                #print (parsed.path)
                # youtube
                if rec.songType == "1":
                    rec.songUrl = urllib.parse.parse_qs(parsed.query).get('v', [None])[0]
                # spotify
                if rec.songType == "2":
                    
                    rec.songUrl = parsed.path[7:]  

                #print(rec.name +" "+ rec.songUrl+" "+ rec.description +" "+ rec.songType+" "+str(re_u.rId))
                # return str(v)

                if rec.songUrl:

                    # adds and commits the information to the recommendation table
                    db.session.add(db.session.merge(rec))
                    db.session.commit()
                    uploaded = "Uploaded :D"
                    
                    
                else:
                    error = "invalid URL"
            return render_template("upload.html", uploaded=uploaded, error = error, logged=logged, id=id, username = username, genre_list=genre_list)
        return render_template("upload.html", logged=logged, id=id, username = username, genre_list=genre_list)
    else:
        return redirect(url_for("login"))


@app.route('/delete', methods=["GET", "POST"])
def delete():
    return render_template("delete.html")

# about page of the website
@app.route('/about')
def about():
    # if user is in session, the website will gather the user's id
    if "user" in session:
        username = session["user"]
        logged = True
        id = session.get("user_id")
        return render_template("about.html", username=username, logged=logged, id=id)
    return render_template("about.html")


if __name__ == '__main__' :
    app.run(debug=True)

