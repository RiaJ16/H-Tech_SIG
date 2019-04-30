# -*- coding: UTF8 -*-

import os
import qgis.utils

from qgis.core import *
from qgis.gui import *

from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QDoubleValidator, QCursor, QColor

from .ventana_historial import VentanaHistorial
from .eliminar_sensor import EliminarSensor
from .obtener_capa import ObtenerCapa
from .online import Online
from .ventana_datos import VentanaDatos
from .ventana_repetidos import VentanaRepetidos

class ClickLienzo(QObject):

	signalCambio = pyqtSignal()

	def __init__(self,bandera,online):
		QObject.__init__(self)
		self.iface = qgis.utils.iface
		self.bandera = bandera
		self.online = online
		self.inicializar()

	def inicializar(self):
		self.lienzo = self.iface.mapCanvas()
		self.seleccionarObjetoGeografico()

	def seleccionarObjetoGeografico(self):
		self.guardaClick = QgsMapToolEmitPoint(self.lienzo)
		self.lienzo.setMapTool(self.guardaClick)
		self.guardaClick.canvasClicked.connect(self.onClicked)

	def onClicked(self,punto):
		capaActiva = ObtenerCapa.capa()
		capaActiva.removeSelection()
		radio = self.lienzo.mapUnitsPerPixel() * 12
		rect = QgsRectangle(punto.x() - radio,
			punto.y() - radio,
			punto.x() + radio,
			punto.y() + radio)
		capaActiva.selectByRect(rect, False)
		#self.lienzo.setSelectionColor( QColor(1, 1, 1, 90) )
		self.lienzo.setSelectionColor(QColor(255,102,0))
		if capaActiva.selectedFeatures():
			for objetoGeografico in capaActiva.selectedFeatures():
				id = objetoGeografico.id()
			if len(capaActiva.selectedFeatures()) > 1:
				cadena = ''
				contador = 0
				for objetoGeografico in capaActiva.selectedFeatures():
					try:
						cadena += '{},'.format(objetoGeografico.attribute('id'))
						contador += 1
					except:
						pass
				if contador > 1:
					ventanaRepetidos = VentanaRepetidos(self.online)
					ventanaRepetidos.inicializar()
					ventanaRepetidos.buscarSensores(cadena[0:-1])
			if self.bandera == 1:
				if not hasattr(self,'ventanaHistorial'):
					self.ventanaHistorial = VentanaHistorial(self.online)
				try:
					self.ventanaHistorial.objetoGeograficoSeleccionado(capaActiva.selectedFeatures()[0])
					self.ventanaHistorial.mostrarVentana()
				except IndexError:
					pass
			elif self.bandera == 2:
				if not hasattr(self,'ventanaDatos'):
					self.ventanaDatos = VentanaDatos()
					self.ventanaDatos.signalCambio.connect(self.cambio)
				try:
					capaActiva.selectedFeatures()[0]
					self.ventanaDatos.inicializar(True)
				except IndexError:
					pass
			else:
				try:
					capaActiva.selectedFeatures()[0]
					self.eliminarSensor = EliminarSensor(self.online)
					self.eliminarSensor.signalCambio.connect(self.cambio)
				except IndexError:
					pass

	def cambio(self):
		self.signalCambio.emit()

	def nuevoDato(self,dato):
		if hasattr(self,'ventanaHistorial'):
			self.ventanaHistorial.nuevoDato(dato)

	def cerrar(self):
		if hasattr(self, 'ventanaHistorial'):
			self.ventanaHistorial.cerrar()
			self.guardaClick.canvasClicked.disconnect(self.onClicked)
		if hasattr(self,'eliminarSensor'):
			self.guardaClick.canvasClicked.disconnect(self.onClicked)
		if hasattr(self,'ventanaDatos'):
			self.ventanaDatos.close()
			self.guardaClick.canvasClicked.disconnect(self.onClicked)
		ObtenerCapa.capa().removeSelection()