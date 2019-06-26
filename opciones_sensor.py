# -*- coding: UTF8 -*-

import qgis.utils

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QButtonGroup, QVBoxLayout, QWidget

from functools import partial

import os

from .resources import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'opciones_sensor.ui'))

class OpcionesSensor(QWidget, FORM_CLASS):

	grupo = QButtonGroup()
	sensor = ''

	INACTIVE_STYLE_SHEET = "font-size: 10pt;color: #7f8f98;background-color: #cbe3f2;boder: 5px solid #64D6EE;border-radius: 15px;"
	ACTIVE_STYLE_SHEET = "font-size: 14pt;color: #FFFFFF;background-color: #3498db;border-radius: 15px;"


	def __init__(self,parent=None):
		"""Constructor."""
		super(OpcionesSensor, self).__init__(parent)
		self.setupUi(self)
		self.iface = qgis.utils.iface
		self._visualizacionInicial()

	def _visualizacionInicial(self):
		self.setWindowFlags(Qt.Widget | Qt.MSWindowsFixedSizeDialogHint)
		#self.setFixedSize(self.size())
		self.scrollArea.setLayout(QVBoxLayout())
		self.alarmas = QWidget()
		uic.loadUi(os.path.join(os.path.dirname(__file__), 'configurar_alarmas.ui'), self.alarmas)
		self.intervalo = QWidget()
		uic.loadUi(os.path.join(os.path.dirname(__file__), 'intervalo.ui'), self.intervalo)
		self.fecha = QWidget()
		uic.loadUi(os.path.join(os.path.dirname(__file__), 'configurar_fecha.ui'), self.fecha)
		self.scrollArea.layout().addWidget(self.alarmas)
		self.scrollArea.layout().addWidget(self.intervalo)
		self.scrollArea.layout().addWidget(self.fecha)
		self._inicializarIntervalo()
		self.alarmas.setVisible(False)
		self.intervalo.setVisible(False)
		self.fecha.setVisible(False)
		self._signals()
		self.listaOpciones.setCurrentItem(self.listaOpciones.item(0))
		self.fecha.listaFecha.setCurrentItem(self.fecha.listaFecha.item(0))
		self.show()

	def _signals(self):
		self.listaOpciones.itemSelectionChanged.connect(self.opcionCambiada)
		self.fecha.listaFecha.itemSelectionChanged.connect(self.opcionFechaCambiada)

	def _inicializarIntervalo(self):
		layout = self.intervalo.layout().itemAt(0)
		for i in range(0,layout.count()):
			botonRadio = layout.itemAt(i).widget().layout().itemAt(0).widget()
			botonRadio.setProperty('state','off')
			botonRadio.parent().setProperty('state','off')
			botonRadio.setStyle(self.intervalo.style())
			botonRadio.parent().setStyle(self.intervalo.style())
			self.grupo.addButton(botonRadio)
			botonRadio.toggled.connect(partial(self.cambiarIntervalo,botonRadio))		
		self.intervalo.min15.setChecked(True)

	def opcionCambiada(self):
		for item in self.listaOpciones.selectedItems():
			if item.text() == "Alarmas":
				self.alarmas.setVisible(True)
				self.intervalo.setVisible(False)
				self.fecha.setVisible(False)
			elif item.text() == "Intervalo":
				self.alarmas.setVisible(False)
				self.intervalo.setVisible(True)
				self.fecha.setVisible(False)
			elif item.text() == "Fecha y hora":
				self.alarmas.setVisible(False)
				self.intervalo.setVisible(False)
				self.fecha.setVisible(True)
			
	def cambiarIntervalo(self,boton,flag):
		if flag:
			boton.parent().setProperty('state','on')
			boton.setProperty('state','on')
		else:
			boton.parent().setProperty('state','off')
			boton.setProperty('state','off')
		boton.parent().setStyle(self.intervalo.style())
		boton.setStyle(self.intervalo.style())

	def opcionFechaCambiada(self):
		for i in range(0,self.fecha.listaFecha.count()):
			if self.fecha.listaFecha.item(i) == self.fecha.listaFecha.selectedItems()[0]:
				break
		if i == 0:
			self.fecha.selectorFecha.setVisible(False)
			self.fecha.selectorHora.setVisible(False)
		if i == 1:
			self.fecha.selectorFecha.setVisible(True)
			self.fecha.selectorHora.setVisible(True)

	def setSensor(self,sensor,titulo):
		self.sensor = sensor
		self.alarmas.minimo.setValue(sensor.datoMinimo)
		self.alarmas.maximo.setValue(sensor.datoMaximo)
		unidades = ''
		if int(sensor.tipoSensor) == 1:
			unidades = 'mca'
		elif int(sensor.tipoSensor) == 2:
			unidades = 'lps'
		elif int(sensor.tipoSensor) == 3:
			unidades = 'm'
		self.alarmas.labelUnidades1.setText(unidades)
		self.alarmas.labelUnidades2.setText(unidades)
		self.setWindowTitle(titulo)
