# -*- coding: UTF8 -*-

import os
import qgis.utils
import threading

from functools import partial

from qgis.core import Qgis

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCursor, QFont, QIcon, QMovie, QPixmap
from PyQt5.QtWidgets import QAction, QLayout, QMenu

from .busy_icon import BusyIcon
from .dragon.programar_horarios import ProgramarHorarios
from .dragon.publisher import Publisher
from .dragon.strings import strings_dragon as strings
from .obtener_capa import ObtenerCapa

from .dragon.ui.resources import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'dragon/ui/pantalla.ui'))


class PantallaBomba(QtWidgets.QDialog, FORM_CLASS):

	def __init__(self, online, parent=None):
		"""Constructor."""
		super(PantallaBomba, self).__init__(parent)
		self.setupUi(self)
		self.online = online
		self.iface = qgis.utils.iface
		#self.layout().setSizeConstraint(QLayout.SetFixedSize)
		self.busy = BusyIcon(self.layout())
		self.busy.startAnimation()
		self._signals()
		self.setWindowIcon(QIcon(":/sigrdap/icons/bomba2.png"))
		#self._comprobarPermisos()

	def _signals(self):
		self.online.signalBombaConsultada.connect(self.cargarDatos)
		self.interruptor.clicked.connect(self.cambiarEstado)
		self.opciones.clicked.connect(self.mostrarMenu)
		self.modo.clicked.connect(self.cambiarModo)

	def disconnectSignals(self):
		self.online.signalBombaConsultada.disconnect(self.cargarDatos)

	def _comprobarPermisos(self):
		self.online.signalPermisos.connect(self._comprobarOpcionesSensor)
		t1 = threading.Thread(target=self.online.consultarPermisos)
		t1.start()

	def _comprobarOpcionesSensor(self, permisos):
		print(permisos)
		#if permisos < 2:
			#self.botonConfiguracion.setVisible(True)

	def _loginError(self):
		self.setWindowTitle("Error")
		self.busy.hide()
		error = "Inicie sesión antes de ver la información"
		self.iface.messageBar().pushMessage("Error", error, level=Qgis.Critical,duration=3)
		self.adjustSize()

	def objetoGeograficoSeleccionado(self, objetoGeografico):
		self.objetoGeografico = objetoGeografico

	def mostrarVentana(self):
		hiloBomba = threading.Thread(target=self.online.consultarBomba, args=(self.objetoGeografico.attribute('bomba'),))
		hiloBomba.start()
		ObtenerCapa().capa().removeSelection()

	def cargarDatos(self):
		bomba = self.online.getBomba()
		if bomba.getIdGrupo == -1:
			pass
		elif bomba.getIdGrupo == 0:
			self._loginError()
		else:
			self.resizeIcons()
			self.show()
			self.activateWindow()
			self.setProperty("state", "pantalla")
			self.labelEstado.setVisible(False)
			self.actualizarEstadoPantalla(bomba.getEstado)
			self.datoPresion.setText(bomba.getPresion)
			self.datoFlujo.setText(bomba.getFlujo)
			self.datoVoltaje1.setText(bomba.getVoltaje1)
			self.datoVoltaje2.setText(bomba.getVoltaje2)
			self.datoVoltaje3.setText(bomba.getVoltaje3)
			self.datoCorriente1.setText(bomba.getCorriente1)
			self.datoCorriente2.setText(bomba.getCorriente2)
			self.datoCorriente3.setText(bomba.getCorriente3)
			elementos = [(bomba.getFase1, self.iconFase1, self.iconFase1Off)]
			elementos.append((bomba.getFase2, self.iconFase2, self.iconFase2Off))
			elementos.append((bomba.getFase3, self.iconFase3, self.iconFase3Off))
			for dato, iconoOn, iconoOff in elementos:
				if dato == 1:
					iconoOn.setVisible(True)
					iconoOff.setVisible(False)
				else:
					iconoOn.setVisible(False)
					iconoOff.setVisible(True)
			self.labelId.setText(str(bomba.getNombre))
			self.setWindowTitle(str(bomba.getNombre))
			self.labelEstado.setText('')
			self.labelEstado.setText(str(bomba.getEstado))
			self.conectadoOn.setVisible(False)
			self.conectadoOff.setVisible(False)
			if bomba.getModoOperacion == 0:
				icon = QIcon()
				icon.addPixmap(QPixmap(':/icons/icons/icon_manual.png'))
				self.modo.setIcon(icon)
			elif bomba.getModoOperacion == 1:
				icon = QIcon()
				icon.addPixmap(QPixmap(':/icons/icons/icon_automatico.png'))
			self.revisarConectado(bomba)
			self.setStyle(self.style())

	def resizeIcons(self):
		iconUrls = (':/icons/icons/presion.png', ':/icons/icons/flujo.png', ':/icons/icons/voltaje.png',
					':/icons/icons/corriente.png')
		labels = (self.iconPresion, self.iconFlujo, self.iconVoltaje, self.iconCorriente)
		for iconUrl, label in zip(iconUrls, labels):
			height = int(label.size().height())
			width = int(label.size().width())
			icon = QPixmap(iconUrl)
			if height < width:
				label.setPixmap(icon.scaledToHeight(height, Qt.SmoothTransformation))
			else:
				label.setPixmap(icon.scaledToWidth(width, Qt.SmoothTransformation))
		iconUrls = (':/icons/icons/ledon.png', ':/icons/icons/ledon.png',
					':/icons/icons/ledon.png', ':/icons/icons/ledoff.png', ':/icons/icons/ledoff.png',
					':/icons/icons/ledoff.png')
		labels = (
			self.iconFase1, self.iconFase2, self.iconFase3, self.iconFase1Off, self.iconFase2Off,
			self.iconFase3Off)
		for iconUrl, label in zip(iconUrls, labels):
			height = int(label.size().height())
			icon = QPixmap(iconUrl)
			label.setPixmap(icon.scaledToHeight(height * .5, Qt.SmoothTransformation))
		try:
			estado = int(self.labelEstado.text())
		except ValueError:
			estado = 0
		if estado == 0 or estado == 1:
			iconBomba = QPixmap(':/images/images/bomba-off.png')
			self.imagenBomba.setPixmap(
				iconBomba.scaled(QSize(442,338), Qt.KeepAspectRatio, Qt.SmoothTransformation))
		#elif estado == 2 or estado == 3:
		#	self.bombaEncendida(self)
		firstLabels = (self.datoPresion, self.datoFlujo)
		labels = (self.datoVoltaje1, self.datoVoltaje2, self.datoVoltaje3, self.datoCorriente1,
				  self.datoCorriente2, self.datoCorriente3)
		fontSizeFirst = int(labels[0].size().height() / 1.5)
		fontSize = int(labels[0].size().height() / 4.5)
		fuente = 11
		maxFuente = 28
		if fontSize < fuente:
			fontSize = fuente
		if fontSizeFirst < fuente:
			fontSizeFirst = fuente
		if fontSize > maxFuente:
			fontSize = maxFuente
		if fontSizeFirst > maxFuente:
			fontSizeFirst = maxFuente
		for label in labels:
			label.setFont(QFont('Verdana', fontSize, QFont.Medium))
		for label in firstLabels:
			label.setFont(QFont('Verdana', fontSizeFirst, QFont.Medium))
		labels = (
			self.uniPresion, self.uniFlujo, self.uniVoltaje1, self.uniVoltaje2, self.uniVoltaje3,
			self.uniCorriente1, self.uniCorriente2, self.uniCorriente3)
		for label in labels:
			label.setFont(QFont('Verdana', fontSize / 1.5))
		labels = (self.labelF1, self.labelF2, self.labelF3)
		for label in labels:
			label.setFont(QFont('Verdana', fontSize / 1.5, QFont.Bold))
		self.busy.hide()

	def actualizarEstadoPantalla(self, estado):
		self.labelEstado.setText(str(estado))
		if estado == 0:
			self.interruptor.setEnabled(True)
			icon = QIcon()
			icon.addPixmap(QPixmap(':/buttons/icons/icon_off.png'))
			self.interruptor.setIcon(icon)
			self.barraEstado.setProperty("state", "off")
			self.interruptor.setProperty("state", "off")
			self.opciones.setProperty("state", "off")
			self.modo.setProperty("state", "off")
			iconBomba = QPixmap(':/images/images/bomba-off.png')
			size = self.imagenBomba.size()
			self.imagenBomba.setPixmap(iconBomba.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
		elif estado == 1:
			icon = QIcon()
			icon.addPixmap(QPixmap(':/buttons/icons/icon_off.png'))
			self.barraEstado.setProperty("state", "turning off")
			iconBomba = QPixmap(':/images/images/bomba-off.png')
			size = self.imagenBomba.size()
			self.imagenBomba.setPixmap(iconBomba.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
		elif estado == 2:
			icon = QIcon()
			icon.addPixmap(QPixmap(':/buttons/icons/icon_on.png'))
			self.barraEstado.setProperty("state", "turning on")
			self.bombaEncendida()
		elif estado == 3:
			self.interruptor.setEnabled(True)
			icon = QIcon()
			icon.addPixmap(QPixmap(':/buttons/icons/icon_on.png'))
			self.interruptor.setIcon(icon)
			self.barraEstado.setProperty("state", "on")
			self.interruptor.setProperty("state", "on")
			self.opciones.setProperty("state", "on")
			self.modo.setProperty("state", "on")
			self.bombaEncendida()
		self.barraEstado.setStyle(self.style())
		self.interruptor.setStyle(self.style())
		self.opciones.setStyle(self.style())

	#@staticmethod
	def bombaEncendida(self):
		movie = QMovie(":/images/images/bomba-animated.gif")
		labelSize = self.imagenBomba.size()
		ORIGINAL_WIDTH = 1412
		ORIGINAL_HEIGHT = 1080
		width = labelSize.width()
		height = labelSize.height()
		if labelSize.height() > labelSize.width():
			width = labelSize.width()
			height = width * ORIGINAL_HEIGHT / ORIGINAL_WIDTH
		else:
			height = labelSize.height()
			width = height * ORIGINAL_WIDTH / ORIGINAL_HEIGHT
		size = QSize(width, height)
		movie.setScaledSize(size)
		movie.setCacheMode(1)
		self.imagenBomba.setMovie(movie)
		movie.start()

	def revisarConectado(self, bomba):
		conectado = bomba.getConectado
		if bomba.getIdCoordinador > 0:
			coordinador = bomba.getCoordinador
			conectado = coordinador.getConectado
		if conectado > 0:
			self.labelId.setEnabled(True)
			self.conectadoOn.setVisible(True)
			self.conectadoOff.setVisible(False)
		else:
			self.labelId.setEnabled(False)
			self.conectadoOn.setVisible(False)
			self.conectadoOff.setVisible(True)

	def cambiarEstado(self):
		bomba = self.online.getBomba()
		flagCoordinador = 1
		if bomba.getIdCoordinador == 0:
			flagCoordinador = 0
			password = self.online.consultarPasswordIoT(bomba.getIdDispositivo, 0)
		if flagCoordinador:
			coordinador = bomba.getCoordinador
			password = self.online.consultarPasswordIoT(coordinador.getIdDispositivo, 1)
		if self.comprobarPassword(password):
			if flagCoordinador:
				topic = "/sensores/%s" % coordinador.getIdDispositivo
			else:
				topic = "/sensores/%s" % bomba.getIdDispositivo
			cadena = ''
			if bomba.getEstado == 0:
				self.barraEstado.setProperty("state", "turning on")
				if flagCoordinador:
					cadena = "{\"Tipo\":\"Config\",\"Cadena\":\"WB1_%s\"}" % bomba.getIdDispositivo
				else:
					cadena = "{\"Tipo\":\"Config\",\"Cadena\":\"WB1\"}"
				# self.online.actualizarEstadoBomba(bomba.getIdGrupo, 2)
				self.iface.messageBar().pushMessage("Aviso", strings.general[3], level=Qgis.Info, duration=7)
			elif bomba.getEstado == 3:
				self.barraEstado.setProperty("state", "turning off")
				if flagCoordinador:
					cadena = "{\"Tipo\":\"Config\",\"Cadena\":\"WB0_%s\"}" % bomba.getIdDispositivo
				else:
					cadena = "{\"Tipo\":\"Config\",\"Cadena\":\"WB0\"}"
				# self.online.actualizarEstadoBomba(bomba.getIdGrupo, 1)
				self.iface.messageBar().pushMessage("Aviso", strings.general[4], level=Qgis.Info, duration=7)
			password = password[0]['password']
			#print(topic, cadena)
			Publisher().publicar(topic, cadena, password)

	def comprobarPassword(self, password):
		if password == 1:
			self.iface.messageBar().pushMessage("Error", strings.general[1], level=Qgis.Critical, duration=7)
			return False
		elif password == 2:
			self.iface.messageBar().pushMessage("Error", strings.general[2], level=Qgis.Critical, duration=7)
			return False
		return True

	def mostrarMenu(self):
		menu = QMenu()
		menu.setStyleSheet(
			"QMenu{background-color: black; color: white; font-family: Verdana; font-size: 11pt;}"
			"QMenu:item:active:selected{background-color: #444444;}")
		accionHorarios = QAction("Programar horarios", menu)
		bomba = self.online.getBomba()
		icon = QIcon()
		icon.addPixmap(QPixmap(':/icons/icons/datetime.png'))
		accionHorarios.setIcon(icon)
		accionHorarios.triggered.connect(self.programarHorarios)
		menu.addAction(accionHorarios)
		menu.exec(QCursor.pos())

	def programarHorarios(self):
		publisher = Publisher()
		bomba = self.online.getBomba()
		ProgramarHorarios(bomba, publisher, self.online, True)

	def cambiarModo(self):
		bomba = self.online.getBomba()
		self.online.signalPassword.connect(self.cambiarModoSlot)
		if bomba.getIdCoordinador == 0:
			self.online.consultarPasswordIoT(bomba.getIdDispositivo, 0, True)
		else:
			self.online.consultarPasswordIoT(bomba.getCoordinador.getIdDispositivo, 1, True)

	def cambiarModoSlot(self, password):
		bomba = self.online.getBomba()
		try:
			self.comprobarPassword(int(password))
		except ValueError:
			if bomba.getIdCoordinador == 0:
				topic = "/sensores/%s" % bomba.getIdDispositivo
			else:
				topic = "/sensores/%s" % bomba.getCoordinador.getIdDispositivo
			cadena = '{"Tipo":"Config","Cadena":"Wq0"}'
			if bomba.getModoOperacion == 0:
				cadena = '{"Tipo":"Config","Cadena":"Wq1"}'
			Publisher().publicar(topic, cadena, password)
		self.online.signalPassword.disconnect()
