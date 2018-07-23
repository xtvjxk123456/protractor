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

    def __add__(self, vector):
        if isinstance(vector, vector2d):
            return vector2d(self.x + vector.x, self.y + vector.y)
        else:
            raise TypeError("can not add with{}".format(vector))

    def __mul__(self, value):
        if isinstance(value, (int, float)):
            return vector2d(self.x * value, self.y * value)
        else:
            raise TypeError("can not mul with{}".format(value))

    def __repr__(self):
        return "<vector2d({},{})>".format(self.x, self.y)


def angleBetween(v1, v2):
    dot = v1.x * v2.x + v1.y * v2.y
    return math.acos(dot / (v1.mod() * v2.mod()))
    # 弧度


def findVectorBetween(v1, angle, revert=True):
    if revert:
        tempAngle = -angle * math.pi / 180
    else:
        tempAngle = angle * math.pi / 180

    return vector2d(v1.x * math.cos(tempAngle) - v1.y * math.sin(tempAngle),
                    v1.y * math.cos(tempAngle) - v1.x * math.sin(tempAngle)).normalize()


def _get_point_in_half_angle(begin, cross, end):
    v1 = vector2d(begin.x() - cross.x(), begin.y() - cross.y())
    v2 = vector2d(end.x() - cross.x(), end.y() - cross.y())
    v1.normalize()
    v2.normalize()

    half_vector = v1 + v2
    half_vector = half_vector*50.0
    # half_vector.normalize()
    # half_vector = half_vector * 50
    return QtCore.QPoint(cross.x() + half_vector.x, cross.y() + half_vector.y)


class Protractor(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Protractor, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint |
                            QtCore.Qt.CustomizeWindowHint |
                            QtCore.Qt.Tool)
        # 设置透明背景，在本例中必须保证有一定的颜色，否则会成为全透明，geometry可能就不对劲了
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        # self.setWindowOpacity(0.2)
        # setWindowOpacity会影响全部的整体，不是合适的方法
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
        painter.setRenderHint(painter.Antialiasing)

        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 1))
        # fillRect 不错，可以绘制背景，将alpha 设置为不为0的值即可
        # painter.setCompositionMode(painter.CompositionMode_Source)
        # 合成模式貌似对本例没啥作用

        if self.beginPos and not self.crossPos and not self.endPos:
            # 画个点
            beginPos = self.mapFromGlobal(self.beginPos)
            painter.setPen(QtGui.QColor(0, 0, 0))
            painter.setBrush(QtCore.Qt.red)
            painter.drawEllipse(beginPos, 2, 2)
            current_pos = self.mapFromGlobal(QtGui.QCursor.pos())
            painter.drawLine(current_pos, beginPos)

        if self.beginPos and self.crossPos and not self.endPos:
            beginPos = self.mapFromGlobal(self.beginPos)
            crossPos = self.mapFromGlobal(self.crossPos)

            painter.setPen(QtGui.QColor(0, 0, 0))
            painter.setBrush(QtCore.Qt.red)
            painter.drawEllipse(beginPos, 2, 2)
            painter.drawLine(crossPos, beginPos)

            painter.drawEllipse(crossPos, 2, 2)
            current_pos = self.mapFromGlobal(QtGui.QCursor.pos())
            painter.drawLine(current_pos, crossPos)

            _p = _get_point_in_half_angle(beginPos, crossPos, current_pos)
            print(_p)
            painter.drawEllipse(_p, 5, 5)
            painter.drawLine(crossPos,_p)

        if self.beginPos and self.crossPos and self.endPos:
            beginPos = self.mapFromGlobal(self.beginPos)
            crossPos = self.mapFromGlobal(self.crossPos)
            endPos = self.mapFromGlobal(self.endPos)

            painter.setPen(QtGui.QColor(0, 0, 0))
            painter.setBrush(QtCore.Qt.red)
            painter.drawEllipse(beginPos, 2, 2)
            painter.drawLine(crossPos, beginPos)

            painter.drawEllipse(crossPos, 2, 2)

            painter.drawEllipse(self.endPos, 2, 2)
            painter.drawLine(endPos, crossPos)

            # _p = _get_point_in_half_angle(beginPos, crossPos, endPos)
            # painter.drawEllipse(_p, 2, 2)

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
    do.show()
    sys.exit(app.exec_())
