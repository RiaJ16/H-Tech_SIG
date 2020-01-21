# -*- coding: utf-8 -*-

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog


class QDialogNext(QDialog):

	startPosition = QPoint(0,0)

	def __init__(self, parent=None):
		super().__init__(parent=parent)
		super().setWindowFlags(Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint)

	def setMovable(self, frame):
		frame.mousePressEvent = self.customMousePressEvent
		frame.mouseMoveEvent = self.customMouseMoveEvent

	def setBotonCerrar(self, botonCerrar):
		self.botonCerrar = botonCerrar
		botonCerrar.enterEvent = self.cerrarEnterEvent
		botonCerrar.leaveEvent = self.cerrarLeaveEvent
		botonCerrar.clicked.connect(self.close)

	def setWindowTitle(self, title):
		super().setWindowTitle(title)
		try:
			self.logo.setToolTip(title)
		except AttributeError:
			pass

	def customMousePressEvent(self, event):
		self.startPosition = event.pos()
		super().mousePressEvent(event)

	def customMouseMoveEvent(self, event):
		delta = event.pos() - self.startPosition
		self.move(self.pos() + delta)
		super().mouseMoveEvent(event)

	def cerrarEnterEvent(self, event):
		icono = QIcon(":General/icons/closeicon.png")
		self.botonCerrar.setIcon(icono)

	def cerrarLeaveEvent(self, event):
		icono = QIcon(":General/icons/closeicon-d.png")
		self.botonCerrar.setIcon(icono)
