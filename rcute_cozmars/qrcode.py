import cv2
import numpy as np

class QRCodeRecognizer:
# class QRCodeRecognizer(cv2.QRCodeDetector):
# inheriting from cv2.QRCodeDetector will bring "segment fault (core dumped)" error when used with asyncio.
# took me long time to debug, still unclear why.
# so I had to make cv2.QRCodeDetector a member of this class

    def __init__(self):
        self.detector = cv2.QRCodeDetector()

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

    def recognize(self, img):
        text, points = self.detector.detectAndDecode(img)[:2]
        if points is not None:
            points = points.reshape(-1, 2).astype(int)
        return (points, text) if self.is_square(points) else (None, '')

    def draw_labels(self, img, points, text, color=(0,0,180)):
        if points is not None:
            if text:
                cv2.putText(img, text, (30, 50), cv2.FONT_HERSHEY_DUPLEX, 0.75, color, 1)
            cv2.polylines(img, [points.reshape(-1, 1, 2)], 1, color)
