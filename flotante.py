# -*- coding: UTF8 -*-

import ctypes

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

class Flotante(QLabel):

	def __init__(self, text="", x=320, y=200, parent=None):
		super().__init__(text, parent, Qt.SplashScreen | Qt.WindowStaysOnTopHint)
		#self.setFrameStyle(QLabel.Sunken | QLabel.Panel)
		self.setAlignment(Qt.AlignCenter)
		self.setFixedSize(x, y)
		self.setFocus()

	def setFixedSize(self, x, y):
		super().setFixedSize(x, y)
		screenSize = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
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
