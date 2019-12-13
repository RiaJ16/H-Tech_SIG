# -*- coding: UTF8 -*-

import os
import qgis.utils

from qgis.core import *
from qgis.gui import *

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import QHeaderView

from .obtener_capa import ObtenerCapa
from .widget_item_mas import WidgetItemMas

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'ventana_repetidos.ui'))

class VentanaRepetidos(QtWidgets.QDialog, FORM_CLASS):

	def __init__(self, online, bomba=False, parent=None):
		"""Constructor."""
		super(VentanaRepetidos, self).__init__(parent)
		self.setupUi(self)
		self.online = online
		self.bomba = bomba
		self.iface = qgis.utils.iface
		self.lienzo = qgis.utils.iface.mapCanvas()

	def inicializar(self):
		self.botonAceptar.setEnabled(False)
		self.botonAceptar.clicked.connect(self.cerrar)
		self.tablaSensores.itemSelectionChanged.connect(self.seleccionCambiada)
		self.tablaSensores.cellDoubleClicked.connect(self.cerrar)

	def buscarSensores(self,cadena):
		bandera = False
		sensores = self.online.separarSensores(cadena)
		self.mostrarSensores(sensores)

	def mostrarSensores(self,sensores):
		try:
			if sensores[0].idSensor == 0:
				self.setWindowTitle("Error")
				#self.busy.hide()
				error = "Inicie sesión antes de ver la información"
				self.iface.messageBar().pushMessage("Error", error, level=Qgis.Critical,duration=3)
				self.adjustSize()
				ObtenerCapa().capa().removeSelection()
			else:
				self.tablaSensores.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);
				#self.tablaSensores.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed);
				self.tablaSensores.setFocusPolicy(Qt.NoFocus)
				for sensor in sensores:
					self.tablaSensores.insertRow(self.tablaSensores.rowCount())
					if self.bomba:
						elementos = [sensor.grupoTexto,"\tBomba","\t"+sensor.municipioTexto]
						self.setWindowTitle("Elige una de las bombas")
					else:
						elementos = [sensor.grupoTexto,"\t"+sensor.tipoSensorTexto,"\t"+sensor.municipioTexto]
					numcol = 0
					fuentes = (QFont("Verdana",12),QFont("Verdana",11),QFont("Verdana",7))
					alineaciones = (Qt.AlignLeft|Qt.AlignVCenter,Qt.AlignLeft|Qt.AlignVCenter,Qt.AlignRight|Qt.AlignBottom)
					brushes = (QBrush(QColor("#2980b9")),QBrush(QColor("black")),QBrush(QColor("gray")))
					#id
					for elemento, fuente, alineacion, brush in zip(elementos,fuentes, alineaciones, brushes):
						item = WidgetItemMas(elemento,sensor.idFeature)
						item.setFont(fuente)
						item.setTextAlignment(alineacion)
						item.setForeground(brush)
						item.setFlags(item.flags() ^ Qt.ItemIsEditable)
						self.tablaSensores.setItem(self.tablaSensores.rowCount()-1,numcol,item)
						numcol += 1
					#self.tablaSensores.resizeColumnsToContents()
					#self.adjustSize() 
				capaActiva = ObtenerCapa().capa()
				self.seleccionados = capaActiva.selectedFeatures()
				self.exec_()
		except IndexError:
			self.setWindowTitle("Error")
			#self.busy.hide()
			self.adjustSize()
			ObtenerCapa().capa().removeSelection()

	def seleccionCambiada(self):
		try:
			self.tablaSensores.selectedItems()[0]
			self.tablaSensores.selectRow(self.tablaSensores.currentRow())
			idSeleccionado = int(self.tablaSensores.item(self.tablaSensores.currentRow(),0).idFeature())
			for caracteristica in self.seleccionados:
				if idSeleccionado == caracteristica.attribute('id'):
					id = caracteristica.id()
			capaActiva = ObtenerCapa().capa()
			capaActiva.removeSelection()
			capaActiva.select(id)
			self.botonAceptar.setEnabled(True)
		except:
			self.botonAceptar.setEnabled(False)
			capaActiva = ObtenerCapa().capa()
			capaActiva.removeSelection()

	def cerrar(self):
		self.hide()

	def reject(self):
		ObtenerCapa().capa().removeSelection()
		QtWidgets.QDialog.reject(self)