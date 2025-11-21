#This file is where the program is to be ran from

from website import create_app #importing website package from __init.py__ to create an application and run it
# Website folder is a python package so when imported it will run all files in folder

app = create_app() # Function in the __init__.py file

# This runs a flask application
if __name__ == '__main__': # Only when this file is ran the following line is executed
    app.run(debug=True) # Starts a web server 
                        # debug=True change in code will auto rerun web server  