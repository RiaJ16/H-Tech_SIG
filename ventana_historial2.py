# -*- coding: UTF8 -*-

import datetime
import os
import qgis.utils
import sys
import threading

from qgis.core import *
from qgis.gui import *

from PyQt5 import QtGui, uic, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QTextCodec, QTime, QRectF
from PyQt5.QtGui import QDoubleValidator, QCursor, QPixmap, QIcon, QPen, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QPushButton, QGraphicsScene

#from .boton_mas import BotonMas
from .busy_icon import BusyIcon
#from .calendario import Calendario
#from .graficas import Graficas
from .obtener_capa import ObtenerCapa
from .sensor import Sensor

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'ventana_historial.ui'))

class VentanaHistorial(QtWidgets.QDialog, FORM_CLASS):

	def __init__(self,online,parent=None):
		"""Constructor."""
		super(VentanaHistorial, self).__init__(parent)
		self.setupUi(self)
		self.online = online
		self.iface = qgis.utils.iface
		self.scrollArea.setVisible(False)
		self.busy = BusyIcon(self.layout())
		self.busy.startAnimation()
		self.mostrarOcultarEstado(desconocido=True)
		self.signals()
		self.inicializar()

	def inicializar(self):
		self.habilitarBotones(False)
		self.botonGraficar.clicked.connect(self.graficar)
		self.botonReportes.clicked.connect(self.reportes)
		self.botonExpandir.clicked.connect(self.expandir)
		self.tablaValores.itemSelectionChanged.connect(self.seleccionCambiada)
		self.capaActiva = ObtenerCapa.capa()
		self.seleccionarPeriodo.currentIndexChanged.connect(self.comportamientoFiltrar)
		self.month.currentIndexChanged.connect(self.cambiarMes)
		self.year.valueChanged.connect(self.cambiarYear)
		self.semaforo = True
		self.multiplicador = 0

	def signals(self):
		pass
		#self.online.signalSensorConsultado.connect(self.consultarDatosSensor)

	def objetoGeograficoSeleccionado(self,objetoGeografico):
		self.objetoGeografico = objetoGeografico

	def actualizarVentana(self,fechaInicial='',fechaFinal='',horaInicial='',horaFinal=''):
		self.reiniciarTabla()
		fechaHoraInicial = "%s%s" % (fechaInicial,horaInicial)
		fechaHoraFinal = "%s%s" % (fechaFinal,horaFinal)
		t1 = threading.Thread(target=self.consultarHistorial,args=(fechaHoraInicial,fechaHoraFinal))
		t1.start()
		#self.consultarHistorial(fechaHoraInicial,fechaHoraFinal)
		#print fechaHoraInicial
		#print fechaHoraFinal
		#self.cambiarEstado()
		self.actualizarFoto()
		self.adjustSize()
		self.show()
		#self.adjustSize()

	def mostrarVentana(self):
		self.online.signalSensorConsultado.connect(self.consultarDatosSensor)
		#self.online.signalConsultarId.connect(self.consultarDatosSensor)
		idFeature = self.objetoGeografico.attribute('id')
		self.id = self.online.consultarIdFromIdFeature(idFeature)
		t1 = threading.Thread(target=self.online.consultarSensorPorId,args=(self.id,))
		t1.start()

	def consultarDatosSensor(self):
		self.online.signalSensorConsultado.disconnect(self.consultarDatosSensor)
		self.tipoSensor = self.online.getSensor().tipoSensor
		self.online.consultarSensorPorIdNombres(self.id)
		sensor = self.online.getSensor()
		isEmpty = self.online.isEmpty(self.id)
		if not isEmpty:
			try:
				titulo = "Sensor de %s" % sensor.tipoSensor.lower()
				valor = ''
				datos = "Sensor ubicado en la calle {}, colonia {}, {}, {}".format(sensor.calle,sensor.colonia,sensor.municipio,sensor.cp)
				self.habilitarBotones(True)
				if self.tipoSensor == 3:
					self.graficoBarra.setVisible(True)
					self.actualizarGrafica()
				else:
					self.graficoBarra.setVisible(False)
				#self.cursor = self.conector.consultarHistorial(self.id)
			except:
				titulo = "Objeto no asociado"
				datos = "Este objeto no ha sido asociado con ningún sensor"
				valor = "<font color='red'>No hay datos registrados</font>"
				self.habilitarBotones(False)
		else:
			titulo = "No hay datos registrados"
			datos = "Este sensor aún no ha recibido datos"
			valor = "<font color='red'>No hay datos registrados</font>"
			self.habilitarBotones(False)
		self.busy.hide()
		self.cargarDatosSensor(titulo,datos,valor)
		self.activateWindow()
		self.cambiarEstado()
		self.actualizarFoto()
		self.adjustSize()
		self.adjustSize()
		self.show()

	def consultarHistorial(self,fechaInicial,fechaFinal):
		idFeature = self.objetoGeografico.attribute('id')
		self.id = self.online.consultarIdFromIdFeature(idFeature)
		#consulta = self.conector.consultarHistorialN(self.id,fechaInicial,fechaFinal,3000,self.multiplicador)
		listaRegistros = self.online.consultarHistoricos(self.id,fechaInicial,fechaFinal)
		#listaRegistros = consulta[1]
		for registro in listaRegistros:
			self.tablaValores.insertRow(self.tablaValores.rowCount())
			fecha = "{}-{}-{}".format(registro.fecha[8:10],registro.fecha[5:7],registro.fecha[0:4])
			item = QTableWidgetItem(fecha)
			self.tablaValores.setItem(self.tablaValores.rowCount()-1,0,item)
			hora = registro.fecha[11:19]
			item = QTableWidgetItem(hora)
			self.tablaValores.setItem(self.tablaValores.rowCount()-1,1,item)
			dato = float("{0:.2f}".format(float(registro.dato)))
			item = QTableWidgetItem(str(dato))
			self.tablaValores.setItem(self.tablaValores.rowCount()-1,2,item)
		'''if consulta[0]:
			self.cargarBotonMas(fechaInicial,fechaFinal)'''
		if listaRegistros == []:
			return False
		else:
			return True

	def cargarDatosSensor(self,titulo,datos,valor):
		self.setWindowTitle(titulo)
		self.labelDatos.setText(datos)
		self.labelValor.setText(valor)

	def reiniciarTabla(self):
		while not self.tablaValores.rowCount() == 0:
			self.tablaValores.removeRow(self.tablaValores.rowCount()-1)

	def habilitarBotones(self,bandera):
		botones = [self.botonGraficar,self.seleccionarPeriodo,self.year,self.month,self.fechaInicial,self.fechaFinal,self.horaInicial,self.horaFinal]
		for boton in botones:
			boton.setEnabled(bandera)
		#self.comportamientoFiltrar()

	def comportamientoFiltrar(self):
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
		now = datetime.datetime.now()
		haceUnaHora = QTime(now.hour-1,now.minute,now.second)
		horaActual= QTime(now.hour,now.minute,now.second)
		primerDiaDelMes = now.replace(day=1)
		if self.seleccionarPeriodo.currentIndex() == 0:
			self.mostrarBotonesFiltrar()
			self.definirFecha(datetime.date.today(),datetime.date.today(),haceUnaHora,horaActual)
			self.filtrar()
		if self.seleccionarPeriodo.currentIndex() == 1:
			self.mostrarBotonesFiltrar()
			self.definirFecha(datetime.date.today(), datetime.date.today() + datetime.timedelta(days=1))
			self.filtrar()
		if self.seleccionarPeriodo.currentIndex() == 2:
			self.mostrarBotonesFiltrar()
			self.definirFecha(datetime.date.today() - datetime.timedelta(days=1),datetime.date.today())
			self.filtrar()
		if self.seleccionarPeriodo.currentIndex() == 3:
			self.mostrarBotonesFiltrar()
			self.month.currentIndexChanged.disconnect()
			self.month.setCurrentIndex(datetime.date.today().month-1)
			self.month.currentIndexChanged.connect(self.cambiarMes)
			self.year.valueChanged.disconnect()
			self.year.setValue(datetime.date.today().year)
			self.year.valueChanged.connect(self.cambiarYear)
			self.cambiarMes()
		if self.seleccionarPeriodo.currentIndex() == 4:
			self.mostrarBotonesFiltrar(True,True)
			self.cambiarMes()
		if self.seleccionarPeriodo.currentIndex() == 5:
			self.mostrarBotonesFiltrar(False,True)
			self.cambiarYear()
		if self.seleccionarPeriodo.currentIndex() == 6:
			self.mostrarBotonesFiltrar(False,False,True)
			self.fechaInicial.dateChanged.connect(self.filtrar)
			self.fechaFinal.dateChanged.connect(self.filtrar)
			self.horaInicial.timeChanged.connect(self.cambioDeHora)
			self.horaFinal.timeChanged.connect(self.cambioDeHora)
		#try:
		#	self.filtrar()
		#except:
		#	pass

	def cambiarMes(self):
		primerDiaDelMes = datetime.date(self.year.value(),self.month.currentIndex()+1,1)
		if primerDiaDelMes.month == 12:
			primerDiaDelSiguienteMes = datetime.date(primerDiaDelMes.year+1,1,1)
		else:
			primerDiaDelSiguienteMes = primerDiaDelMes.replace(month=primerDiaDelMes.month+1)
		self.definirFecha(primerDiaDelMes,primerDiaDelSiguienteMes)
		self.filtrar()

	def cambiarYear(self):
		if self.seleccionarPeriodo.currentIndex() == 5:
			primerDiaDelYear = datetime.date(self.year.value(),1,1)
			primerDiaDelSiguienteYear = datetime.date(self.year.value()+1,1,1)
			self.definirFecha(primerDiaDelYear,primerDiaDelSiguienteYear)
			self.filtrar()
		else:
			self.cambiarMes()

	def mostrarBotonesFiltrar(self,flag0=False,flag1=False,flag2=False):
		self.month.setVisible(flag0)
		self.year.setVisible(flag1)
		lista = [self.fechaInicial,self.fechaFinal,self.horaInicial,self.horaFinal,self.labelFechaInicial,self.labelFechaFinal,self.labelHoraInicial,self.labelHoraFinal]
		for campo in lista:
			campo.setVisible(flag2)

	def definirFecha(self,fechaInicial,fechaFinal,horaInicial=QTime(0,0,0),horaFinal=QTime(0,0,0)):
		self.horaInicial.setTime(horaInicial)
		self.horaFinal.setTime(horaFinal)
		self.fechaInicial.setDate(fechaInicial)
		self.fechaFinal.setDate(fechaFinal)

	def cambioDeHora(self):
		if self.semaforo:
			self.semaforo = False
			self.filtrar()
			self.semaforo = True

	def filtrar(self,bandera=False):
		self.multiplicador = 0
		fechaInicial = "%04d%02d%02d" % (self.fechaInicial.date().year(), self.fechaInicial.date().month(), self.fechaInicial.date().day())
		fechaFinal = "%04d%02d%02d" % (self.fechaFinal.date().year(), self.fechaFinal.date().month(), self.fechaFinal.date().day())
		horaInicial = "%02d%02d%02d" % (self.horaInicial.time().hour(),self.horaInicial.time().minute(),self.horaInicial.time().second())
		horaFinal = "%02d%02d%02d" % (self.horaFinal.time().hour(),self.horaFinal.time().minute(),self.horaFinal.time().second())
		self.actualizarVentana(fechaInicial,fechaFinal,horaInicial,horaFinal)

	def graficar(self):
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
		indice = self.seleccionarPeriodo.currentIndex()
		periodo = 3
		if indice == 0:
			periodo = 0
		elif indice == 1 or indice == 2:
			periodo = 1
		elif indice == 3 or indice == 4:
			periodo = 2
		maximo = self.conector.consultarSensorObjeto(self.id).maximo
		self.graficas = Graficas(self.tipoSensor)
		self.graficas.graficar(dateandtimes,values,self.getDateTimes(),periodo,maximo)

	def getDateTimes(self):
		date = datetime.date(self.fechaInicial.date().year(),self.fechaInicial.date().month(),self.fechaInicial.date().day())
		time = datetime.time(self.horaInicial.time().hour(),self.horaInicial.time().minute(),self.horaInicial.time().second())
		dtInicial = datetime.datetime.combine(date,time)
		date = datetime.date(self.fechaFinal.date().year(),self.fechaFinal.date().month(),self.fechaFinal.date().day())
		time = datetime.time(self.horaFinal.time().hour(),self.horaFinal.time().minute(),self.horaFinal.time().second())
		dtFinal = datetime.datetime.combine(date,time)
		return [dtInicial,dtFinal]

	def reportes(self):
		reportes = Calendario(self.conector,self.id,self.tipoSensor)
		self.close()

	def seleccionCambiada(self):
		if self.tipoSensor == 1:
			try:
				self.labelValor.setText("{} mca".format(self.tablaValores.item(self.tablaValores.currentRow(),2).text()))
			except:
				pass
		elif self.tipoSensor == 2:
			try:
				self.labelValor.setText("{} lps".format(self.tablaValores.item(self.tablaValores.currentRow(),2).text()))
			except:
				pass
		elif self.tipoSensor == 3:
			try:
				self.labelValor.setText("{} m²".format(self.tablaValores.item(self.tablaValores.currentRow(),2).text()))
			except:
				pass
		self.tablaValores.selectRow(self.tablaValores.currentRow())

	def cambiarEstado(self):
		self.online.consultarSensorPorId(self.id)
		estado = int(self.online.getSensor().estado)
		if estado == 0:
			self.mostrarOcultarEstado(desconocido=True)
		if estado == 1:
			self.mostrarOcultarEstado(sinConexion=True)
		if estado == 2:
			self.mostrarOcultarEstado(intermitente=True)
		if estado == 3:
			self.mostrarOcultarEstado(True)

	def mostrarOcultarEstado(self,conectado=False,intermitente=False,sinConexion=False,desconocido=False):
		self.labelConectado.setVisible(conectado)
		self.labelIntermitente.setVisible(intermitente)
		self.labelSinConexion.setVisible(sinConexion)
		self.labelDesconocido.setVisible(desconocido)

	def expandir(self):
		self.scrollArea.setVisible(not self.scrollArea.isVisible())
		if self.scrollArea.isVisible():
			self.botonExpandir.setIcon(QIcon(":/Varios/icons/collapse.png"))
		else:
			self.botonExpandir.setIcon(QIcon(":/Varios/icons/expand.png"))
		self.adjustSize()

	def actualizarFoto(self):
		try:
			filename = self.conector.consultarFotoPozo(self.conector.consultarIdPozo(self.id))
		except:
			filename = ""
		if filename == "" or filename == None:
			filename = "%s\\.sigrdap\\nodisponible.png" % os.environ['HOME']
		foto = QPixmap(filename)
		self.labelFoto.setPixmap(foto)

	def cerrar(self):
		self.close()

	def cargarBotonMas(self,fechaInicial,fechaFinal):
		self.botonMas = BotonMas(fechaInicial,fechaFinal)
		self.botonMas.setText('Cargar más datos')
		self.botonMas.aumentarMultiplicador()
		self.multiplicador += 1
		self.tablaValores.insertRow(self.tablaValores.rowCount())
		self.tablaValores.setCellWidget(self.tablaValores.rowCount()-1,0,self.botonMas)
		self.botonMas.clicked.connect(self.cargarMasDatos)

	def cargarMasDatos(self):
		self.tablaValores.removeRow(self.tablaValores.rowCount()-1)
		self.consultarHistorial(self.botonMas.fechaInicial(),self.botonMas.fechaFinal())

	def actualizarGrafica(self):
		sensor = self.conector.consultarSensorN(self.id)
		self.graficoBarra.setAlignment(Qt.AlignBottom|Qt.AlignLeft)
		scene = QGraphicsScene()
		altura = self.graficoBarra.size().height()
		porcentaje = sensor.datoActual * altura / sensor.altura
		if porcentaje > altura:
			porcentaje = altura
		grafica = QRectF(0, 0, self.graficoBarra.size().width()-2, int(porcentaje)-2)
		scene.addRect(grafica, QPen(QColor("#3498db")), QBrush(QColor("#3498db")));
		self.graficoBarra.setScene(scene)

	def nuevoDato(self,dato):
		if self.tipoSensor == 3:
			self.actualizarGrafica()