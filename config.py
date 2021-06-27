import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'epicbreadmanfish'
    project_dir = os.path.dirname(os.path.abspath(__file__))
    database = "sqlite:///{}".format(os.path.join(project_dir, "recommendation.db"))
    #SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL') or 'recommendation.db'
    SQLALCHEMY_DATABASE_URI = database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"
