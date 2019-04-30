# -*- coding: UTF8 -*-

import datetime
import os
import qgis.utils
import sys
import threading
import time

from qgis.core import *
from qgis.gui import *

from PyQt5 import QtGui, uic, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QTextCodec, QTime, QRectF
from PyQt5.QtGui import QBrush, QColor, QCursor, QDoubleValidator, QFont, QIcon, QPen, QPixmap
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QHeaderView, QPushButton, QTableWidgetItem

from .busy_icon import BusyIcon
from .calendario import Calendario
from .graficas import Graficas
from .obtener_capa import ObtenerCapa
from .sensor import Sensor

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'ventana_historial.ui'))

class VentanaHistorial(QtWidgets.QDialog, FORM_CLASS):

	semaforoDatosSensor = True
	semaforoHistoricos = 0

	def __init__(self,online,parent=None):
		"""Constructor."""
		super(VentanaHistorial, self).__init__(parent)
		self.setupUi(self)
		self.online = online
		self.iface = qgis.utils.iface
		self.semaforo = True
		self.__visualizacionInicial()
		self.capaActiva = ObtenerCapa.capa()
		self.__signals()
		self.__estilizarTabla()
		
	#INICIALIZACIÓN	
		
	def __visualizacionInicial(self):
		#self.__habilitarBotones(False)
		self.graficoBarra.setVisible(False)
		self.__mostrarOcultarEstado(desconocido=True)
		self.busy = BusyIcon(self.layout())
		self.busy.startAnimation()
		self.day.setDate(datetime.date.today())
		self.month.setCurrentIndex(datetime.date.today().month-1)
		self.year.setValue(datetime.date.today().year)
		#self.actualizarFoto()

	def __habilitarBotones(self,bandera):
		botones = [self.botonGraficar,self.botonReportes,self.seleccionarPeriodo,self.year,self.month,self.fechaInicial,self.fechaFinal,self.horaInicial,self.horaFinal,self.day]
		for boton in botones:
			boton.setEnabled(bandera)

	def __mostrarOcultarEstado(self,conectado=False,intermitente=False,sinConexion=False,desconocido=False):
		self.labelConectado.setVisible(conectado)
		self.labelIntermitente.setVisible(intermitente)
		self.labelSinConexion.setVisible(sinConexion)
		self.labelDesconocido.setVisible(desconocido)

	def __signals(self):
		self.botonGraficar.clicked.connect(self.graficar)
		self.botonReportes.clicked.connect(self.reportes)
		#self.tablaValores.itemSelectionChanged.connect(self.seleccionCambiada)
		self.seleccionarPeriodo.currentIndexChanged.connect(self.__cambiarContexto)
		self.month.currentIndexChanged.connect(self.cambiarMes)
		self.year.valueChanged.connect(self.cambiarYear)
		self.day.dateChanged.connect(self.cambiarDia)
		self.online.signalSensorConsultado.connect(self.cargarDatosSensor)
		self.online.signalConsultarGrupo.connect(self.actualizarFoto)
		self.online.signalHistoricos.connect(self.cargarRegistros)
		self.online.signalErrorConexion.connect(self.__errorConexion)

	def objetoGeograficoSeleccionado(self,objetoGeografico):
		self.objetoGeografico = objetoGeografico

	def __errorConexion(self):
		self.setWindowTitle("Error de conexión")
		self.labelGrupo.setText("Error de conexión")
		self.__habilitarBotones(False)
		self.busy.hide()
		error = "Conéctese a internet para hacer uso de esta aplicación"
		self.iface.messageBar().pushMessage("Error de conexión", error, level=Qgis.Critical,duration=3)
		self.adjustSize()

	#FUNCIONAMIENTO

	def mostrarVentana(self):
		self.semaforoDatosSensor = True
		self.__cambiarContexto()
		self.obtenerDatosSensor()
		self.adjustSize()
		self.show()
		self.activateWindow()
		self.capaActiva.removeSelection()

	#<Métodos para alterar la interfaz de la ventana de acuerdo a las opciones de filtrado

	def __cambiarContexto(self): #Altera la ventana de acuerdo al periodo de filtrado seleccionado
		self.__desconectarSignalsContexto
		now = datetime.datetime.now()
		haceUnaHora = QTime(now.hour-1,now.minute,now.second)
		horaActual = QTime(now.hour,now.minute,now.second)
		primerDiaDelMes = now.replace(day=1)
		#hoy = datetime.date.today()
		if self.seleccionarPeriodo.currentIndex() == 0:
			self.__adaptarBotones()
			self.definirFecha(datetime.date.today(),datetime.date.today(),haceUnaHora,horaActual)
			self.filtrar()
		if self.seleccionarPeriodo.currentIndex() == 1:
			self.__adaptarBotones(False,False,False,True)
			self.cambiarDia()
			#self.day.setDate(hoy)
			#self.definirFecha(hoy,hoy+datetime.timedelta(days=1))
		if self.seleccionarPeriodo.currentIndex() == 2:
			self.__adaptarBotones(True,True)
			#self.month.setCurrentIndex(datetime.date.today().month-1)
			self.month.currentIndexChanged.connect(self.cambiarMes)
			self.year.valueChanged.connect(self.cambiarYear)
			#self.year.setValue(datetime.date.today().year)
			self.cambiarMes()
		'''if self.seleccionarPeriodo.currentIndex() == 3:
			self.__adaptarBotones(False,True)
			self.year.valueChanged.connect(self.cambiarYear)
			self.year.setValue(datetime.date.today().year)
			self.cambiarYear()'''
		if self.seleccionarPeriodo.currentIndex() == 3:
			self.__adaptarBotones(False,False,True)
			self.fechaInicial.dateChanged.connect(self.filtrar)
			self.fechaFinal.dateChanged.connect(self.filtrar)
			self.horaInicial.timeChanged.connect(self.cambioDeHora)
			self.horaFinal.timeChanged.connect(self.cambioDeHora)
			self.filtrar()
		self.adjustSize()
		self.adjustSize()

	def __desconectarSignalsContexto(self):
		try:
			self.fechaInicial.dateChanged.disconnect(self.filtrar)
		except:
			pass
		try:
			self.fechaFinal.dateChanged.disconnect(self.filtrar)
		except:
			pass
		try:
			self.horaInicial.timeChanged.disconnect(self.cambioDeHora)
		except:
			pass
		try:
			self.horaFinal.timeChanged.disconnect(self.cambioDeHora)
		except:
			pass
		try:
			self.month.currentIndexChanged.disconnect()
		except:
			pass
		try:
			self.year.valueChanged.disconnect()
		except:
			pass

	def __adaptarBotones(self,flag0=False,flag1=False,flag2=False,flag3=False): #Muestra u oculta los elementos de la interfaz para filtrar
		self.month.setVisible(flag0)
		self.year.setVisible(flag1)
		lista = [self.fechaInicial,self.fechaFinal,self.horaInicial,self.horaFinal,self.labelFechaInicial,self.labelFechaFinal,self.labelHoraInicial,self.labelHoraFinal]
		for campo in lista:
			campo.setVisible(flag2)
		self.day.setVisible(flag3)

	def definirFecha(self,fechaInicial,fechaFinal,horaInicial=QTime(0,0,0),horaFinal=QTime(0,0,0)):
		self.horaInicial.setTime(horaInicial)
		self.horaFinal.setTime(horaFinal)
		self.fechaInicial.setDate(fechaInicial)
		self.fechaFinal.setDate(fechaFinal)

	def cambiarDia(self):
		date = datetime.date(self.day.date().year(),self.day.date().month(),self.day.date().day())
		time = datetime.time(self.day.time().hour(),self.day.time().minute(),self.day.time().second())
		dia = datetime.datetime.combine(date,time)
		self.definirFecha(dia,dia+datetime.timedelta(days=1))
		self.filtrar()

	def cambiarMes(self):
		primerDiaDelMes = datetime.date(self.year.value(),self.month.currentIndex()+1,1)
		if primerDiaDelMes.month == 12:
			primerDiaDelSiguienteMes = datetime.date(primerDiaDelMes.year+1,1,1)
		else:
			primerDiaDelSiguienteMes = primerDiaDelMes.replace(month=primerDiaDelMes.month+1)
		self.definirFecha(primerDiaDelMes,primerDiaDelSiguienteMes)
		self.filtrar()

	def cambiarYear(self):
		if self.seleccionarPeriodo.currentIndex() == 3:
			primerDiaDelYear = datetime.date(self.year.value(),1,1)
			primerDiaDelSiguienteYear = datetime.date(self.year.value()+1,1,1)
			self.definirFecha(primerDiaDelYear,primerDiaDelSiguienteYear)
			self.filtrar()
		else:
			self.cambiarMes()

	def cambioDeHora(self):
		if self.semaforo:
			self.semaforo = False
			self.filtrar()
			self.semaforo = True

	#!contexto fin>

	def obtenerDatosSensor(self):
		idFeature = self.objetoGeografico.attribute('id')
		t1 = threading.Thread(target=self.online.consultarSensorPorIdFeature,args=(idFeature,))
		self.busy.show()
		t1.start()

	def cargarDatosSensor(self):
		sensor = self.online.sensor
		self.semaforoDatosSensor = False
		if sensor.idSensor == 0:
			self.setWindowTitle("Error")
			self.labelGrupo.setText("Error")
			self.__habilitarBotones(False)
			self.busy.hide()
			error = "Inicie sesión antes de ver la información"
			self.iface.messageBar().pushMessage("Error", error, level=Qgis.Critical,duration=3)
			self.adjustSize()
		else:
			self.__habilitarBotones(True)
			self.labelDireccion.setText("<b><font color='#2980b9'>Ubicación:</font></b> %s, %s, %s" % (sensor.calle,sensor.colonia,sensor.municipioTexto))
			self.labelTipo.setText("<b><font color='#2980b9'>Tipo:</font></b> %s" % sensor.tipoSensorTexto)
			self.labelGrupo.setText("<b>%s</b>" % sensor.grupoTexto.upper())
			self.labelValor.setText("%2.2f %s" % (sensor.datoActual,self.__unidades(sensor.tipoSensor)))
			self.setWindowTitle("%s: sensor de %s" % (sensor.grupoTexto,sensor.tipoSensorTexto.lower()))
			if sensor.tipoSensor == 3:
				self.graficoBarra.setVisible(True)
			else:
				self.graficoBarra.setVisible(False)
				self.adjustSize()
			self.cambiarEstado(sensor.estado)
			self.adjustSize()
			#self.busy.hide()
			self.adjustSize()
			t1 = threading.Thread(target=self.online.consultarGrupoPorId,args=(sensor.grupo,))
			t1.start()

	def cambiarEstado(self,estado):
		if estado == 0:
			self.__mostrarOcultarEstado(desconocido=True)
		if estado == 1:
			self.__mostrarOcultarEstado(sinConexion=True)
		if estado == 2:
			self.__mostrarOcultarEstado(intermitente=True)
		if estado == 3:
			self.__mostrarOcultarEstado(True)

	def __unidades(self,tipoSensor):
		if tipoSensor == 1:
			return "mca"
		elif tipoSensor == 2:
			return "lps"
		elif tipoSensor == 3:
			return "m²"
		else:
			return ''

	def actualizarFoto(self):
		try:
			filename = self.online.grupo.foto
		except:
			filename = ""
		if filename == "" or filename == None:
			filename = "%s\\.sigrdap\\Fotos\\nodisponible.png" % os.environ['HOME']
		foto = QPixmap(filename)
		newHeight = 80
		try:
			newWidth = foto.width()*newHeight/foto.height()
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

	#<Métodos para el filtrado
	
	def filtrar(self):
		self.busy.show()
		t1 = threading.Thread(target=self.hiloFiltrar)
		t1.start()

	def hiloFiltrar(self,bandera=False):
		fechaInicial = "%04d%02d%02d" % (self.fechaInicial.date().year(), self.fechaInicial.date().month(), self.fechaInicial.date().day())
		fechaFinal = "%04d%02d%02d" % (self.fechaFinal.date().year(), self.fechaFinal.date().month(), self.fechaFinal.date().day())
		horaInicial = "%02d%02d%02d" % (self.horaInicial.time().hour(),self.horaInicial.time().minute(),self.horaInicial.time().second())
		horaFinal = "%02d%02d%02d" % (self.horaFinal.time().hour(),self.horaFinal.time().minute(),self.horaFinal.time().second())
		fechaHoraInicial = "%s%s" % (fechaInicial,horaInicial)
		fechaHoraFinal = "%s%s" % (fechaFinal,horaFinal)
		#t1 = threading.Thread(target=self.online.consultarHistoricos,args=(1,fechaHoraInicial,fechaHoraFinal))
		#t1.start()
		self.semaforoHistoricos = int((int(fechaHoraInicial) + int(fechaHoraFinal))/1000000)
		while self.semaforoDatosSensor:
			time.sleep(0.1)
		self.online.consultarHistoricos(self.online.sensor.idSensor,fechaHoraInicial,fechaHoraFinal)

	def cargarRegistros(self,token):
		if token == self.semaforoHistoricos:
			self.__reiniciarTabla()
			historicos = self.online.historicos
			fuenteHora = QFont("Verdana",8,QFont.DemiBold)
			fuenteDato = QFont("Verdana",18)
			fuenteUnidades = QFont("Verdana",8)
			fuenteFecha = QFont("Verdana",6)
			for registro in historicos:
				self.tablaValores.insertRow(self.tablaValores.rowCount())
				#FECHA
				fecha = "{}-{}-{}".format(registro.fecha[8:10],registro.fecha[5:7],registro.fecha[0:4])
				item = QTableWidgetItem(fecha)
				item.setFont(fuenteFecha)
				item.setTextAlignment(Qt.AlignRight|Qt.AlignBottom)
				self.tablaValores.setItem(self.tablaValores.rowCount()-1,3,item)
				#HORA
				hora = "%shrs" % registro.fecha[11:16]
				item = QTableWidgetItem(hora)
				item.setFont(fuenteHora)
				item.setTextAlignment(Qt.AlignLeft|Qt.AlignBottom)
				self.tablaValores.setItem(self.tablaValores.rowCount()-1,0,item)
				#VALOR
				dato = float("{0:.2f}".format(float(registro.dato)))
				item = QTableWidgetItem(str("%.2f" % dato))
				item.setFont(fuenteDato)
				item.setTextAlignment(Qt.AlignRight)
				self.tablaValores.setItem(self.tablaValores.rowCount()-1,1,item)
				#UNIDADES
				item = QTableWidgetItem("mca")
				item.setFont(fuenteUnidades)
				item.setTextAlignment(Qt.AlignLeft|Qt.AlignVCenter)
				item.setForeground(QBrush(QColor("gray")))
				self.tablaValores.setItem(self.tablaValores.rowCount()-1,2,item)
			self.busy.hide()
			self.adjustSize()

	def __reiniciarTabla(self):
		while not self.tablaValores.rowCount() == 0:
			self.tablaValores.removeRow(self.tablaValores.rowCount()-1)

	def __estilizarTabla(self):
		self.tablaValores.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);
		self.tablaValores.setFocusPolicy(Qt.NoFocus)

	#!filtrar fin>
	
	#<Métodos para graficar

	def graficar(self):
		sensor = self.online.sensor
		i = 0
		dateandtimes = []
		values = []
		while i<self.tablaValores.rowCount():
			fecha = self.tablaValores.item(i,0).text()
			date = datetime.date(int(fecha[6:10]),int(fecha[3:5]),int(fecha[0:2]))
			hora = self.tablaValores.item(i,1).text()
			time = datetime.time(int(hora[0:2]),int(hora[3:5]),0)
			dateandtime = datetime.datetime.combine(date,time)
			dateandtimes.append(dateandtime)
			values.append(float(self.tablaValores.item(i,2).text()))
			i=i+1
		periodo = self.seleccionarPeriodo.currentIndex()
		self.graficas = Graficas(sensor.tipoSensor)
		self.graficas.graficar(dateandtimes,values,self.getDateTimes(),periodo,sensor.maximo)

	def getDateTimes(self):
		date = datetime.date(self.fechaInicial.date().year(),self.fechaInicial.date().month(),self.fechaInicial.date().day())
		time = datetime.time(self.horaInicial.time().hour(),self.horaInicial.time().minute(),self.horaInicial.time().second())
		dtInicial = datetime.datetime.combine(date,time)
		date = datetime.date(self.fechaFinal.date().year(),self.fechaFinal.date().month(),self.fechaFinal.date().day())
		time = datetime.time(self.horaFinal.time().hour(),self.horaFinal.time().minute(),self.horaFinal.time().second())
		dtFinal = datetime.datetime.combine(date,time)
		return [dtInicial,dtFinal]
	
	#!graficar fin>

	#<Métodos para mostrar reportes

	def reportes(self):
		sensor = self.online.sensor
		reportes = Calendario(self.online,sensor)
		self.close()

	#!reportes fin>

	def cerrar(self):
		self.hide()