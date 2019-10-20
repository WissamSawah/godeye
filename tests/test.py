import unittest
import sys


class OpenCVTest(unittest.TestCase):
    """ Simple functionality tests. """

    def test_import(self):
        """ Test that the cv2 module can be imported. """
        import cv2

    def test_video_capture(self):
        """ Test the camera connection. """
        import cv2
        cap = cv2.VideoCapture(0)
        self.assertTrue(cap.isOpened())

    def test_redirectError(self):
        import cv2

        try:
            cv2.imshow("", None) # This causes an assert
            self.assertEqual("Dead code", 0)
        except cv2.error as _e:
            pass

        handler_called = [False]
        def test_error_handler(status, func_name, err_msg, file_name, line):
            handler_called[0] = True

        cv2.redirectError(test_error_handler)
        try:
            cv2.imshow("", None) # This causes an assert
            self.assertEqual("Dead code", 0)
        except cv2.error as _e:
            self.assertEqual(handler_called[0], True)
            pass

        cv2.redirectError(None)
        try:
            cv2.imshow("", None) # This causes an assert
            self.assertEqual("Dead code", 0)
        except cv2.error as _e:
            pass

        





if __name__ == '__main__':
    unittest.main(verbosity=3)
