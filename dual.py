# -*- coding: UTF8 -*-

import os
import datetime
import qgis.utils
#import serial
import win32com.shell.shell as shell
import win32serviceutil as w32su

from qgis.core import *
from qgis.gui import *

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QTime, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QColor, QBrush
from PyQt5.QtWidgets import QTableWidgetItem

#from Reloj import Reloj
#from Sensor import Sensor
#from LectorDatos import LectorDatos
#from Alarmas import Alarmas
#from abstract_worker import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'dual.ui'))

class Dual(QtWidgets.QDockWidget,FORM_CLASS,QObject):

	signalNuevoSensor = pyqtSignal(str)
	signalNuevoDato = pyqtSignal(str)

	def __init__(self,online,parent=None):
		QObject.__init__(self)
		super(Dual, self).__init__(parent)
		self.setupUi(self)
		self.iface = qgis.utils.iface
		self.online = online
		self.iface.mainWindow().addDockWidget(Qt.RightDockWidgetArea,self)
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.setVisible(False)
		self.setFloating(False)
		self.running = False
		#self.botonBroadcast.clicked.connect(self.enviarBroadcast)
		self.botonIniciarPeticion.clicked.connect(self.iniciarPeticion)
		self.displayTiempoRestante.display("00:00")
		self.h_list = []
		self.tablaSensores.itemSelectionChanged.connect(self.seleccionarSensor)
		self.tablaSensores.itemDoubleClicked.connect(self.dobleClick)
		self.tablaDatos.itemDoubleClicked.connect(self.identificarSensor)
		self.selectorModo.currentIndexChanged.connect(self.cambiarModo)
		self.cargarTabla()
		self.sensoresActivos = []
		self.direccionesDatos = []
		#self.comprobarServicio()

	def comprobarServicio(self):
		if w32su.QueryServiceStatus("PyXbeeSvc")[1] == 4:
			archivo = open("%s\.sigrdap\opcion" % os.environ['HOME'], 'r')
			opcion = archivo.readline()
			tiempo = opcion[0]
			modo = opcion[1]
			self.selectorTiempo.setCurrentIndex(int(tiempo))
			self.selectorModo.setCurrentIndex(int(modo))
			self.iniciarPeticion(True)

	def iniciarPeticion(self,servicioActivo=False):
		if(self.conectarPuertoSerial() or (self.selectorModo.currentIndex() == 1) or self.running or servicioActivo):
			if not self.running:
				self.lectorDatos = LectorDatos(10)
				self.alarma = Alarmas()
				self.lectorDatos.signalNuevoDato.connect(self.actualizarTabla)
				self.lectorDatos.signalNuevoDato.connect(self.alarma.actualizar)
				self.lectorDatos.signalNuevoDato.connect(self.nuevoDato)
				commands = 'net start PyXbeeSvc'
				archivo = open("%s\.sigrdap\opcion" % os.environ['HOME'], 'w+')
				archivo.write("%s%s1" % (self.selectorTiempo.currentIndex(),self.selectorModo.currentIndex()))
				archivo.close()
				try:
					if not servicioActivo:
						shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+commands)
					self.cambiarEstadoBotones(True)
					self.running = True
					self.botonIniciarPeticion.setIcon(QIcon(":/VentanaZigBee/icons/stop.png"))
					self.i = self.obtenerTiempoRestante()
					self.reloj = Reloj()
					self.reloj.signalSecond.connect(self.actualizarReloj)
					self.reloj.start()
				except:
					print("Operación cancelada por el usuario")
				start_worker(self.lectorDatos, self.iface, 'testing the worker')
			else:
				commands = 'net stop PyXbeeSvc'
				try:
					self.lectorDatos.stop()
					self.lectorDatos.signalNuevoDato.disconnect()
					self.lectorDatos = None
					shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+commands)
					self.running = False
					archivo = open("%s\.sigrdap\opcion" % os.environ['HOME'], 'w+')
					archivo.write("%s%s0" % (self.selectorTiempo.currentIndex(),self.selectorModo.currentIndex()))
					archivo.close()
					self.cambiarEstadoBotones(False)
					self.botonIniciarPeticion.setIcon(QIcon(":/VentanaZigBee/icons/play.png"))
					self.reloj.signalSecond.disconnect(self.actualizarReloj)
					self.reloj.stop()
					self.displayTiempoRestante.display("00:00")
					del self.reloj
				except:
					print("Operación cancelada por el usuario")
		else:
			self.iface.messageBar().pushMessage("Error","No se encontró un dispositivo ZigBee conectado. Conéctelo o cambie al modo En línea",level=QgsMessageBar.CRITICAL,duration=3)

	def obtenerTiempoRestante(self):
		ahora = datetime.datetime.now()
		segundosRestantes = 60-ahora.second
		tiempo = self.selectorTiempo.currentIndex()
		if tiempo == 0:
			modOp = 1
		if tiempo == 1:
			modOp = 15
		elif tiempo == 2:
			modOp = 30
		elif tiempo == 3:
			modOp = 60
		minutosRestantes = (59 - ahora.minute) % modOp
		tiempoRestante = (minutosRestantes * 60) + segundosRestantes
		tiempoRestante = tiempoRestante % (modOp * 60)
		return tiempoRestante

	def actualizarReloj(self):
		minuto = (self.i/60)
		segundo = self.i % 60
		tiempoString = "%02d:%02d" % (minuto,segundo)
		self.displayTiempoRestante.display(tiempoString)
		self.i -= 1
		indice = self.selectorTiempo.currentIndex()
		modo = self.selectorModo.currentIndex()
		if self.i == -1:
			if indice == 0:
				self.i = 59
			if indice == 1:
				self.i = 899
			if indice == 2:
				self.i = 1799
			if indice == 3:
				self.i = 3599
		if modo == 0:
			if indice == 0:
				if self.i == 45:
					self.actualizarEstado()
			if indice == 1:
				if self.i == 885:
					self.actualizarEstado()
			if indice == 2:
				if self.i == 1785:
					self.actualizarEstado()
			if indice == 3:
				if self.i == 3585:
					self.actualizarEstado()
		elif modo == 1:
			if indice == 1:
				if self.i == 885:
					self.actualizarEstado()
					print("Actualizado 15")

	def cambiarEstadoBotones(self,bandera):
		self.displayTiempoRestante.setEnabled(bandera)
		self.selectorTiempo.setEnabled(not bandera)
		self.selectorModo.setEnabled(not bandera)

	def actualizarTabla(self,linea):
		valorActual = self.tablaDatos.rowCount()
		self.tablaDatos.insertRow(valorActual)
		address = linea.split('\t')[0]
		dato = linea.split('\t')[1]
		self.direccionesDatos.append([True,address,dato])
		itemDato = QTableWidgetItem("%s" % dato)
		self.tablaDatos.setItem(valorActual,1,itemDato)
		self.etiquetar(self.leerDato(address,dato))

	def leerDato(self,direccion,dato):
		tipoDato = 2
		tipoSensor = 0
		caracterTipo = dato[0]
		if dato[0] == 'C' or dato[0] == 'c':
			tipoDato = 0
			caracterTipo = dato[1]
		if caracterTipo == 'P' or caracterTipo == 'p':
			tipoSensor = 1
			tipoDato = 1
		elif caracterTipo == 'F' or caracterTipo == 'f':
			tipoSensor = 2
			tipoDato = 1
		elif caracterTipo == 'N' or caracterTipo == 'n':
			tipoSensor = 3
			tipoDato = 1
		if not (tipoDato == 2): #si es una respuesta al broadcast o envío de datos
			try:
				sensor = self.conector.consultarSensorPorRadio(direccion,tipoSensor)
				try:
					self.sensoresActivos.append(sensor)
					return self.conector.consultarPozo(sensor.pozo)
				except:
					self.conector.actualizarEstado(sensor.IDSensor,3)
					return self.conector.consultarNombrePozo(sensor.pozo)
			except:
				if not (tipoSensor == 0):
					self.direccionesDatos[self.tablaDatos.rowCount()-1][0] = False
					return "Desconocido"

	def comprobarTipoDato(self,dato0,dato1):
		tipoDato = 2
		tipoSensor = 0
		caracterTipo = dato0
		if dato0 == 'C' or dato0 == 'c':
			tipoDato = 0
			caracterTipo = dato1
		if caracterTipo == 'P' or caracterTipo == 'p':
			tipoSensor = 1
			tipoDato = 1
		elif caracterTipo == 'F' or caracterTipo == 'f':
			tipoSensor = 2
			tipoDato = 1
		elif caracterTipo == 'N' or caracterTipo == 'n':
			tipoSensor = 3
			tipoDato = 1
		return [tipoDato,tipoSensor]

	def identificarSensor(self):
		direccion = self.direccionesDatos[self.tablaDatos.currentRow()][1]
		if self.direccionesDatos[self.tablaDatos.currentRow()][0]:
			self.iface.messageBar().pushMessage("Aviso", "Dirección del Xbee copiada al portapapeles",level=QgsMessageBar.INFO,duration=3)
			os.system("echo %s | clip" % direccion)
		else:
			self.signalNuevoSensor.emit(direccion)

	def etiquetar(self,etiqueta):
		item = QTableWidgetItem("%s" % etiqueta)
		self.tablaDatos.setItem(self.tablaDatos.rowCount()-1,0,item)

	def actualizarTablaDatos(self):
		i = 0
		for dato in self.direccionesDatos:
			try:
				sensor = self.conector.consultarSensorPorRadio(dato[1],self.comprobarTipoDato(dato[2][0],dato[2][1:])[1])
				nombrePozo = self.conector.consultarPozo(sensor.pozo)
				dato[0] = True
			except:
				nombrePozo = "Desconocido"
				dato[0] = False
			self.tablaDatos.setItem(i,0,QTableWidgetItem(nombrePozo))
			i += 1

#Éstos son los métodos relacionados a la pestaña del estado de los sensores

	def cargarTabla(self):
		self.limpiarTabla()
		#self.sensores = self.conector.consultarSensoresN()
		self.sensores = []
		i = 0
		for sensor in self.sensores:
			self.tablaSensores.insertRow(i)
			items = []
			items.append(QTableWidgetItem("%s, %s" % (sensor.calle,sensor.colonia)))
			tipoSensor = self.conector.consultarNombreID(sensor.sensor)
			items.append(QTableWidgetItem("%s" % tipoSensor))
			j = 0
			for item in items:
				item.setBackground(self.colorEstados(int(sensor.estado)))
				item.setFlags(item.flags() ^ Qt.ItemIsEditable)
				self.tablaSensores.setItem(i,j,item)
				j += 1
			i += 1

	def colorEstados(self,estado):
		if estado == 1:
			color = QBrush(QColor(231, 76, 60))
		elif estado == 2:
			color = QBrush(QColor(241, 196, 15))
		elif estado == 3:
			color = QBrush(QColor(39, 174, 96))
		else:
			color = QBrush(QColor(236, 240, 241))
		return color
	
	def limpiarTabla(self):
		while not self.tablaSensores.rowCount() == 0:
			self.tablaSensores.removeRow(self.tablaSensores.rowCount()-1)

	def seleccionarSensor(self):
		capaActiva = self.obtenerCapa()
		self.iface.mapCanvas().setSelectionColor(QColor(44, 62, 80))
		try:
			self.tablaSensores.selectedItems()[0]
			capaActiva.selectAll()
			seleccionados = capaActiva.selectedFeatures()
			try:
				self.tablaSensores.selectRow(self.tablaSensores.currentRow())
				idFeature = int(self.sensores[self.tablaSensores.currentRow()].idFeature)
				for caracteristica in seleccionados:
					if idFeature == caracteristica.attribute('id'):
						id = caracteristica.id()
				capaActiva.removeSelection()
				capaActiva.select(id)
				self.resaltarObjetos()
			except:
				capaActiva.removeSelection()
		except:
			capaActiva.removeSelection()

	def dobleClick(self):
		capaActiva = self.obtenerCapa()
		try:
			capaActiva.selectedFeatures()[0]
			box = capaActiva.boundingBoxOfSelected()
			self.iface.mapCanvas().setExtent(box)
			self.iface.mapCanvas().refresh()
		except:
			pass

	def resaltarObjetos(self):
		capaActiva = self.obtenerCapa()
		# remove all highlight objects
		for h in range(len(self.h_list)):
			self.h_list.pop(h)
		# create highlight geometries for selected objects
		for i in capaActiva.selectedFeatures():
			h = QgsHighlight(self.iface.mapCanvas(), i.geometry(), capaActiva)
		# set highlight symbol properties
			h.setColor(QColor(0,0,0,180))
			h.setWidth(12)
			h.setFillColor(QColor(0,0,0,180))
			self.h_list.append(h)
		capaActiva.removeSelection()

	def obtenerCapa(self):
		capa = ''
		for layer in QgsMapLayerRegistry.instance().mapLayers().values():
			if layer.name() == "Sensores":
				capa = layer
				break
		return capa

	def actualizarEstado(self):
		#self.alarma.buscarAlarmas()
		self.cargarTabla()
		listaRespuestas = []
		if not (self.sensoresActivos == []):
			i = 0
			for sensor in self.sensores:
				for sensorActivo in self.sensoresActivos:
					listaRespuestas.append(False)
					if sensor.IDSensor == sensorActivo.IDSensor:
						listaRespuestas[i] = True
						break
				i += 1
		else:
			for sensor in self.sensores:
				listaRespuestas.append(False)
		i = 0
		for sensor in self.sensores:
			if listaRespuestas[i]:
				if sensor.estado == 0:
					self.conector.actualizarEstado(sensor.IDSensor,2)
				elif sensor.estado <= 2:
					self.conector.actualizarEstado(sensor.IDSensor,sensor.estado+1)
			else:
				if sensor.estado == 0:
					self.conector.actualizarEstado(sensor.IDSensor,1)
				elif sensor.estado >= 2:
					self.conector.actualizarEstado(sensor.IDSensor,sensor.estado-1)
			i += 1
		self.sensoresActivos = []
		self.cargarTabla()

	def conectarPuertoSerial(self):
		conectado = False
		try:
			serial.tools.list_ports.comports()[0]
			for puerto in serial.tools.list_ports.comports():
				try:
					serialPort = serial.Serial(puerto.device,9600)
					conectado = True
					serialPort.close()
					break
				except:
					conectado = False
		except:
			conectado = False
		#return conectado
		return True

	def cambiarModo(self):
		if self.selectorModo.currentIndex() == 1:
			self.selectorTiempo.setVisible(False)
			self.selectorTiempo.setCurrentIndex(1)
		else:
			self.selectorTiempo.setVisible(True)

	def nuevoDato(self,dato):
		self.signalNuevoDato.emit(dato)