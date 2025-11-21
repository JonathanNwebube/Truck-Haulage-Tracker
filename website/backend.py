from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from . database import User, Job, Days, Week
from . import db
from werkzeug.security import generate_password_hash, check_password_hash #help hash a password from flask_login - hashing a password
from flask_login import login_user, login_required, logout_user, current_user
from datetime import date, datetime
import json


weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day = date.today()
dt = datetime.now()
weekdayNumber = dt.weekday()
weekday = weekdays[weekdayNumber]



# This file is a blueprint of the program, containing multiple routes inside it

backend = Blueprint('backend',__name__) #Defining the name of the blueprint

    ###  AUTHENTICATION ROUTES  ---------------------------------------------------------------------------

@backend.route('/login', methods=['GET', 'POST']) #creating a decorator, when the URL is /login the function below is invoked
def login(): 
    if request.method == 'POST':
        email = request.form.get('email') # request variable when accessed in a route will have information of a request sent to access this route - URL, method, information sent
        password = request.form.get('password')

        # validation that user is in database
        user = User.query.filter_by(email=email).first()  # query database and searching for something in database
        if user:
            if check_password_hash(user.password, password): #hashes password entered and compares it to stored hasehd password
                flash('Logged in successfully!', category ='success')
                login_user(user, remember=True) #remebers user is logged in until flask session over or logs out
                return redirect(url_for('backend.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    
    return render_template("login.html",user=current_user)


@backend.route('/logout') #creating a decorator, when the URL is /logout the function below is invoked
@login_required #decorator - makes sure, this rout is inaccesible unless user is logged in
def logout():
    logout_user() #logs out current user
    flash('Logged out of account', category='success')
    return redirect(url_for('backend.login')) #Brings user back to login page when they've signed out


@backend.route('/CreateAccount', methods=['GET', 'POST']) #creating a decorator, when the URL is /CreateAccount the function below is invoked
def create_account():
    if request.method == 'POST': # differentiate between GET and POST request
        first_name = request.form.get('first_name').capitalize() # .get is used to get a specific attribute from the form
        second_name = request.form.get('second_name').capitalize() # capitalize function used to make first letter a capital 
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        #validation

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
            
        # category allows you to display the message in a different colour
        if len(first_name) < 2:
            flash('First name must be greater than 1 characters', category='error')
        elif len(second_name) <2:
            flash ('Second name must be greater than 1 character', category='error')
        elif len(email)<4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(password) < 7:
            flash('Password must be greater than 6 characters.', category='error')
        elif password != password_confirm:
            flash('Passwords do not match.', category='error')
        else:
            #creating a new user
            new_user = User(first_name=first_name, second_name=second_name, email=email, password=generate_password_hash(password, method='sha256'), manager=False) # Defining a user and defining the password with an ireverisble hash instead of plain text - sha256 is a hashing algorithm
            db.session.add(new_user) # add user to database
            db.session.commit() # update the database
            flash('Account Created', category = 'success')
            login_user(new_user, remember=True)
            return redirect(url_for('backend.home')) # redirect user to homepage of website, home is the function - backend is the name of blueprint, home is the function - do it in this way incase we change the URL path in that function

    return render_template("create_account.html", user=current_user)

    ### OTHER ROUTES ----------------------------------------------------------------------------------------


@backend.route('/') # defining the homepage route - this is a decorator (A decorator is a function that takes in another function as a parameter and then returns a function)
@login_required # decorator - cannot get to the home page unless logged in
def home(): #this function runs when the URL is /
    
    #Have to get last week_no from Week database and increment that number by 1 every time it is a new monday
    weekQuery = Week.query.order_by(Week.id.desc()).first()
    lastMonday = weekQuery.monday_date

    if str(day) != str(lastMonday) and weekday=="Monday":
        week = weekQuery.week_no
        week += 1
        new_week = Week(week_no=week, monday_date=date.today())
        db.session.add(new_week)
        db.session.commit()
            
    return render_template("home.html", user = current_user) #will be able to reference the current user and check if it is authentic


@backend.route('/EditSchedules', methods=['GET','POST']) # defining the route for the manager to edit the drivers schedules
@login_required # decorator so that you cannot access schedules without being logged in
def edit_schedules():#when the URL path is /EditSchedules then this function is ran
    
    driver = User.query.order_by(User.first_name)   # sort the drivers into alphabetical order, more professional than before
    if request.method == 'POST':
        # allow the field information from the form to be accessed by other functions
        global driverEdit
        global driverEditID

        ### Before the driver submitted would show as < User 7 >
        ### used to record the user selected in the form from 'edit_schedules.html' file to save in database
        driverSelect = request.form.get('drivers') #saves the user input from webpage     
        sliceDriverEdit = driverSelect [6:] # slices the variable value 
        sliceDriverEdit = sliceDriverEdit[:1] #slices the variable again
        driverEdit = User.query.filter_by(id=sliceDriverEdit).first() #queries for the user with the correct id
        driverEditID = driverEdit.id
        driverEdit = driverEdit.first_name
        
        return redirect(url_for('backend.schedules'))
 
    return render_template("edit_schedules.html", user=current_user, drivers=driver, day=day, weekday=weekday, weekdays = weekdays) #will be able to reference the current user and check if it is authentic
    

@backend.route('/AddSchedule', methods=['GET', 'POST'])
@login_required
def schedules():
    if request.method == 'POST':
        date = request.form.get('date')
        time = request.form.get('time') # .get is used to get a specific attribute from the form
        tractorID = request.form.get('tractorID')  
        start_location = request.form.get('start_location').capitalize() # capitalize function used to make first letter a capital
        end_location = request.form.get('end_location').capitalize() # capitalize function used to make first letter a capital

        ### Validation
        if date == "":
            flash('Must select a date', category='error')
        elif time == "":
            flash('Must enter a time', category='error')
        elif tractorID == "":
            flash('Must enter a tractorID', category='error')
        elif start_location == "":
            flash('Must enter the start location', category='error')
        elif end_location =="":
            flash('Must enter the end location', category='error')
        else:
            new_job = Job(date=date, time=time, tractorID=tractorID, 
                          start_location=start_location, end_location=end_location, 
                          user = driverEdit, user_id = driverEditID)
            db.session.add(new_job) # add user to database
            db.session.commit() # update the database
            flash('Schedule updated', category = 'success')
            return redirect(url_for('backend.view_schedule'))

    return render_template('schedule_days.html',  user = current_user)


@backend.route('/ViewSchedule', methods=['GET', 'POST'])
@login_required
def view_schedule():
    
    job = Job.query.order_by(Job.date).all()
    jobLen = len(job)
    driver = User.query.all()

    if request.method == 'POST': 
        specificDriver = request.form.get('drivers')
        if specificDriver != None:
            sliceSpecificDriver = specificDriver [6:] # slices the variable value 
            sliceSpecificDriver = sliceSpecificDriver[:1] #slices the variable again
            specificDriver = User.query.filter_by(id=sliceSpecificDriver).first()
            specificDriver = specificDriver.first_name
        else:
            specificDriver = 'blank'



        # specificDate = request.form.get('date')
        # if specificDate == "":
        #     specificDate = None

    

        return redirect(url_for('backend.specific_schedule', specificDriver=specificDriver,))
        
    return render_template("view_schedule.html", user = current_user, jobs = job, drivers=driver, day=day, weekday=weekday, jobLen=jobLen)


@backend.route('/<specificDriver>_schedule', methods=['GET', 'POST'])
@login_required
def specific_schedule(specificDriver):

    
    job = Job.query.order_by(Job.date).filter_by(user=specificDriver).all()
    jobLen=len(job)


    return render_template("specific_schedule.html", user=current_user, jobs = job, specificDriver = specificDriver, day=day, jobLen=jobLen, weekday=weekday)


@backend.route('/ChooseDriverForHours', methods = ['GET','POST'])
@login_required
def hours_driver():

    weekQuery = Week.query.order_by(Week.id.desc()).first()
    weekNumber = weekQuery.week_no
    driver = User.query.all()
    if request.method == 'POST': 
        global timeSheetDriver
        global timeSheetDriverID

        timeSheetDriver = request.form.get('drivers')
        sliceTimeSheetDriver = timeSheetDriver [6:] # slices the variable value 
        sliceTimeSheetDriver = sliceTimeSheetDriver[:1] #slices the variable again
        timeSheetDriver = User.query.filter_by(id=sliceTimeSheetDriver).first()
        timeSheetDriverID = timeSheetDriver.id
        timeSheetDriver = timeSheetDriver.first_name

    
        return redirect(url_for('backend.hours_worked'))

    return render_template('hours_driver.html',  user=current_user, drivers=driver, day=day, weekday=weekday, weekNumber = weekNumber)


@backend.route('/HoursWorked', methods = ['GET', 'POST'])
@login_required
def hours_worked():

    weekNumber = Week.query.order_by(Week.id.desc()).first()
    weekNumber = weekNumber.week_no
    

    if request.method == 'POST':
        monday = request.form.get('monday')
        tuesday = request.form.get('tuesday')
        wednesday = request.form.get('wednesday')
        thursday = request.form.get('thursday')
        friday = request.form.get('friday')
        saturday = request.form.get('saturday')
        sunday = request.form.get('sunday')

        if monday == "":
            monday = 0
        if tuesday == "":
            tuesday = 0 
        if wednesday == "":
            wednesday = 0
        if thursday == "":
            thursday = 0
        if friday == "":
            friday = 0
        if saturday == "":
            saturday = 0
        if sunday == "":
            sunday = 0
        
        #updating the schedule
        new_hours = Days(week=weekNumber, monday=monday, tuesday=tuesday, wednesday=wednesday, thursday=thursday, friday=friday, saturday=saturday, sunday=sunday, user=timeSheetDriver, user_id = timeSheetDriverID) # Defining a user and defining the password with an ireverisble hash instead of plain text - sha256 is a hashing algorithm
        db.session.add(new_hours) # add user to database
        db.session.commit() # update the database
        
    return render_template("hours_worked.html", user=current_user, weekday = weekday, day=day, weekNumber=weekNumber)

@backend.route('/delete-job', methods=['POST'])
def delete_job():  
    job = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    jobId = job['jobId']
    job = Job.query.get(jobId)
    print (job)
    if job:
        db.session.delete(job)
        db.session.commit()

    return jsonify({})

@backend.route('/Calendar', methods=['GET', 'POST'])
@login_required
def calendar():

    if request.method == 'POST':
        date = request.form.get('date')
        if date == "":
            flash('Must select a date', category='error')
        else:
            print(date)
            date = str(date)
            job = Job.query.order_by(Job.date).filter_by(date=date).all()
            print(job)
            

    return render_template("calendar.html", user = current_user)

# def calculateHours():
#     pass