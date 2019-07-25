# -*- coding: UTF8 -*-

import os
import qgis.utils
import requests
import sys
import threading

from qgis.core import *

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap

from .busy_icon import BusyIcon
from .obtener_capa import ObtenerCapa
from .online import Online
from .sensor import Sensor

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'eliminar_sensor.ui'))

class EliminarSensor(QtWidgets.QDialog, FORM_CLASS, QObject):

	signalCambio = pyqtSignal()

	def __init__(self,online,parent=None):
		QObject.__init__(self)
		super(EliminarSensor, self).__init__(parent)
		self.setupUi(self)
		self.iface = qgis.utils.iface
		self.busy = BusyIcon(self.layout())
		self.busy.startAnimation()
		self.online = online
		self.internet = True
		self.__signals()
		self.inicializar()

	def __signals(self):
		self.botonCancelar.clicked.connect(self.hide)
		self.online.signalSensorConsultado.connect(self.consultarSensor)
		self.online.signalConsultarGrupo.connect(self.actualizarFoto)
		self.online.signalErrorConexion.connect(self.__errorConexion)

	def __errorConexion(self):
		self.setWindowTitle("Error de conexión")
		self.labelGrupo.setText("Error de conexión")
		self.loading(False)
		self.botonAceptar.setEnabled(False)
		self.__mostrarOcultar(False)
		error = "Conéctese a internet para hacer uso de esta aplicación."
		self.label.setText(error)
		self.iface.messageBar().pushMessage("Error de conexión", error, level=Qgis.Critical,duration=3)

	def __errorLogin(self):
		self.setWindowTitle("Error de autenticación")
		self.labelGrupo.setText("Error de autenticación")
		self.loading(False)
		self.botonAceptar.setEnabled(False)
		self.__mostrarOcultar(False)
		error = "No se ha iniciado la sesión. Inicie sesión y vuelva a intentarlo."
		self.label.setText(error)
		self.iface.messageBar().pushMessage("Error", error, level=Qgis.Critical,duration=3)

	def __mostrarOcultar(self,flag):
		self.labelFoto.setVisible(flag)
		self.labelDireccion.setVisible(flag)
		self.labelTipo.setVisible(flag)
		self.adjustSize()
		self.adjustSize()

	def inicializar(self):
		idFeature = self.obtenerId()
		t1 = threading.Thread(target=self.online.consultarSensorPorIdFeature,args=(idFeature,))
		t1.start()
		self.loading(True)
		self.adjustSize()
		self.show()

	def consultarSensor(self):
		try:
			sensor = self.online.getSensor()
			self.idSensor = sensor.idSensor
			if sensor.idSensor == 0:
				self.__errorLogin()
			else:
				self.labelDireccion.setText("<b><font color='#2980b9'>Ubicación:</font></b> %s, %s, %s, %s" % (sensor.calle,sensor.colonia,sensor.cp,sensor.municipioTexto))
				self.labelTipo.setText("<b><font color='#2980b9'>Tipo:</font></b> %s" % sensor.tipoSensorTexto)
				self.labelGrupo.setText("<b>%s</b>" % sensor.grupoTexto.upper())
				#self.setWindowTitle("%s: sensor de %s" % (sensor.grupoTexto,sensor.tipoSensorTexto.lower()))
				t1 = threading.Thread(target=self.online.consultarGrupoPorId,args=(sensor.grupo,))
				t1.start()
				try:
					self.botonAceptar.clicked.disconnect(self.eliminarObjetoGeografico)
				except:
					pass
				self.botonAceptar.clicked.connect(self.eliminarRegistro)
		except:
			self.label.setText("Este objeto no está asociado con ningún sensor. ¿Desea eliminarlo?")
			self.loading(False,False)
			try:
				self.botonAceptar.clicked.disconnect(self.eliminarRegistro)
			except:
				pass
			self.botonAceptar.clicked.connect(self.eliminarObjetoGeografico)
	
	def eliminarRegistro(self):
		codigo = self.online.eliminarSensor(self.idSensor)
		if codigo == '0':
			self.eliminarObjetoGeografico()
			#self.signalCambio.emit()
		elif codigo == '1':
			self.iface.messageBar().pushMessage("Error de permisos", "No cuenta con los permisos necesarios para realizar esta operación", level=Qgis.Critical,duration=3)
			#self.signalCambio.emit()
			#print("Abrir ventana de login")

	def eliminarObjetoGeografico(self):
		capaActiva = ObtenerCapa().capa()
		capaActiva.dataProvider().deleteFeatures([capaActiva.selectedFeatures()[0].id()])
		capaActiva.triggerRepaint()
		self.hide()

	def obtenerId(self):
		capaActiva = ObtenerCapa().capa()
		objetoGeografico = capaActiva.selectedFeatures()[0]
		id = objetoGeografico.attribute('id')
		return id

	def actualizarFoto(self):
		try:
			filename = self.online.grupo.foto
		except:
			filename = ""
		if filename == "" or filename == None:
			filename = "%s\\.sigrdap\\nodisponible.png" % os.environ['HOME']
		foto = QPixmap(filename)
		newHeight = 80
		try:
			newWidth = foto.width()*85/foto.height()
		except:
			newWidth = 0
		if newWidth > 154:
			newWidth = 154
			newHeight = foto.height()*newWidth/foto.width()
		self.labelFoto.setPixmap(foto.scaled(newWidth,newHeight))
		self.adjustSize()
		self.adjustSize()
		newWidth = foto.width()
		newHeight = foto.height()
		if newWidth > 1024:
			newWidth = 1024
			newHeight = newHeight * newWidth / foto.width()
		html = "<p><img src=\'%s' width='%f' height='%f'></p>" % (filename,newWidth,newHeight)
		self.labelFoto.setToolTip(html)
		self.loading(False)

	def loading(self,flag=True,asFlag=True):
		self.busy.setVisible(flag)
		self.botonAceptar.setEnabled(not flag)
		self.adjustSize()
