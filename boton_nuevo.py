# -*- coding: UTF8 -*-

import os

from qgis.core import *
from qgis.gui import *

from PyQt5 import QtGui, QtCore, uic
from PyQt5.QtGui import QIcon, QDoubleValidator, QFont, QMovie
from PyQt5.QtWidgets import QDialog, QLabel, QLayout, QHBoxLayout, QMessageBox, QWidget, QPushButton, QLineEdit
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QSize, Qt

from .busy_icon import BusyIcon
from .ventana_datos import VentanaDatos
from .validacion import Validacion
import qgis.utils

class BotonNuevo(QObject):

	signalCambio = pyqtSignal()
	def __init__(self,direccion=''):
		QObject.__init__(self)
		self.iface = qgis.utils.iface
		self.lienzo = self.iface.mapCanvas()
		self.direccion = direccion

	def inicializar(self):
		self.crearBarra()
		self.validacion = Validacion(self.widget.sender)
		self.validacion.validarDoble([self.textoX,self.textoY])
		self.obtenerCoordenadas()

	def crearBarra(self):
		if not hasattr(self, 'widget'):
			self.widget = QDialog()
			#self.widget.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
			self.widget.setStyleSheet('QLineEdit {background-color: transparent; border-style: solid; border-bottom: 2px solid #3498db;} QLabel{ color: rgb(104, 104, 104);font-family: Verdana;font-size: 9} QPushButton:enabled{background-color: #3498db;color: rgb(255, 255, 255);font-size: 10pt; font-weight: bold;} QPushButton:disabled{background-color: #adc1ce;color: rgb(255, 255, 255);font-size: 10pt; font-weight: bold;}')
			self.etiqueta = QLabel("Haz click donde desees agregar el sensor")
			self.textoX = QLineEdit(self.widget)
			self.textoY = QLineEdit(self.widget)
			lineEdits = [self.textoX,self.textoY]
			for elemento in lineEdits:
				elemento.setFixedSize(QSize(170,26))
				elemento.setFont(QFont("MS Shell Dlg 2",10))
			self.boton = QPushButton(self.widget)
			self.boton.setText("ACEPTAR")
			self.boton.setEnabled(False)
			self.boton.clicked.connect(self.pasarCoordenadas)
			self.widget.setLayout(QHBoxLayout())
			self.widget.layout().setSizeConstraint(QLayout.SetFixedSize)
			self.widget.setFixedSize(self.widget.maximumSize())
			self.widget.setWindowTitle("Agregar nuevo sensor")
			icon = QIcon(":/sigrdap/icons/nuevo.png")
			self.widget.setWindowIcon(icon)
			self.widget.layout().addWidget(self.etiqueta)
			self.widget.layout().addWidget(self.textoX)
			self.widget.layout().addWidget(self.textoY)
			self.widget.layout().addWidget(self.boton)
			self.busy = BusyIcon(self.widget.layout())
			self.busy.startAnimation()
			self.busy.hide()
			self.widget.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		self.widget.setVisible(True)

	def alEliminarBarra(self):
		if hasattr(self, 'widget'):
			del self.widget
			self.guardaClick.canvasClicked.disconnect(self.onClicked)

	def obtenerCoordenadas(self):
		self.guardaClick = QgsMapToolEmitPoint(self.lienzo)
		self.lienzo.setMapTool(self.guardaClick)
		self.guardaClick.canvasClicked.connect(self.onClicked)

	def onClicked(self,punto):
		self.textoX.setText(str(punto.x()))
		self.textoY.setText(str(punto.y()))
		self.boton.setEnabled(True)

	def pasarCoordenadas(self):
		#self.busy.show()
		if not hasattr(self,'ventanaDatos'):
			self.ventanaDatos = VentanaDatos(self.direccion)
			self.ventanaDatos.signalCambio.connect(self.cambio)
		self.ventanaDatos.inicializar(False,self.textoX.text(),self.textoY.text())
		self.salir()

	def cambio(self):
		self.signalCambio.emit()

	def salir(self):
		self.busy.hide()
		self.widget.close()

	def cerrar(self):
		if hasattr(self,'ventanaDatos'):
			self.ventanaDatos.cerrar()
			del self.ventanaDatos
		if hasattr(self,'widget'):
			self.widget.close()
			del self.widget