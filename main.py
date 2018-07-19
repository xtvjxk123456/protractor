# coding:utf-8
from __future__ import division
import math

from Qt import QtWidgets, QtGui, QtCompat, QtCore


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

    def __repr__(self):
        return "<vector2d({},{})>".format(self.x, self.y)


def angleBetween(v1, v2):
    dot = v1.x * v2.x + v1.y * v2.y
    return math.acos(dot / (v1.mod() * v2.mod()))


def findVectorBetween(v1, angle):
    v_a = vector2d(math.sin(math.asin(v1.x / v1.mod()) - angle * math.pi / 180.0),
                   math.cos(math.acos(v1.y / v1.mod()) - angle * math.pi / 180.0))
    v_b = vector2d(math.sin(math.asin(v1.x / v1.mod()) + angle * math.pi / 180.0),
                   math.cos(math.acos(v1.y / v1.mod()) + angle * math.pi / 180.0))
    return v_a, v_b


class Protractor(QtWidgets.QDialog):
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

    def paintEvent(self, event):
        """
        Paint event
        """
        # Convert click and current mouse positions to local space.
        mouse_pos = self.mapFromGlobal(QtGui.QCursor.pos())
        click_pos = None
        if self._click_pos is not None:
            click_pos = self.mapFromGlobal(self._click_pos)

        painter = QtGui.QPainter(self)

        # Draw background. Aside from aesthetics, this makes the full
        # tool region accept mouse events.
        painter.setBrush(QtGui.QColor(0, 0, 0, self._opacity))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(event.rect())

        # Clear the capture area
        if click_pos is not None:
            capture_rect = QtCore.QRect(click_pos, mouse_pos)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
            painter.drawRect(capture_rect)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)

        pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 64), 1, QtCore.Qt.DotLine)
        painter.setPen(pen)

        # Draw cropping markers at click position
        if click_pos is not None:
            painter.drawLine(event.rect().left(), click_pos.y(),
                             event.rect().right(), click_pos.y())
            painter.drawLine(click_pos.x(), event.rect().top(),
                             click_pos.x(), event.rect().bottom())

        # Draw cropping markers at current mouse position
        painter.drawLine(event.rect().left(), mouse_pos.y(),
                         event.rect().right(), mouse_pos.y())
        painter.drawLine(mouse_pos.x(), event.rect().top(),
                         mouse_pos.x(), event.rect().bottom())

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
            self._click_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        """
        Mouse release event
        """
        if event.button() == QtCore.Qt.LeftButton and self._click_pos is not None:
            # End click drag operation and commit the current capture rect
            self._capture_rect = QtCore.QRect(self._click_pos,
                                              event.globalPos()).normalized()
            self._click_pos = None
        self.close()

    def mouseMoveEvent(self, event):
        """
        Mouse move event
        """
        self.repaint()

    def showEvent(self, event):
        """
        Show event
        """
        self._fit_screen_geometry()
        # Start fade in animation
        fade_anim = QtCore.QPropertyAnimation(self, "_opacity_anim_prop", self)
        fade_anim.setStartValue(self._opacity)
        fade_anim.setEndValue(127)
        fade_anim.setDuration(300)
        fade_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        fade_anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def _fit_screen_geometry(self):
        # Compute the union of all screen geometries, and resize to fit.
        desktop = QtGui.QApplication.instance().desktop()
        workspace_rect = QtCore.QRect()
        for i in range(desktop.screenCount()):
            workspace_rect = workspace_rect.united(desktop.screenGeometry(i))
        self.setGeometry(workspace_rect)
