import base64
import sys
import cv2
import time
import datetime
import re

import numpy as np
from queue import Queue
from threading import Thread
import threading

from fps import FPS
from stream import liveStream
from detector import ObjectDetector
from objects import detect_objects_webcam

MODEL_BASE = 'models/research'
sys.path.append(MODEL_BASE)
sys.path.append(MODEL_BASE + '/object_detection')
sys.path.append(MODEL_BASE + '/slim')

from flask import Flask, redirect, flash, render_template, request, Response, url_for, session, session

from flask_wtf.file import FileField
import numpy as np
from PIL import Image
from PIL import ImageDraw
import tensorflow as tf
# from grabscreen import grab_screen

# from utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from werkzeug.datastructures import CombinedMultiDict
from wtforms import Form, ValidationError
from cv2 import imencode
from app_utils import draw_boxes_and_labels
from object_detection.utils import label_map_util
from MySQLdb import escape_string as thwart
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
import MySQLdb.cursors


app = Flask(__name__)

app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'wissamsy81@gmail.com',
	MAIL_PASSWORD = '0936065947'
	)
mail = Mail(app)

app.secret_key = 'GANT1949'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'wesam1995'
app.config['MYSQL_DB'] = 'pythonlogin'

mysql = MySQL(app)


PATH_TO_CKPT = 'frozen_inference_graph.pb'
PATH_TO_LABELS = 'mscoco_label_map.pbtxt'

content_types = {'jpg': 'image/jpeg',
                 'jpeg': 'image/jpeg',
                 'png': 'image/png'}
extensions = sorted(content_types.keys())




def worker(input_q, output_q):
    detection_graph = client.detection_graph
    sess = client.sess
    fps = FPS().start()
    while True:
        fps.update()
        frame = input_q.get()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output_q.put(detect_objects_webcam(frame_rgb, sess, detection_graph))
        # print(frame_rgb)

    fps.stop()
    sess.close()


class VideoForm(Form):
    input_video = FileField()

# registration, login, logout


@app.route('/godeye/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        image = request.form['image']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE username = %s", [username])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s)', ([image], [username], [password], [email]))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


@app.route('/godeye/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    session.permanent = False
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
         # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            send_mail()
            flash('You were successfully logged in ' + username)
            return redirect(url_for('main_display'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)



@app.route('/godeye/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))



@app.route('/godeye/profile')
def profile4():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/godeye/index')
def main_display():
	if 'loggedin' in session:
	    video_form = VideoForm(request.form)
	    #return render_template('main.html', photo_form=photo_form, result={})
	    return render_template('main.html', photo_form=photo_form, video_form=video_form, result={}, username=session['username'])
	return redirect(url_for('login'))


# Camera image processing

@app.route('/godeye/realproc', methods=['GET', 'POST'])
def realproc():

	# liveStream.new()
	return render_template('realtime.html')



@app.route('/realstop', methods=['GET', 'POST'])
def realstop():
    video_form = VideoForm(request.form)
    if request.method == 'POST':
        print("In - Stop - POST")
        if request.form['realstop'] == 'Stop Web Cam':
            print(request.form['realstop'])
            fps_init.stop()
            video_init.stop()
            video_init.update()
            print("Stopped")
    return render_template('main.html', photo_form=photo_form, video_form=video_form)



@app.route('/send-mail/')
def send_mail():
    try:
        msg = Message("Send Mail Tutorial!",
            sender="wissamsy81@gmail.com",
            recipients=["wesam.sawah@me.com"])
        msg.body = 'Hello Waleed!\n\nIt looks like someone just logged into your God`s Eye system\n\n The login time is: {}'.format(datetime.datetime.now()).split('.')[0]
        mail.send(msg)
        return 'Mail sent!'
    except Exception:
        return("error")

# Just camera without the interface incase someone wanna use it to another application.

@app.route('/realpros')
def realpros():
    print("in real pros")
    input_q = Queue(5)
    output_q = Queue()
    for i in range(1):
        t = Thread(target=worker, args=(input_q, output_q))
        t.daemon = True
        t.start()

    video_init.init()
    video_capture = video_init.start()
    fps = fps_init.start()
    def generate():
        # print("in gen real pros")
        frame = video_capture.read()

        while video_capture.grabbed:
            # print("in while gen real pros")
            input_q.put(frame)
            t = time.time()

            if output_q.empty():
                pass
            else:
                font = cv2.FONT_HERSHEY_SIMPLEX
                data = output_q.get()
                rec_points = data['rect_points']
                class_names = data['class_names']
                class_colors = data['class_colors']
                for point, name, color in zip(rec_points, class_names, class_colors):
                    cv2.rectangle(frame, (int(point['xmin'] * 480), int(point['ymin'] * 360)),
                                  (int(point['xmax'] * 480), int(point['ymax'] * 360)), color, 3)
                    cv2.rectangle(frame, (int(point['xmin'] * 480), int(point['ymin'] * 360)),
                                  (int(point['xmin'] * 480) + len(name[0]) * 6,
                                   int(point['ymin'] * 360) - 10), color, -1, cv2.LINE_AA)
                    cv2.putText(frame, name[0], (int(point['xmin'] * 480), int(point['ymin'] * 360)), font,
                                0.3, (0, 0, 0), 1)

                payload = cv2.imencode('.jpg', frame)[1].tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + payload + b'\r\n')
                frame = video_capture.read()
                detection_graph = client.detection_graph
                sess = client.sess
                detect_objects_webcam(frame, sess, detection_graph)
                # centers=[]
            fps.update()
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


client = ObjectDetector()

video_init = liveStream(src=0, width=480, height=360)
# video_init2 = liveStream(src="http://192.168.1.197:8020/videoView", width=480, height=360)

fps_init = FPS()

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

if __name__ == '__main__':

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    # sess.init_app(app)
    app.run(debug=True)
