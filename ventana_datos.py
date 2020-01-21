# -*- coding: utf-8 -*-

import os
import qgis.utils
import requests
import threading

from qgis.core import *
from qgis.gui import *

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QIcon, QMovie, QValidator
from PyQt5.QtWidgets import QComboBox, QLabel, QLineEdit, QPushButton

from .alarmas import Alarmas
from .busy_icon import BusyIcon
from .obtener_capa import ObtenerCapa
from .online import Online
from .q_dialog_next import QDialogNext
from .sensor import Sensor
from .validacion import Validacion


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ventana_datos.ui'))


class VentanaDatos(QDialogNext, FORM_CLASS,QObject):

	signalCambio = pyqtSignal()
	signalCerrada = pyqtSignal()
	internet = True

	def __init__(self, online, direccion='', parent=None, editar=False):
		"""Constructor."""
		QObject.__init__(self)
		super(VentanaDatos, self).__init__(parent)
		self.setupUi(self)
		self.setMovable(self.kraken)
		self.setBotonCerrar(self.botonCerrar)
		if editar:
			self.setWindowIcon(QIcon(":/sigrdap/icons/edit.png"))
		self.botonOnline.setVisible(False)
		self.iface = qgis.utils.iface
		self.online = online
		#if not self.online.login():
		#	self.internet = False
		self.__signals()
		self.editIdDispositivo.setText(str(direccion))
		self.busy = BusyIcon(self.layout())
		self.busy.startAnimation()
		#self.adjustSize()
		#if self.internet:
		#	self.llenarLista()

	def __signals(self):
		#self.online.signalErrorConexion.connect(self.__errorConexion)
		self.botonGuardar.clicked.connect(self.validarAlEnviar)
		self.editAltura.textChanged.connect(self.actualizarMaximo)
		self.online.signalMunicipios.connect(self.__llenarMunicipios)
		self.online.signalTiposSensor.connect(self.__llenarTiposSensor)
		self.online.signalGrupos.connect(self.__llenarGrupos)
		self.activarAlarma.clicked.connect(self.checkboxCambiada)
		self.online.signalGenerarId.connect(self.__generarId)
		self.online.signalConsultarId.connect(self.hiloSensor)
		self.selectorTipoSensor.currentIndexChanged.connect(self.sensorCambiado)
		self.online.signalSensorConsultado.connect(self.obtenerSensor)
		self.online.signalLoggedIn.connect(self._mostrarVentana)

	def disconnectSignals(self):
		self.online.signalMunicipios.disconnect(self.__llenarMunicipios)
		self.online.signalTiposSensor.disconnect(self.__llenarTiposSensor)
		self.online.signalGrupos.disconnect(self.__llenarGrupos)
		self.online.signalGenerarId.disconnect(self.__generarId)
		self.online.signalConsultarId.disconnect(self.hiloSensor)
		self.online.signalSensorConsultado.connect(self.obtenerSensor)
		self.online.signalLoggedIn.disconnect(self._mostrarVentana)

	def __errorConexion(self):
		self.internet = False
		error = "Conéctese a internet para hacer uso de esta aplicación"
		self.iface.messageBar().pushMessage("Error de conexión", error, level=Qgis.Critical,duration=3)

	def __errorLogin(self):
		self.internet = False
		error = "No se ha iniciado la sesión. Inicie sesión y vuelva a intentarlo."
		self.iface.messageBar().pushMessage("Error", error, level=Qgis.Critical,duration=3)

	def inicializar(self,bandera,x=0,y=0):
		self.banderaEditar = bandera
		self.coordenadaX = x
		self.coordenadaY = y
		if self.online.login():
			self.internet = True
			self.llenarLista()
		else:
			#self.__errorConexion()
			pass
		self.adjustSize()
		self.adjustSize()

	def _mostrarVentana(self,estado):
		if estado == 0 or estado == 1:
			if self.internet:
				self.activateWindow()
				self.validar()
				if not self.banderaEditar:
					self.idFeature = self.getIdFeature()
					t1 = threading.Thread(target=self.online.generarId)
					t1.start()
					#self.online.generarId()
					self.sensorCambiado(False)
				else:
					capaActiva = ObtenerCapa().capa()
					objetoGeografico = capaActiva.selectedFeatures()[0]
					self.idFeature = objetoGeografico.attribute('id')
					t1 = threading.Thread(target=self.online.consultarIdFromIdFeature,args=(self.idFeature,))
					t1.start()
					self.busy.show()
				self.loading(True)
				self.show()
		else:
			self.__errorLogin()

	def __generarId(self,id):
		self.id = id

	def sensorCambiado(self,bandera):
		if(self.selectorTipoSensor.currentIndex() == 0):
			self.adaptarCampos(True,False,False,"mca",bandera)
		if(self.selectorTipoSensor.currentIndex() == 1):
			self.adaptarCampos(True,False,True,"lps",bandera,True)
		if(self.selectorTipoSensor.currentIndex() == 2):
			self.adaptarCampos(True,True,True,"%",bandera)

	def adaptarCampos(self,bool1,bool2,bool3,texto,bandera,bool4=True):
		self.editNivelMaximo.setVisible(bool1)
		self.labelMax.setVisible(bool1)
		self.labelDerMax.setVisible(bool1)
		self.labelMin.setVisible(bool1)
		self.labelDerMin.setVisible(bool1)
		self.editNivelMinimo.setVisible(bool1)
		self.labelAltura.setVisible(bool2)
		self.editAltura.setVisible(bool2)
		self.labelDerAlt.setVisible(bool2)
		self.labelArea.setVisible(bool2)
		self.editArea.setVisible(bool2)
		self.labelDerArea.setVisible(bool2)
		self.labelDerMax.setText(texto)
		self.labelDerMin.setText(texto)
		self.activarAlarma.setVisible(bool4)
		#self.labelAlarma2.setVisible(bool4)
		self.labelDerGrafica.setText(texto)
		if bool2:
			self.labelDerGrafica.setText("m³")
		if not bandera:
			if not bool1:
				self.activarAlarma.setChecked(False)
			else:
				self.activarAlarma.setChecked(True)
		self.botonOnline.setVisible(False)
		self.adjustSize()
		self.adjustSize()

	def rellenarCampos(self,sensor):
		self.selectorTipoSensor.setEnabled(False)
		self.botonOnline.setEnabled(False)
		self.editIdDispositivo.setText(sensor.idDispositivo)
		self.editCalle.setText(sensor.calle)
		self.editColonia.setText(sensor.colonia)
		self.editCP.setText(sensor.cp)
		self.selectorMunicipio.setCurrentIndex(sensor.municipio-1)
		self.selectorTipoSensor.setCurrentIndex(sensor.tipoSensor-1)
		self.selectorGrupo.setCurrentIndex(self.__searchGroupByIndex(sensor.grupo))
		self.editNivelMaximo.setText(str(sensor.datoMaximo))
		self.editNivelMinimo.setText(str(sensor.datoMinimo))
		self.editArea.setText(str(sensor.area))
		self.editAltura.setText(str(sensor.altura))
		self.editGrafica.setText(str(sensor.maximo))
		if sensor.alarma == 0:
			self.activarAlarma.setChecked(False)
		elif sensor.alarma >= 1:
			self.activarAlarma.setChecked(True)
		if sensor.online == 0:
			self.botonOnline.setChecked(False)
			self.botonOnline.setText("El sensor no es En línea")
		elif sensor.online == 1:
			self.botonOnline.setChecked(True)
			self.botonOnline.setText("Sensor En línea")

	def __searchGroupByIndex(self,idGrupo):
		i = 0
		for elemento in self.listaGrupos:
			if int(elemento.getIdGrupo()) == int(idGrupo):
				break
			i += 1
		return i

	def checkboxCambiada(self):
		if not self.activarAlarma.isChecked():
			self.activarAlarma.setText("Encender alarma")
			icono = QIcon(":VentanaConfiguracion/icons/alarma_active.png")
			self.activarAlarma.setIcon(icono)
			self.editNivelMaximo.setEnabled(False)
			self.editNivelMinimo.setEnabled(False)
		else:
			self.activarAlarma.setText("Apagar alarma")
			icono = QIcon(":VentanaConfiguracion/icons/alarma.png")
			self.activarAlarma.setIcon(icono)
			self.editNivelMaximo.setEnabled(True)
			self.editNivelMinimo.setEnabled(True)

	def agregarNodo(self,banderaEditar):
		alarma = 0
		GPRS = 0
		if self.activarAlarma.isChecked():
			if int(self.online.getSensor().alarma) == 0:
				alarma = 1
			else:
				alarma = self.online.getSensor().alarma
		if self.botonOnline.isChecked():
			GPRS = 1
		grupo = self.listaGrupos[self.selectorGrupo.currentIndex()]
		sensor = Sensor(self.id,self.editIdDispositivo.text(),self.idFeature,self.editCalle.text(),self.editColonia.text(),self.editCP.text(),self.selectorTipoSensor.currentIndex()+1,self.selectorMunicipio.currentIndex()+1,self.editArea.text(),self.editNivelMaximo.text(),self.editNivelMinimo.text(),alarma,self.editAltura.text(),datoActual=self.online.getSensor().datoActual,grupo=grupo.getIdGrupo(),online=GPRS,maximo=self.editGrafica.text(),x=self.coordenadaX,y=self.coordenadaY,idSubsistema=grupo.getIdSubsistema())
		if not banderaEditar:
			if self.online.insertarSensor(sensor):
				aviso = "El nuevo sensor se almacenó correctamente"
				self.iface.messageBar().pushMessage("Aviso", aviso, level=Qgis.Info,duration=3)
		else:
			if self.online.editarSensor(sensor):
				aviso = "Los datos se actualizaron correctamente"
				self.iface.messageBar().pushMessage("Aviso", aviso, level=Qgis.Info,duration=3)

	def agregarObjetoGeografico(self,x,y,id,capaActiva):
		capacidades = capaActiva.dataProvider().capabilities()
		if capacidades & QgsVectorDataProvider.AddFeatures:
			objetoGeografico = QgsFeature(capaActiva.fields()) #se crea un objeto geográfico que podra recibir los campos correspondientes a la capa activa
			objetoGeografico.setAttributes([id]) #lista con los atributos a agregar
			objetoGeografico.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(x),float(y))))
			capaActiva.dataProvider().addFeatures([objetoGeografico])
			capaActiva.updateFeature(objetoGeografico)
		#capaActiva.setCacheImage( None )
		capaActiva.triggerRepaint()

	def validar(self):
		self.validacion = Validacion(self.sender)
		self.validacion.validarDoble([self.editArea,self.editNivelMaximo,self.editNivelMinimo,self.editAltura,self.editGrafica])
		self.validacion.validarRegExp([self.editIdDispositivo,self.editCalle,self.editColonia,self.editCP],'[\w|\s|\.]+')

	def validarAlEnviar(self):
		self.busy.show()
		banderaEditar = self.banderaEditar
		listaTodos = [self.editIdDispositivo,self.editCalle,self.editColonia,self.editCP,self.editGrafica]
		validez = True
		for elemento in listaTodos:
			if not (elemento.validator().validate(elemento.text(),0)[0] == QValidator.Acceptable):
				elemento.setFocus()
				error = "Rellene todos los campos correctamente."
				self.iface.messageBar().pushMessage("Error", error, level=Qgis.Critical,duration=3)
				validez = False
				break
		if validez:
			self.agregarNodo(banderaEditar)
			if not banderaEditar:
				lienzo = qgis.utils.iface.mapCanvas()
				capaActiva = ObtenerCapa().capa()
				self.agregarObjetoGeografico(self.coordenadaX,self.coordenadaY,self.idFeature,capaActiva)
				self.close()
		alarma = Alarmas()
		alarma.login()
		self.signalCambio.emit()
		self.busy.hide()
		self.adjustSize()

	def getIdFeature(self):
		capaActiva = ObtenerCapa().capa()
		capaActiva.selectAll()
		idFeature = 0
		for feature in capaActiva.getSelectedFeatures():
			if feature[0]+1 > idFeature:
				idFeature = feature[0]+1
		capaActiva.removeSelection()
		#numero = self.conector.generarIdFeature(numero)
		return idFeature

	def hiloSensor(self,idSensor):
		t1 = threading.Thread(target=self.online.consultarSensorPorId,args=(idSensor,))
		t1.start()

	def obtenerSensor(self):
		sensor = self.online.getSensor()
		self.loading(False)
		self.rellenarCampos(sensor)
		self.sensorCambiado(True)
		self.id = sensor.idSensor

	def llenarLista(self):
		self.limpiarVentana()
		t1 = threading.Thread(target=self.online.consultarMunicipios)
		t2 = threading.Thread(target=self.online.consultarTiposSensor)
		t3 = threading.Thread(target=self.online.consultarGrupos)
		t1.start()
		t2.start()
		t3.start()

	def __llenarMunicipios(self):
		if not self.banderaEditar:
			self.loading(False)
		listaMunicipios = self.online.municipios
		for municipio in listaMunicipios:
			self.selectorMunicipio.addItem(municipio.getNombre())
		self.sensorCambiado(True)

	def __llenarTiposSensor(self):
		listaTipoSensor = self.online.tiposSensor
		for tipoSensor in listaTipoSensor:
			self.selectorTipoSensor.addItem(tipoSensor.getNombre())
		self.sensorCambiado(True)

	def __llenarGrupos(self):
		self.listaGrupos = self.online.getGrupos()
		if self.listaGrupos == []:
			self.selectorGrupo.setEnabled(False)
		else:
			for grupo in self.listaGrupos:
				self.selectorGrupo.addItem(grupo.getNombre())
		self.sensorCambiado(True)

	def actualizarMaximo(self):
		if(self.selectorTipoSensor.currentIndex() == 2):
			self.editGrafica.setText(self.editAltura.text())

	def limpiarVentana(self):
		self.editIdDispositivo.setText('')
		self.editCalle.setText('')
		self.editColonia.setText('')
		self.editCP.setText('')
		self.editNivelMaximo.setText('40')
		self.editNivelMinimo.setText('0')
		self.editArea.setText('')
		self.editAltura.setText('')
		self.editGrafica.setText('90')
		self.selectorMunicipio.clear()
		self.selectorGrupo.clear()
		self.selectorTipoSensor.clear()
		self.activarAlarma.setChecked(False)
		self.botonOnline.setChecked(True)

	def loading(self,bandera):
		elementos = self.findChildren(QPushButton)
		elementos.extend(self.findChildren(QLineEdit))
		elementos.extend(self.findChildren(QLabel))
		elementos.extend(self.findChildren(QComboBox))
		for elemento in elementos:
			elemento.setVisible(not bandera)
		self.busy.setVisible(bandera)
		self.adjustSize()

	def cerrar(self):
		self.hide()

	def closeEvent(self, event):
		ObtenerCapa().capa().removeSelection()
		self.signalCerrada.emit()
