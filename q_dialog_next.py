# -*- coding: utf-8 -*-

from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QDialog

class QDialogNext(QDialog):

	startPosition = QPoint(0,0)

	def __init__(self, parent=None):
		super().__init__(parent=parent)

	def setMovable(self, frame):
		frame.mousePressEvent = self.customMousePressEvent
		frame.mouseMoveEvent = self.customMouseMoveEvent

	def customMousePressEvent(self, event):
		self.startPosition = event.pos()
		super().mousePressEvent(event)

	def customMouseMoveEvent(self, event):
		delta = event.pos() - self.startPosition
		self.move(self.pos() + delta)
		super().mouseMoveEvent(event)