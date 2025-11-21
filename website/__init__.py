from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# the name of this file makes the folder 'website' a python package 

db = SQLAlchemy() # defining a new database - this line initialises it - an object
DB_NAME = 'database.db' # returns the name of a specified database


# Creating an instance of the Flask class
def create_app():
    app = Flask(__name__) # initialising the app, __name__ used so that Flask knows where to look for templates etc...
    app.config['SECRET_KEY'] = 'sfibdjkfhb hdfjbs' # This is to sign session cookies for protection
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' #SQLAlchemy is stored in this location 
    db.init_app(app) # initialise the database by giving it the flask app


    # registering blueprints in this file and showing where the differnt URLs for the application are
    from .backend import backend #importing the blueprint backend from the file backend.py
    
    # Shows how to access all the URLs from the corresponding blueprints
    app.register_blueprint(backend, url_prefix='/') #sets the prefix of a URL to /: when creating different routes don't need to add / everytime before the rest of the URL

 
    from .database import User
     
    #creating a database - sql now automatically does this and eliminates need for the create_database function
    with app.app_context():
        db.create_all()
    
    login_manager = LoginManager()
    login_manager.login_view = 'backend.login' #where flask should redirect page when user is not logged in
    login_manager.init_app(app) #tells LoginManager which app is being used

    # Tells flask how to load a user - what user is being looked for, by refrencing their id
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id)) # Going to look for primary key and check it is equal to what is passed
    
    return app
