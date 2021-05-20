import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'epicbreadmanfish'
    SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL') or 'recommendation.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
