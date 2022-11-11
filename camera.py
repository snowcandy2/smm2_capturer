#-*- coding=utf-8 -*-
import logging
import cv2
import numpy as np

CAMERA_ID = 5  # obs camera

class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(CAMERA_ID)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

    def __delete__(self, instance):
        self.cap.release()
        cv2.destroyAllWindows()


    def test_camera(self):
        logging.info("Start Camera Test")
        while True:
            ret, frame = self.cap.read()
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.cap.release()
        cv2.destroyAllWindows()

    def screenshot(self):
        ret, frame = self.cap.read()
        cv2.imwrite("capture.jpg", frame)

    def getFrame(self):
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                        filename='logger.log', level=logging.INFO)
    cam = Camera()
    cam.test_camera()