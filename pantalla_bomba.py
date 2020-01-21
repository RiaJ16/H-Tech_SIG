# -*- coding: UTF8 -*-

import os
import qgis.utils
import threading

from functools import partial

from qgis.core import Qgis

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCursor, QFont, QIcon, QMovie, QPixmap
from PyQt5.QtWidgets import QAction, QLayout, QMenu, QWidget

from .busy_icon import BusyIcon
from .programar_horarios import ProgramarHorarios
from .dragon.publisher import Publisher
from .dragon.strings import strings_dragon as strings
from .obtener_capa import ObtenerCapa
from .q_dialog_next import QDialogNext

from .dragon.ui.resources import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'dragon/ui/pantalla.ui'))


class PantallaBomba(QDialogNext, FORM_CLASS):

	def __init__(self, online, parent=None):
		"""Constructor."""
		super(PantallaBomba, self).__init__(parent)
		self.widget = QWidget()
		uic.loadUi(os.path.join(os.path.dirname(__file__), 'kraken.ui'), self)
		uic.loadUi(os.path.join(os.path.dirname(__file__), 'dragon/ui/pantalla.ui'), self.widget)
		self.layout().addWidget(self.widget)
		#self.setupUi(self)
		self.online = online
		self.iface = qgis.utils.iface
		self.setMovable(self.kraken)
		self.setBotonCerrar(self.botonCerrar)
		#self.widget.setVisible(True)
		#self.layout().setSizeConstraint(QLayout.SetFixedSize)
		self.busy = BusyIcon(self.layout())
		self.busy.startAnimation()
		self._signals()
		self.setWindowIcon(QIcon(":/sigrdap/icons/bomba2.png"))
		#self._comprobarPermisos()

	def _signals(self):
		self.online.signalBombaConsultada.connect(self.cargarDatos)
		self.widget.interruptor.clicked.connect(self.cambiarEstado)
		self.widget.opciones.clicked.connect(self.mostrarMenu)
		self.widget.modo.clicked.connect(self.cambiarModo)

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
			self.widget.setProperty("state", "pantalla")
			self.widget.labelEstado.setVisible(False)
			self.actualizarEstadoPantalla(bomba.getEstado)
			self.widget.datoPresion.setText(bomba.getPresion)
			self.widget.datoFlujo.setText(bomba.getFlujo)
			self.widget.datoVoltaje1.setText(bomba.getVoltaje1)
			self.widget.datoVoltaje2.setText(bomba.getVoltaje2)
			self.widget.datoVoltaje3.setText(bomba.getVoltaje3)
			self.widget.datoCorriente1.setText(bomba.getCorriente1)
			self.widget.datoCorriente2.setText(bomba.getCorriente2)
			self.widget.datoCorriente3.setText(bomba.getCorriente3)
			elementos = [(bomba.getFase1, self.widget.iconFase1, self.widget.iconFase1Off)]
			elementos.append((bomba.getFase2, self.widget.iconFase2, self.widget.iconFase2Off))
			elementos.append((bomba.getFase3, self.widget.iconFase3, self.widget.iconFase3Off))
			for dato, iconoOn, iconoOff in elementos:
				if dato == 1:
					iconoOn.setVisible(True)
					iconoOff.setVisible(False)
				else:
					iconoOn.setVisible(False)
					iconoOff.setVisible(True)
			self.widget.labelId.setText(str(bomba.getNombre))
			self.setWindowTitle(str(bomba.getNombre))
			self.widget.labelEstado.setText('')
			self.widget.labelEstado.setText(str(bomba.getEstado))
			self.widget.conectadoOn.setVisible(False)
			self.widget.conectadoOff.setVisible(False)
			if bomba.getModoOperacion == 0:
				icon = QIcon()
				icon.addPixmap(QPixmap(':/icons/icons/icon_manual.png'))
				self.widget.modo.setIcon(icon)
			elif bomba.getModoOperacion == 1:
				icon = QIcon()
				icon.addPixmap(QPixmap(':/icons/icons/icon_automatico.png'))
			self.revisarConectado(bomba)
			self.widget.setStyle(self.style())

	def resizeIcons(self):
		iconUrls = (':/icons/icons/presion.png', ':/icons/icons/flujo.png', ':/icons/icons/voltaje.png',
					':/icons/icons/corriente.png')
		labels = (self.widget.iconPresion, self.widget.iconFlujo, self.widget.iconVoltaje, self.widget.iconCorriente)
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
			self.widget.iconFase1, self.widget.iconFase2, self.widget.iconFase3, self.widget.iconFase1Off, self.widget.iconFase2Off,
			self.widget.iconFase3Off)
		for iconUrl, label in zip(iconUrls, labels):
			height = int(label.size().height())
			icon = QPixmap(iconUrl)
			label.setPixmap(icon.scaledToHeight(height * .5, Qt.SmoothTransformation))
		try:
			estado = int(self.widget.labelEstado.text())
		except ValueError:
			estado = 0
		if estado == 0 or estado == 1:
			iconBomba = QPixmap(':/images/images/bomba-off.png')
			self.widget.imagenBomba.setPixmap(
				iconBomba.scaled(QSize(442,338), Qt.KeepAspectRatio, Qt.SmoothTransformation))
		#elif estado == 2 or estado == 3:
		#	self.bombaEncendida(self)
		firstLabels = (self.widget.datoPresion, self.widget.datoFlujo)
		labels = (self.widget.datoVoltaje1, self.widget.datoVoltaje2, self.widget.datoVoltaje3, self.widget.datoCorriente1,
				  self.widget.datoCorriente2, self.widget.datoCorriente3)
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
			self.widget.uniPresion, self.widget.uniFlujo, self.widget.uniVoltaje1, self.widget.uniVoltaje2, self.widget.uniVoltaje3,
			self.widget.uniCorriente1, self.widget.uniCorriente2, self.widget.uniCorriente3)
		for label in labels:
			label.setFont(QFont('Verdana', fontSize / 1.5))
		labels = (self.widget.labelF1, self.widget.labelF2, self.widget.labelF3)
		for label in labels:
			label.setFont(QFont('Verdana', fontSize / 1.5, QFont.Bold))
		self.busy.hide()

	def actualizarEstadoPantalla(self, estado):
		self.widget.labelEstado.setText(str(estado))
		if estado == 0:
			self.widget.interruptor.setEnabled(True)
			icon = QIcon()
			icon.addPixmap(QPixmap(':/buttons/icons/icon_off.png'))
			self.widget.interruptor.setIcon(icon)
			self.widget.barraEstado.setProperty("state", "off")
			self.widget.interruptor.setProperty("state", "off")
			self.widget.opciones.setProperty("state", "off")
			self.widget.modo.setProperty("state", "off")
			iconBomba = QPixmap(':/images/images/bomba-off.png')
			size = self.widget.imagenBomba.size()
			self.widget.imagenBomba.setPixmap(iconBomba.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
		elif estado == 1:
			icon = QIcon()
			icon.addPixmap(QPixmap(':/buttons/icons/icon_off.png'))
			self.widget.barraEstado.setProperty("state", "turning off")
			iconBomba = QPixmap(':/images/images/bomba-off.png')
			size = self.widget.imagenBomba.size()
			self.widget.imagenBomba.setPixmap(iconBomba.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
		elif estado == 2:
			icon = QIcon()
			icon.addPixmap(QPixmap(':/buttons/icons/icon_on.png'))
			self.widget.barraEstado.setProperty("state", "turning on")
			self.bombaEncendida()
		elif estado == 3:
			self.widget.interruptor.setEnabled(True)
			icon = QIcon()
			icon.addPixmap(QPixmap(':/buttons/icons/icon_on.png'))
			self.widget.interruptor.setIcon(icon)
			self.widget.barraEstado.setProperty("state", "on")
			self.widget.interruptor.setProperty("state", "on")
			self.widget.opciones.setProperty("state", "on")
			self.widget.modo.setProperty("state", "on")
			self.bombaEncendida()
		self.widget.barraEstado.setStyle(self.style())
		self.widget.interruptor.setStyle(self.style())
		self.widget.opciones.setStyle(self.style())

	#@staticmethod
	def bombaEncendida(self):
		movie = QMovie(":/images/images/bomba-animated.gif")
		labelSize = self.widget.imagenBomba.size()
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
		self.widget.imagenBomba.setMovie(movie)
		movie.start()

	def revisarConectado(self, bomba):
		conectado = bomba.getConectado
		if bomba.getIdCoordinador > 0:
			coordinador = bomba.getCoordinador
			conectado = coordinador.getConectado
		if conectado > 0:
			self.widget.labelId.setEnabled(True)
			self.widget.conectadoOn.setVisible(True)
			self.widget.conectadoOff.setVisible(False)
		else:
			self.widget.labelId.setEnabled(False)
			self.widget.conectadoOn.setVisible(False)
			self.widget.conectadoOff.setVisible(True)

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
				self.widget.barraEstado.setProperty("state", "turning on")
				if flagCoordinador:
					cadena = "{\"Tipo\":\"Config\",\"Cadena\":\"WB1_%s\"}" % bomba.getIdDispositivo
				else:
					cadena = "{\"Tipo\":\"Config\",\"Cadena\":\"WB1\"}"
				# self.online.actualizarEstadoBomba(bomba.getIdGrupo, 2)
				self.iface.messageBar().pushMessage("Aviso", strings.general[3], level=Qgis.Info, duration=7)
			elif bomba.getEstado == 3:
				self.widget.barraEstado.setProperty("state", "turning off")
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
