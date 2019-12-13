# -*- coding: UTF8 -*-

import os
import qgis.utils

from qgis.core import *
from qgis.gui import *

from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QDoubleValidator, QCursor, QColor

from .ventana_historial import VentanaHistorial
from .eliminar_sensor import EliminarSensor
from .mover_sensor import MoverSensor
from .obtener_capa import ObtenerCapa
from .online import Online
from .pantalla_bomba import PantallaBomba
from .ventana_datos import VentanaDatos
from .ventana_repetidos import VentanaRepetidos

class ClickLienzo(QObject):

	signalCambio = pyqtSignal()
	signalNoCapa = pyqtSignal()

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
		multiplicador = 12
		if self.bandera == 0:
			multiplicador = 20
		capaActiva = ObtenerCapa().capa()
		if capaActiva == '':
			self.signalNoCapa.emit()
		else:
			capaActiva.removeSelection()
			radio = self.lienzo.mapUnitsPerPixel() * multiplicador
			rect = QgsRectangle(punto.x() - radio,
				punto.y() - radio,
				punto.x() + radio,
				punto.y() + radio)
			capaActiva.selectByRect(rect, False)
			#self.lienzo.setSelectionColor( QColor(1, 1, 1, 90) )
			self.lienzo.setSelectionColor(QColor(255,102,0))
			if capaActiva.selectedFeatures():
				if len(capaActiva.selectedFeatures()) == 1:
					if self.bandera == 0:
						objetoGeografico = capaActiva.selectedFeatures()[0]
						if objetoGeografico.attribute('bomba') <= 1:
							capaActiva.removeSelection()
				elif len(capaActiva.selectedFeatures()) > 1:
					cadena = ''
					contador = 0
					for objetoGeografico in capaActiva.selectedFeatures():
						try:
							if self.bandera == 0:
								if objetoGeografico.attribute('tipoSensor') == 1 and objetoGeografico.attribute('bomba') > 1:
									cadena += '{},'.format(objetoGeografico.attribute('id'))
									contador += 1
							else:
								cadena += '{},'.format(objetoGeografico.attribute('id'))
								contador += 1
						except:
							pass
					if contador == 0:
						capaActiva.removeSelection()
					elif contador > 1:
						if self.bandera:
							ventanaRepetidos = VentanaRepetidos(self.online)
						else:
							ventanaRepetidos = VentanaRepetidos(self.online, True)
						ventanaRepetidos.inicializar()
						ventanaRepetidos.buscarSensores(cadena[0:-1])
				if self.bandera == 0:
					if capaActiva.selectedFeatures():
						if not hasattr(self,'pantallaBomba'):
							self.pantallaBomba = PantallaBomba(self.online)
						self.pantallaBomba.objetoGeograficoSeleccionado(capaActiva.selectedFeatures()[0])
						self.pantallaBomba.mostrarVentana()
				elif self.bandera == 1:
					if not hasattr(self,'ventanaHistorial'):
						self.ventanaHistorial = VentanaHistorial(self.online)
					try:
						self.ventanaHistorial.objetoGeograficoSeleccionado(capaActiva.selectedFeatures()[0])
						self.ventanaHistorial.mostrarVentana()
					except IndexError:
						pass
				elif self.bandera == 2:
					if not hasattr(self,'ventanaDatos'):
						self.ventanaDatos = VentanaDatos(self.online, editar=True)
						self.ventanaDatos.signalCambio.connect(self.cambio)
					try:
						capaActiva.selectedFeatures()[0]
						(x,y) = capaActiva.selectedFeatures()[0].geometry().asPoint()
						self.ventanaDatos.inicializar(True,x,y)
					except IndexError:
						pass
				elif self.bandera == 3:
					if not hasattr(self,'moverSensor'):
						self.moverSensor = MoverSensor(self.online)
						self.moverSensor.signalEditado.connect(self._editado)
					try:
						self.moverSensor.pasarObjetoGeografico(capaActiva.selectedFeatures()[0])
						self.moverSensor.crearBarra()
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

	def _editado(self):
		self.seleccionarObjetoGeografico()

	def cerrar(self):
		if hasattr(self, 'ventanaHistorial'):
			self.ventanaHistorial.cerrar()
			self.ventanaHistorial.disconnectSignals()
			self.guardaClick.canvasClicked.disconnect(self.onClicked)
		if hasattr(self,'eliminarSensor'):
			self.eliminarSensor.disconnectSignals()
			self.guardaClick.canvasClicked.disconnect(self.onClicked)
		if hasattr(self,'ventanaDatos'):
			self.ventanaDatos.close()
			self.ventanaDatos.disconnectSignals()
			self.guardaClick.canvasClicked.disconnect(self.onClicked)
		if hasattr(self,'moverSensor'):
			self.moverSensor.widget.close()
			self.moverSensor.disconnectSignals()
			self.guardaClick.canvasClicked.disconnect(self.onClicked)
		if hasattr(self,'pantallaBomba'):
			self.pantallaBomba.close()
			self.pantallaBomba.disconnectSignals()
			self.guardaClick.canvasClicked.disconnect(self.onClicked)
		try:
			ObtenerCapa().capa().removeSelection()
		except AttributeError:
			pass