from . import db # importing from the package db which is in the init file
from flask_login import UserMixin # custom class to inherit giving user object specific things to login

# Creating a table for the schedule days
class Week(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    week_no = db.Column(db.Integer)
    monday_date = db.Column(db.String)
    

class Days(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    week = db.Column(db.Integer)
    monday = db.Column(db.Integer)
    tuesday = db.Column(db.Integer)
    wednesday = db.Column(db.Integer)
    thursday = db.Column(db.Integer)
    friday = db.Column(db.Integer)
    saturday = db.Column(db.Integer)
    sunday = db.Column(db.Integer)
    user = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


#Creating a table for the schedules
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String)
    time = db.Column(db.String)
    tractorID = db.Column(db.String(20))
    start_location = db.Column(db.String(150))
    end_location = db.Column(db.String(150))
    user = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


#Creating a table for user information using a class object
class User (db.Model, UserMixin): #UserMixin used for implementations of this objects properties 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True) #Identifies this column as the primary key
    password = db.Column(db.String(150)) #Creates a column for password that accepts strings
    first_name = db.Column(db.String(150)) #Sets first_name character limit to 150
    second_name = db.Column(db.String(150))
    manager = db.Column(db.Boolean) #True when account level is manager False when it is not
    jobs = db.relationship('Job')
    hours = db.relationship('Days')

