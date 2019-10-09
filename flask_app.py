import base64
import sys
import tempfile
import cv2
import time
import argparse
# from datetime import datetime
import datetime

import numpy as np
from queue import Queue
from threading import Thread
import threading

MODEL_BASE = 'models/research'
sys.path.append(MODEL_BASE)
sys.path.append(MODEL_BASE + '/object_detection')
sys.path.append(MODEL_BASE + '/slim')

from flask import redirect, flash
from flask import render_template
from flask import request
from flask import Response
from flask import url_for
from flask import session
from flask_wtf.file import FileField
import numpy as np
from PIL import Image
from PIL import ImageDraw
import tensorflow as tf
# from grabscreen import grab_screen

# from utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from werkzeug.datastructures import CombinedMultiDict
from wtforms import Form
from wtforms import ValidationError
from cv2 import imencode
from app_utils import draw_boxes_and_labels
from object_detection.utils import label_map_util
from MySQLdb import escape_string as thwart
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask import Flask, render_template, Response, request, redirect, url_for, session
import re
from bs4 import BeautifulSoup
from itertools import count



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




# Helper Functions
class FPS:
    def __init__(self):
        # store the start time, end time, and total number of frames
        # that were examined between the start and end intervals
        self._start = None
        self._end = None
        self._numFrames = 0

    def start(self):
        # start the timer
        self._start = datetime.datetime.now()
        return self

    def stop(self):
        # stop the timer
        self._end = datetime.datetime.now()

    def update(self):
        # increment the total number of frames examined during the
        # start and end intervals
        self._numFrames += 1

    def elapsed(self):
        # return the total number of seconds between the start and
        # end interval
        return (self._end - self._start).total_seconds()

    def fps(self):
        # compute the (approximate) frames per second
        return self._numFrames / self.elapsed()

class WebcamVideoStream:
    def __init__(self, src, width, height):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.src = src
        self.width = width
        self.height = height

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def init(self):
        self.stream = cv2.VideoCapture(self.src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        (self.grabbed, self.frame) = self.stream.read()

    def start(self):
        # start the thread to read frames from the video stream
        self.camthread = Thread(target=self.update, args=())
        self.camthread.start()
        # WebcamVideoStream.new()
        return self


    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        # if the thread indicator variable is set, stop the thread
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        # self.stream.release()


def is_image():
  def _is_image(form, field):
    if not field.data:
      raise ValidationError()
    elif field.data.filename.split('.')[-1].lower() not in extensions:
      raise ValidationError()

  return _is_image



# Webcam feed Helper
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

# detector for web camera
def detect_objects_webcam(image_np, sess, detection_graph):
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    # screen = cv2.resize((0,40,1280,745), (800,450))
    image_np_expanded = np.expand_dims(image_np, axis=0)
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # Each box represents a part of the image where a particular object was detected.
    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

    # Each score represent how level of confidence for each of the objects.
    # Score is shown on the result image, together with the class label.
    scores = detection_graph.get_tensor_by_name('detection_scores:0')
    classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # Actual detection.
    (boxes, scores, classes, num_detections) = sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_np_expanded})

    # Visualization of the results of a detection.
    rect_points, class_names, class_colors = draw_boxes_and_labels(
        boxes=np.squeeze(boxes),
        classes=np.squeeze(classes).astype(np.int32),
        scores=np.squeeze(scores),
        category_index=client.category_index,
        min_score_thresh=.5,

    )
    for i,b in enumerate(boxes[0]):
        if classes[0][i] == 3 or classes[0][i] == 6 or classes[0][i] == 8:
            if scores[0][i] >= 0.5:
                mid_x = (boxes[0][i][1]+boxes[0][i][3])/2
                mid_y = (boxes[0][i][2]+boxes[0][i][3])/2
                apx_distance = round(((1 - (boxes[0][i][3] - boxes[0][i][1]))**4),1)

                cv2.putText(image_np, '{}'.format(apx_distance), (int(mid_x*800),int(mid_y*450)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                # gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

                if apx_distance == 0:
                    # if mid_x > 0.3 and mid_x < 0.7:
                    # if mid_x > 0.3 and mid_x < 0.7:
                    cv2.putText(image_np, 'WARNING!!!', (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 3)

    return dict(rect_points=rect_points, class_names=class_names, class_colors=class_colors)

# Image class
class PhotoForm(Form):
  input_photo = FileField(
      'File extension should be: %s (case-insensitive)' % ', '.join(extensions),
      validators=[is_image()])

class VideoForm(Form):
    input_video = FileField()

# Obect Dection Class
class ObjectDetector(object):

  def __init__(self):
    self.detection_graph = self._build_graph()
    self.sess = tf.compat.v1.Session(graph=self.detection_graph)

    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(
        label_map, max_num_classes=90, use_display_name=True)
    self.category_index = label_map_util.create_category_index(categories)

  def _build_graph(self):
    detection_graph = tf.Graph()
    with detection_graph.as_default():
      od_graph_def = tf.compat.v1.GraphDef()
      with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    return detection_graph

@app.route('/godeye/index')
def main_display():
	if 'loggedin' in session:
	    photo_form = PhotoForm(request.form)
	    video_form = VideoForm(request.form)
	    #return render_template('main.html', photo_form=photo_form, result={})
	    return render_template('main.html', photo_form=photo_form, video_form=video_form, result={}, username=session['username'])
	return redirect(url_for('login'))

@app.route('/imgproc', methods=['GET', 'POST'])
def imgproc():
  video_form = VideoForm(request.form)
  form = PhotoForm(CombinedMultiDict((request.files, request.form)))
  if request.method == 'POST' and form.validate():
    with tempfile.NamedTemporaryFile() as temp:
      form.input_photo.data.save(temp)
      temp.flush()
      print(temp.name)
      result = detect_objects(temp.name)

    photo_form = PhotoForm(request.form)
    return render_template('main.html',
                           photo_form=photo_form, video_form=video_form, result=result)
  else:
    return redirect(url_for('main_display'))



@app.route('/realproc', methods=['GET', 'POST'])
def realproc():

	# WebcamVideoStream.new()
	return render_template('realtime.html')



@app.route('/realstop', methods=['GET', 'POST'])
def realstop():
    photo_form = PhotoForm(request.form)
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


# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
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

video_init = WebcamVideoStream(src=0, width=480, height=360)
# video_init2 = WebcamVideoStream(src="http://192.168.1.197:8020/videoView", width=480, height=360)

fps_init = FPS()

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

if __name__ == '__main__':

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    # sess.init_app(app)
    app.run(debug=True)
