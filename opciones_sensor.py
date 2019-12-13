# -*- coding: UTF8 -*-

import datetime
import os
import qgis.utils
import time

from qgis.core import Qgis

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QButtonGroup, QVBoxLayout, QWidget

from functools import partial

from .online import Online
from .publisher import Publisher
from .resources import *
from .strings import strings_opciones_sensor as strings

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'opciones_sensor.ui'))

class OpcionesSensor(QWidget, FORM_CLASS):

	grupo = QButtonGroup()
	sensor = ''

	INACTIVE_STYLE_SHEET = "font-size: 10pt;color: #7f8f98;background-color: #cbe3f2;boder: 5px solid #64D6EE;border-radius: 15px;"
	ACTIVE_STYLE_SHEET = "font-size: 14pt;color: #FFFFFF;background-color: #3498db;border-radius: 15px;"


	def __init__(self, online, parent=None):
		"""Constructor."""
		super(OpcionesSensor, self).__init__(parent)
		self.setupUi(self)
		self.iface = qgis.utils.iface
		self.online = online
		self.publicador = Publisher()
		self.alarma = 0
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
		self.fecha.selectorFecha.setDate(datetime.date.today())
		self.fecha.selectorHora.setTime(datetime.datetime.now().time())
		self.show()

	def _signals(self):
		self.listaOpciones.itemSelectionChanged.connect(self.opcionCambiada)
		self.fecha.listaFecha.itemSelectionChanged.connect(self.opcionFechaCambiada)
		self.alarmas.botonAlarma.clicked.connect(self.interruptorAlarma)
		self.alarmas.botonEnviar.clicked.connect(self.enviarAlarmas)
		self.intervalo.botonEnviar.clicked.connect(self.enviarIntervalo)
		self.fecha.botonEnviar.clicked.connect(self.enviarFechaYHora)

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

	def interruptorAlarma(self):
		self.cambiarBotonAlarma(not(self.alarma))

	def cambiarBotonAlarma(self,flag=True):
		icon = QIcon()
		if flag:
			icon.addPixmap(QPixmap(':VentanaConfiguracion/icons/icon_on.png'))
			self.alarma = 1
		else:
			icon.addPixmap(QPixmap(':VentanaConfiguracion/icons/icon_off.png'))
			self.alarma = 0
		self.alarmas.minimo.setEnabled(flag)
		self.alarmas.maximo.setEnabled(flag)
		self.alarmas.botonAlarma.setIcon(icon)

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
		if int(sensor.intervalo) == 3:
			self.intervalo.min3.setChecked(True)
		elif int(sensor.intervalo) == 5:
			self.intervalo.min5.setChecked(True)
		elif int(sensor.intervalo) == 10:
			self.intervalo.min10.setChecked(True)
		elif int(sensor.intervalo) == 15:
			self.intervalo.min15.setChecked(True)
		elif int(sensor.intervalo) == 30:
			self.intervalo.min30.setChecked(True)
		elif int(sensor.intervalo) == 45:
			self.intervalo.min45.setChecked(True)
		elif int(sensor.intervalo) == 60:
			self.intervalo.min60.setChecked(True)
		self.setWindowTitle(titulo)
		self.cambiarBotonAlarma(sensor.alarma)

	def setCoordinador(self, coordinador):
		self.coordinador = coordinador

#---Métodos para publicar la opción seleccionada en cada una de las ventanas---

	def enviarAlarmas(self):
		idDispositivo = self.sensor.idDispositivo
		anexo = ''
		flagCoordinador = 0
		if self.sensor.coordinador > 0:
			flagCoordinador = 0
			idDispositivo = self.coordinador.getIdDispositivo
			anexo = "_" + self.sensor.idDispositivo
		password = self.online.consultarPasswordIoT(idDispositivo, flagCoordinador)
		if self.comprobarPassword(password):
			password = password[0]['password']
			stringIndex = 0
			if self.alarma:
				topic = "/sensores/{}".format(self.sensor.idDispositivo)
				minimo = self.alarmas.minimo.value()
				maximo = self.alarmas.maximo.value()
				mensajeMinimo = "{\"Tipo\":\"Config\",\"Cadena\":\"Wa%sm%.02f%s\"}" % (self.sensor.tipoSensorTexto[0].upper(),minimo,anexo)
				mensajeMaximo = "{\"Tipo\":\"Config\",\"Cadena\":\"Wa%sM%.02f%s\"}" % (self.sensor.tipoSensorTexto[0].upper(),maximo,anexo)
				if not (self.sensor.datoMinimo == minimo):
					self.publicador.publicar(topic,mensajeMinimo,password)
					self.sensor.datoMinimo = minimo
					stringIndex = stringIndex | 0b001
					time.sleep(0.5)
				if not (self.sensor.datoMaximo == maximo):
					self.publicador.publicar(topic,mensajeMaximo,password)
					self.sensor.datoMaximo = maximo
					stringIndex = stringIndex | 0b010
			if self.sensor.alarma > 0:
				self.sensor.alarma = 1
			if not (self.alarma == self.sensor.alarma):
				self.sensor.alarma = self.alarma
				self.online.configurarAlarma(self.sensor)
				if self.alarma == 1:
					stringIndex = stringIndex | 0b100
				else:
					stringIndex = 8
			if stringIndex > 0:
				qgis.utils.iface.messageBar().pushMessage("Aviso", strings.alarmas[stringIndex], level=Qgis.Info,duration=4)

	def enviarIntervalo(self):
		idDispositivo = self.sensor.idDispositivo
		anexo = ''
		flagCoordinador = 0
		if self.sensor.coordinador > 0:
			flagCoordinador = 1
			idDispositivo = self.coordinador.getIdDispositivo
			anexo = "_" + self.sensor.idDispositivo
		password = self.online.consultarPasswordIoT(idDispositivo, flagCoordinador)
		if self.comprobarPassword(password):
			password = password[0]['password']
			topic = "/sensores/{}".format(idDispositivo)
			minutos = 15
			if self.intervalo.min3.isChecked():
				minutos = 3
			elif self.intervalo.min5.isChecked():
				minutos = 5
			elif self.intervalo.min10.isChecked():
				minutos = 10
			elif self.intervalo.min15.isChecked():
				minutos = 15
			elif self.intervalo.min30.isChecked():
				minutos = 30
			elif self.intervalo.min45.isChecked():
				minutos = 45
			elif self.intervalo.min60.isChecked():
				minutos = 60
			mensaje = "{\"Tipo\":\"Config\",\"Cadena\":\"WR%d%s\"}" % (minutos, anexo)
			self.publicador.publicar(topic,mensaje,password)
			qgis.utils.iface.messageBar().pushMessage("Aviso", strings.intervalo[1], level=Qgis.Info,duration=4)

	def enviarFechaYHora(self):
		idDispositivo = self.sensor.idDispositivo
		anexo = ''
		flagCoordinador = 0
		if self.sensor.coordinador > 0:
			flagCoordinador = 1
			idDispositivo = self.coordinador.getIdDispositivo
			anexo = "_" + self.sensor.idDispositivo
		password = self.online.consultarPasswordIoT(idDispositivo, flagCoordinador)
		if self.comprobarPassword(password):
			print("i.i")
			password = password[0]['password']
			topic = "/sensores/{}".format(idDispositivo)
			for i in range(0,self.fecha.listaFecha.count()):
				if self.fecha.listaFecha.item(i) == self.fecha.listaFecha.currentItem():
					break
			if i == 0:
				fecha = datetime.date.today().strftime("%d%m%Y")
				hora = datetime.datetime.now().strftime("%H%M%S")
			if i == 1:
				fecha = self.fecha.selectorFecha.date().toString("ddMMyyyy")
				hora = self.fecha.selectorHora.time().toString("HHmmss")
			mensajeFecha = "{\"Tipo\":\"Config\",\"Cadena\":\"WD%s%s\"}" % (fecha, anexo)
			mensajeHora = "{\"Tipo\":\"Config\",\"Cadena\":\"WT%s%s\"}" % (hora, anexo)
			self.publicador.publicar(topic,mensajeFecha,password)
			#time.sleep(0.5)
			self.publicador.publicar(topic,mensajeHora,password)
			qgis.utils.iface.messageBar().pushMessage("Aviso", strings.fecha[3], level=Qgis.Info,duration=4)

	def comprobarPassword(self,password):
		if password == []:
			return False
		else:
			if password == 1:
				qgis.utils.iface.messageBar().pushMessage("Error", strings.general[1], level=Qgis.Critical,duration=7)
				return False
			elif password == 2:
				qgis.utils.iface.messageBar().pushMessage("Error", strings.general[2], level=Qgis.Critical,duration=7)
				return False
		return True

