import cv2
from cv2 import aruco
import numpy as np

class ArucoDetector:

    def __init__(self):
        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)
        self.parameters = aruco.DetectorParameters_create()

    def angle_between(self, v1, v2):
        return np.arccos(np.clip(np.dot(v1, v2)/np.linalg.norm(v1)/np.linalg.norm(v2), -1, 1))

    def edges(self, pts):
        return [np.linalg.norm(pts[i]-pts[(i+1)%4]) for i in range(4)]

    def is_square(self, pts):
        # pts should be in clock or counterclock wise ordered
        if pts is None:
            return False
        edges = self.edges(pts)
        return (.8 < min(edges) / max(edges) < 1.2) and (.9 < self.angle_between(pts[0]-pts[1], pts[0]-pts[3])*2/np.pi < 1.1)

    def order4points(self, pts):
        xSorted = pts[np.argsort(pts[:, 0]), :]
        leftMost = xSorted[:2, :]
        rightMost = xSorted[2:, :]
        tl, bl = leftMost[np.argsort(leftMost[:, 1]), :]
        tr, br = rightMost[np.argsort(rightMost[:, 1]), :]
        return tr, br, bl, tl

    def detect(self, img):
        mean_c =  cv2.adaptiveThreshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,65,2)
        return aruco.detectMarkers(mean_c, self.aruco_dict, parameters=self.parameters)[:2]

    def draw_labels(self, img, corners, ids):
        aruco.drawDetectedMarkers(img, corners, ids)
