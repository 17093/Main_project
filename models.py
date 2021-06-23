from app import db

RecommendationGenre = db.Table('RecommendationGenre', db.Model.metadata,
                    db.Column('gId', db.Integer, db.ForeignKey('Genre.id')),
                    db.Column('rId', db.Integer, db.ForeignKey('Recommendation.id'))
                    )

class Recommendation(db.Model):
    __tablename__ = 'Recommendation'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    songUrl = db.Column(db.String())
    username = db.Column(db.Integer, db.ForeignKey('User.id'))
    description = db.Column(db.String())

    genres = db.relationship('Genre', secondary=RecommendationGenre, back_populates='recommendations')


class Genre(db.Model):
    __tablename__ = 'Genre'
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String())
    genreDesc = db.Column(db.String())

    recommendations = db.relationship('Recommendation', secondary=RecommendationGenre, back_populates='genres')

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String())
    passWord = db.Column(db.String())
    bio = db.Column(db.String())
    favGenre = db.Column(db.Integer, db.ForeignKey('Genre.id'))

    #db.create_all(extend.existing=True)