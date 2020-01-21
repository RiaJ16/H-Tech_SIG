# -*- coding: UTF8 -*-

from qgis.PyQt.QtWidgets import QApplication

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


class Flotante(QLabel):

	def __init__(self, text="", x=320, y=200, parent=None):
		super().__init__(text, parent, Qt.SplashScreen | Qt.WindowStaysOnTopHint)
		#self.setFrameStyle(QLabel.Sunken | QLabel.Panel)
		self.resolucion = QApplication.instance().desktop().screenGeometry()
		self.setAlignment(Qt.AlignCenter)
		self.setFixedSize(x, y)
		self.setFocus()

	def setFixedSize(self, x, y):
		super().setFixedSize(x, y)
		screenSize = self.resolucion.width(), self.resolucion.height()
		xPos = (screenSize[0]-x)/2
		yPos = (screenSize[1]-y)/2
		self.move(xPos,yPos)

	def focusOutEvent(self, event):
		toReturn = super().focusOutEvent(event)
		self.hide()
		return toReturn

	def mouseReleaseEvent(self, event):
		toReturn = super().mouseReleaseEvent(event)
		self.hide()
		return toReturn
