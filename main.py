# coding:utf-8
from __future__ import division
import math
import sys

import PySide.QtGui as QtGui
import PySide.QtCore as QtCore


class vector2d(object):
    def __init__(self, x=None, y=None):
        super(vector2d, self).__init__()
        self._x = None
        self._y = None

        self.x = x
        self.y = y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, _x=None):
        try:
            temp = float(_x)
        except Exception:
            raise
        else:
            self._x = temp

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, _y=None):
        try:
            temp = float(_y)
        except Exception:
            raise
        else:
            self._y = temp

    def mod(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalize(self):
        self.x = self.x / self.mod()
        self.y = self.y / self.mod()
        return self

    def __repr__(self):
        return "<vector2d({},{})>".format(self.x, self.y)


def angleBetween(v1, v2):
    dot = v1.x * v2.x + v1.y * v2.y
    return math.acos(dot / (v1.mod() * v2.mod()))


def findVectorBetween(v1, angle, revert=True):
    if revert:
        tempAngle = -angle * math.pi / 180
    else:
        tempAngle = angle * math.pi / 180

    return vector2d(v1.x * math.cos(tempAngle) - v1.y * math.sin(tempAngle),
                    v1.y * math.cos(tempAngle) - v1.x * math.sin(tempAngle)).normalize()


class Protractor(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Protractor, self).__init__(parent)

        self._opacity = 1

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint |
                            QtCore.Qt.CustomizeWindowHint |
                            QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setCursor(QtCore.Qt.CrossCursor)
        self.setMouseTracking(True)

        desktop = QtGui.QApplication.instance().desktop()
        desktop.resized.connect(self._fit_screen_geometry)
        desktop.screenCountChanged.connect(self._fit_screen_geometry)

        self.beginPos = None
        self.crossPos = None
        self.endPos = None

        self._fit_screen_geometry()

    def paintEvent(self, event):
        """
        Paint event
        """
        painter = QtGui.QPainter(self)

        current_pos = self.mapFromGlobal(QtGui.QCursor.pos())
        # if self.beginPos:
        #     # 画个点
        #     beginPos = self.mapFromGlobal(self.beginPos)
        #     painter.setPen(QtGui.QColor(0, 0, 0))
        #     painter.setBrush(QtCore.Qt.red)
        #     painter.drawEllipse(beginPos, 2, 2)
        #     painter.drawLine(current_pos, beginPos)
        #
        #     if self.crossPos:
        #         crossPos = self.mapFromGlobal(self.crossPos)
        #         painter.drawEllipse(crossPos, 2, 2)
        #         painter.drawLine(crossPos, beginPos)
        #         painter.drawLine(current_pos, crossPos)
        #
        #         if self.endPos:
        #             endPos = self.mapFromGlobal(self.endPos)
        #             painter.drawEllipse(self.endPos, 2, 2)
        #             painter.drawLine(endPos, crossPos)

        print(self.beginPos, self.crossPos, self.endPos)

    def keyPressEvent(self, event):
        """
        Key press event
        """
        # for some reason I am not totally sure about, it looks like
        # pressing escape while this dialog is active crashes Maya.
        # I tried subclassing closeEvent, but it looks like the crashing
        # is triggered before the code reaches this point.
        # by sealing the keypress event and not allowing any further processing
        # of the escape key (or any other key for that matter), the
        # behaviour can be successfully avoided.

        # TODO: See if we can get the behacior with hitting escape back
        # maybe by manually handling the closing of the window? I tried
        # some obvious things and weren't successful, but didn't dig very
        # deep as it felt like a nice-to-have and not a massive priority.

        pass

    def mousePressEvent(self, event):
        """
        Mouse click event
        """
        if event.button() == QtCore.Qt.LeftButton:
            # Begin click drag operation
            if not self.beginPos:
                self.beginPos = event.globalPos()
            elif not self.crossPos:
                self.crossPos = event.globalPos()
            elif not self.endPos:
                self.endPos = event.globalPos()
            else:
                self.beginPos = event.globalPos()
                self.crossPos = None
                self.endPos = None

    def mouseReleaseEvent(self, event):
        """
        Mouse release event
        """
        # if event.button() == QtCore.Qt.LeftButton and self._click_pos is not None:
        #     # End click drag operation and commit the current capture rect
        #     self._capture_rect = QtCore.QRect(self._click_pos,
        #                                       event.globalPos()).normalized()
        #     self._click_pos = None
        # self.close()
        pass

    def mouseDoubleClickEvent(self, event):
        self.close()

    def mouseMoveEvent(self, event):
        """
        Mouse move event
        """
        self.update()

    def _fit_screen_geometry(self):
        # Compute the union of all screen geometries, and resize to fit.
        desktop = QtGui.QApplication.instance().desktop()
        workspace_rect = QtCore.QRect()
        for i in range(desktop.screenCount()):
            workspace_rect = workspace_rect.united(desktop.screenGeometry(i))
        self.setGeometry(workspace_rect)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    do = Protractor()
    do.exec_()
    sys.exit(app.exec_())
