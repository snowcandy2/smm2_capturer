#-*- coding=utf-8 -*-
import time

import camera as theCam
import logging
import cv2
import numpy as np



class Identifier:
    def __init__(self, camera):
        assert isinstance(camera, theCam.Camera)
        self.camera = camera
        self.frame = self.camera.getFrame()

    def output(self, filename):
        cv2.imencode('.png', self.frame)[1].tofile(filename)
        # cv2.imwrite(filename, self.frame)

    def output_part(self, filename, x, y, dx, dy):
        cv2.imwrite(filename, self.getPart(x, y, dx, dy))

    def refresh(self):
        self.frame = self.camera.getFrame()

    def Print(self):
        cv2.imshow("result", self.frame)

    def getPart(self, x, y, dx, dy):
        frame = self.frame
        part = frame[y:y+dy, x:x+dx]
        return part

    def getGrayColor(self, x, y):
        img = self.frame
        img_gray = 0.2126*img[:,:,2] + 0.7152*img[:,:,1] + 0.0722*img[:,:,0]
        return img_gray[y, x]

    def findPicture(self, picture, dontgetgray=False, part=None):
        # print(picture,),
        if isinstance(picture, str): # 提供路径的话把picture改为图片
            picture = cv2.imread(picture, 1)
        if isinstance(part, list) and len(part) == 4:
            cam_result = self.getPart(part[0], part[1], part[2], part[3]) # (31, 633, 40, 40)
        else:
            cam_result = self.frame
        if not dontgetgray:
            cam_result = cv2.cvtColor(cam_result, cv2.COLOR_BGR2GRAY)
        picture_gray = cv2.cvtColor(picture, cv2.COLOR_BGR2GRAY) if not dontgetgray else picture
        # cv2.imwrite("./debug/picture_gray_%d.jpg" % time.time(), picture_gray)
        res = cv2.matchTemplate(cam_result, picture_gray, cv2.TM_CCOEFF_NORMED)
        # cv2.imwrite("./debug/cam_result_%d.jpg" % time.time(), cam_result)
        # if cv2.minMaxLoc(res)[1] <= 0.0:
        #     cv2.imwrite("./debug/cam-res.png", cam_result)
        #     cv2.imwrite("./debug/picture-gray.png", picture_gray)
        return {
            "min": cv2.minMaxLoc(res)[0],
            "max": cv2.minMaxLoc(res)[1],
            "min_loc": cv2.minMaxLoc(res)[2],
            "max_loc": cv2.minMaxLoc(res)[3],
        }

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                        filename='identify_log.log', level=logging.INFO)
    vcam = theCam.Camera()
    id2 = Identifier(vcam)
    while True:
        time.sleep(0.5)
        r = id2.findPicture('./sub_image/you_win.png')
        if r['max'] > 0.78:
            logging.info("'You win' detected. ")
        r = id2.findPicture('./sub_image/you_lose.png')
        if r['max'] > 0.78:
            logging.info("'You lose' detected. ")

