# God's Eye Web application

## Introduction
This software will oversee a area by using camera feed(Webcam or ip camera) where autonomous vehicles are operating. The software will be able to recognize what is on the feed, and it will notify the user in case of a fault or collision between the autonomous vehicles. In this webb application you will be able to navigate between three different pages, Home, Profile and Logut to logout from the system.

## Packages and how to run
In case to run this application you will have to clone/download this repo and install all the packages in requirments.txt or run the following command `pip3 install -r requirements.txt ` make sure that you also have pip3 and python3 installed before you run this command. You will also need a connection to SQL to be able to execute the setup.sql file. Once you downloaded the repo and the packages open a terminal inside the directory and run this commando `export DYLD_LIBRARY_PATH=/usr/local/mysql/lib:$DYLD_LIBRARY_PATH` this will put some files in the right place in case to run the sql code. Finally run `python3 flask_app.py` to start the program.

## Avaliable routes

The software is running on localhost 5000.

- Login page 
  http://0.0.0.0:5000/godeye/login

- Registration page
  http://0.0.0.0:5000/godeye/register
  
- Landing page 
  http://0.0.0.0:5000/godeye/index
  
- The camera software inside the webb application 
  http://0.0.0.0:5000/godeye/realproc
  
- The camera software (Outside the application) Camera 1 
  http://0.0.0.0:5000/realpros
  
- The camera software (Outside the application) Camera 2 
  http://0.0.0.0:5000/realpros2
  
