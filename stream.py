import cv2
from threading import Thread
import threading


class liveStream:
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
        # liveStream.new()
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
