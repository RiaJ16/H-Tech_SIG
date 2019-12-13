# -*- coding: UTF8 -*-

import os

from qgis.core import *
from qgis.gui import *

from PyQt5 import QtGui, QtCore, uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QSize, Qt
from PyQt5.QtGui import QColor, QIcon, QDoubleValidator, QFont, QMovie
from PyQt5.QtWidgets import QDialog, QLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QWidget, QPushButton, QVBoxLayout

from .busy_icon import BusyIcon
from .obtener_capa import ObtenerCapa
from .ventana_datos import VentanaDatos
from .validacion import Validacion
import qgis.utils


class BotonNuevo(QObject):

	signalCambio = pyqtSignal()
	signalNoCapa = pyqtSignal()

	def __init__(self, online, direccion=''):
		QObject.__init__(self)
		self.iface = qgis.utils.iface
		self.lienzo = self.iface.mapCanvas()
		self.h_list = []
		self.online = online
		self.direccion = direccion

	def inicializar(self):
		obtenerCapa = ObtenerCapa().capa()
		if obtenerCapa == '':
			self.signalNoCapa.emit()
		else:
			self.crearBarra()
			self.validacion = Validacion(self.widget.sender)
			self.validacion.validarDoble([self.widget.textoX, self.widget.textoY])
			self.obtenerCoordenadas()

	def crearBarra(self):
		if not hasattr(self, 'widget'):
			self.widget = QDialog()
			#self.widget.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
			uic.loadUi(os.path.join(os.path.dirname(__file__), 'agregar_sensor.ui'), self.widget)
			self.widget.textoX.textChanged.connect(self.resaltarPunto)
			self.widget.textoY.textChanged.connect(self.resaltarPunto)
			self.widget.boton.setEnabled(False)
			self.widget.boton.clicked.connect(self.pasarCoordenadas)
			self.widget.layout().setSizeConstraint(QLayout.SetFixedSize)
			self.busy = BusyIcon(self.widget.layout())
			self.busy.startAnimation()
			self.busy.hide()
			self.widget.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		self.widget.closeEvent = self.closeEvent
		self.widget.setVisible(True)

	def alEliminarBarra(self):
		if hasattr(self, 'widget'):
			del self.widget

	def obtenerCoordenadas(self):
		self.guardaClick = QgsMapToolEmitPoint(self.lienzo)
		self.lienzo.setMapTool(self.guardaClick)
		self.guardaClick.canvasClicked.connect(self.onClicked)

	def onClicked(self,punto):
		self.widget.textoX.setText(str(punto.x()))
		self.widget.textoY.setText(str(punto.y()))
		self.widget.boton.setEnabled(True)

	def resaltarPunto(self):
		try:
			x = float(self.widget.textoX.text())
			y = float(self.widget.textoY.text())
			for h in range(len(self.h_list)):
				self.h_list.pop(h)
			h = QgsHighlight(self.iface.mapCanvas(), QgsGeometry.fromPointXY(QgsPointXY(x, y)), ObtenerCapa().capa())
			h.setColor(QColor(232, 65, 24, 255))
			h.setWidth(4)
			h.setFillColor(QColor(251, 197, 49, 255))
			self.h_list.append(h)
		except ValueError:
			pass

	def pasarCoordenadas(self):
		#self.busy.show()
		if not hasattr(self,'ventanaDatos'):
			self.ventanaDatos = VentanaDatos(self.online, self.direccion)
			self.ventanaDatos.signalCambio.connect(self.cambio)
			self.ventanaDatos.signalCerrada.connect(self.ventanaDatosCerrada)
		self.ventanaDatos.inicializar(False, self.widget.textoX.text(), self.widget.textoY.text())
		self.salir()

	def cambio(self):
		self.signalCambio.emit()

	def salir(self):
		self.busy.hide()
		self.widget.hide()
		self.guardaClick.canvasClicked.disconnect(self.onClicked)
		try:
			self.guardaClick.canvasClicked.disconnect(self.onClicked)
		except TypeError:
			pass

	def cerrar(self):
		self.widget.boton.clicked.disconnect()
		if hasattr(self,'ventanaDatos'):
			self.ventanaDatos.cerrar()
			self.ventanaDatos.disconnectSignals()
			self.ventanaDatos.signalCambio.disconnect()
			del self.ventanaDatos
		if hasattr(self,'widget'):
			self.widget.close()
			self.alEliminarBarra()

	def ventanaDatosCerrada(self):
		for h in range(len(self.h_list)):
			self.h_list.pop(h)
		try:
			self.guardaClick.canvasClicked.disconnect(self.onClicked)
		except TypeError:
			pass

	def closeEvent(self, event):
		ObtenerCapa().capa().removeSelection()
		self.ventanaDatosCerrada()
