# -*- coding: UTF8 -*-

import ctypes
import datetime
import locale
import os
import qgis.utils
import sys
import threading
import time

from qgis.core import *
from qgis.gui import *

from PyQt5 import QtGui, uic, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QTextCodec, QTime, QRectF, QPoint, QSize
from PyQt5.QtGui import QBrush, QColor, QCursor, QDoubleValidator, QFont, QIcon, QPen, QPixmap
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QHBoxLayout, QHeaderView, QLabel, QLayout, QPushButton, QTableWidgetItem, QToolTip, QWidget

from .busy_icon import BusyIcon
from .calendario import Calendario
from .descargador_fotos import DescargadorFotos
from .graficas import Graficas
from .fecha_widget_item import FechaWidgetItem
from .flotante import Flotante
from .obtener_capa import ObtenerCapa
from .opciones_sensor import OpcionesSensor
from .q_dialog_next import QDialogNext
from .sensor import Sensor

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'ventana_historial.ui'))

class VentanaHistorial(QDialogNext, FORM_CLASS):

	semaforoDatosSensor = True
	semaforoHistoricos = 0

	def __init__(self,online,parent=None):
		"""Constructor."""
		super(VentanaHistorial, self).__init__(parent)
		self.setupUi(self)
		self.online = online
		self.iface = qgis.utils.iface
		self.setMovable(self.kraken)
		self.setBotonCerrar(self.botonCerrar)
		self.semaforo = True
		self.loadedRows = 0
		self.fotoFlotante = Flotante()#parent = self.iface.mainWindow())
		self.__visualizacionInicial()
		self.comprobarPermisos()
		self.__signals()
		self.__estilizarTabla()

	#INICIALIZACIÓN	

	def __visualizacionInicial(self):
		#self.__habilitarBotones(False)
		self.graficoBarra.setVisible(False)
		self.botonConfiguracion.setVisible(False)
		self.__mostrarOcultarEstado(desconocido=True)
		self.busy = BusyIcon(self.layout())
		self.busy.startAnimation()
		self.day.setDate(datetime.date.today())
		self.month.setCurrentIndex(datetime.date.today().month-1)
		self.year.setValue(datetime.date.today().year)
		#self.actualizarFoto()

	def __habilitarBotones(self,bandera):
		botones = [self.botonGraficar,self.botonReportes,self.seleccionarPeriodo,self.year,self.month,self.fechaInicial,self.fechaFinal,self.horaInicial,self.horaFinal,self.day,self.botonConfiguracion]
		for boton in botones:
			boton.setEnabled(bandera)
		if not bandera:
			self.labelValor.setText("...")
			self.__reiniciarTabla()
			simbolos = [self.iconOff, self.iconOn, self.labelDesconocido, self.labelSinConexion, self.labelIntermitente, self.labelConectado]
			for simbolo in simbolos:
				simbolo.setVisible(bandera)

	def __mostrarOcultarEstado(self,conectado=False,intermitente=False,sinConexion=False,desconocido=False):
		self.labelConectado.setVisible(conectado)
		self.labelIntermitente.setVisible(intermitente)
		self.labelSinConexion.setVisible(sinConexion)
		self.labelDesconocido.setVisible(desconocido)

	def comprobarPermisos(self):
		self.online.signalPermisos.connect(self.comprobarOpcionesSensor)
		t1 = threading.Thread(target=self.online.consultarPermisos)
		t1.start()

	def comprobarOpcionesSensor(self,permisos):
		if permisos < 2:
			self.botonConfiguracion.setVisible(True)

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
		self.online.signalFotoDescargada.connect(self.fotoDescargada)
		self.botonConfiguracion.pressed.connect(self.iconoPresionado)
		self.botonConfiguracion.released.connect(self.iconoSoltado)
		self.botonConfiguracion.clicked.connect(self.configuracion)
		self.tablaValores.verticalScrollBar().valueChanged.connect(self.scrolleado)
		self.botonFoto.clicked.connect(self.fotoFlotante.show)

	def disconnectSignals(self):
		self.online.signalSensorConsultado.disconnect(self.cargarDatosSensor)
		self.online.signalConsultarGrupo.disconnect(self.actualizarFoto)
		self.online.signalHistoricos.disconnect(self.cargarRegistros)
		self.online.signalErrorConexion.disconnect(self.__errorConexion)
		self.online.signalFotoDescargada.disconnect(self.fotoDescargada)

	def objetoGeograficoSeleccionado(self,objetoGeografico):
		self.objetoGeografico = objetoGeografico

	def __errorConexion(self):
		self.setWindowTitle("Error de conexión")
		self.labelGrupo.setText("Error de conexión")
		self.labelTipo.setText("")
		self.labelDireccion.setText("")
		self.__habilitarBotones(False)
		self.busy.hide()
		error = "Conéctese a internet para hacer uso de esta aplicación"
		#self.iface.messageBar().pushMessage("Error de conexión", error, level=Qgis.Critical,duration=3)
		self.adjustSize()

	#FUNCIONAMIENTO

	def mostrarVentana(self):
		self.semaforoDatosSensor = True
		self.__cambiarContexto()
		self.obtenerDatosSensor()
		self.adjustSize()
		self.show()
		self.activateWindow()
		ObtenerCapa().capa().removeSelection()
		if hasattr(self,'opcionesSensor'):
			self.opcionesSensor.hide()

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
		sensor = self.online.getSensor()
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
			conectado = sensor.conectado
			if sensor.coordinador > 0:
				self.coordinador = self.online.consultarCoordinador(sensor.coordinador)
				conectado = self.coordinador.getConectado
			if conectado == -1:
				self.iconOff.setVisible(False)
				self.iconOn.setVisible(False)
			else:
				self.iconOff.setVisible(not sensor.conectado)
				self.iconOn.setVisible(sensor.conectado)
			if sensor.calle == "" or sensor.calle.isspace():
				calle = ""
			else:
				calle = "%s, " % sensor.calle
			if sensor.colonia == "" or sensor.colonia.isspace():
				colonia = ""
			else:
				colonia = "%s, " % sensor.colonia
			self.labelDireccion.setText("<b><font color='#2980b9'>Ubicación:</font></b> %s%s%s" % (calle, colonia, sensor.municipioTexto))
			self.labelTipo.setText("<b><font color='#2980b9'>Tipo:</font></b> %s" % sensor.tipoSensorTexto)
			self.labelGrupo.setText("<b>%s</b>" % sensor.grupoTexto.upper())
			self.labelValor.setText("%2.2f<span style='font-size:12pt;color:gray;vertical-align:top'>%s</span>" % (sensor.datoActual,self.__unidades(sensor.tipoSensor)))
			self.setWindowTitle("%s: sensor de %s" % (sensor.grupoTexto,sensor.tipoSensorTexto.lower()))
			if sensor.tipoSensor == 3:
				self.graficoBarra.setVisible(True)
				#self.actualizarGrafica()
				self.botonReportes.setVisible(False)
			else:
				self.graficoBarra.setVisible(False)
				self.botonReportes.setVisible(True)
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
			return "m³"
		else:
			return ''

	def actualizarGrafica(self, sensor):
		volumen = sensor.area * sensor.altura
		self.graficoBarra.setAlignment(Qt.AlignBottom|Qt.AlignLeft)
		scene = QGraphicsScene()
		altura = self.graficoBarra.size().height()
		try:
			barra = sensor.datoActual * altura / volumen
			if barra > altura:
				barra = altura
			porcentaje = sensor.datoActual / volumen * 100
		except ZeroDivisionError:
			barra = 0
			porcentaje = 0
		grafica = QRectF(0, 0, self.graficoBarra.size().width(), int(barra))
		scene.addRect(grafica, QPen(QColor("#3498db")), QBrush(QColor("#3498db")))
		porcentajeTexto = "{:2.0f}%".format(porcentaje)
		textItemValor = scene.addText(porcentajeTexto, QFont("Verdana", 7))
		if porcentaje == 100:
			textItemValor.setDefaultTextColor(QColor(255,255,255))
			textItemValor.setPos(-4,0)
		elif porcentaje > 95:
			textItemValor.setDefaultTextColor(QColor(255,255,255))
			textItemValor.setPos(1,0)
		else:
			textItemValor.setDefaultTextColor(QColor("#2980b9"))
			textItemValor.setPos(1,-20)
		self.graficoBarra.setScene(scene)
		self.graficoBarra.setToolTip("El tanque está {} lleno".format(porcentajeTexto))

	def actualizarFoto(self, descargar=True):
		descargadorFotos = DescargadorFotos(self.online, descargar)
		miniatura = descargadorFotos.obtenerMiniatura()
		self.botonFoto.setIcon(miniatura[0])
		self.botonFoto.setIconSize(miniatura[1])
		reduccion = descargadorFotos.obtenerReduccion()
		self.fotoFlotante.setFixedSize(reduccion[1].width(), reduccion[1].height())
		self.fotoFlotante.setText(reduccion[0])

	def fotoDescargada(self, token):
		self.actualizarFoto(False)

	def iconoPresionado(self):
		icon = QIcon(':sigrdap/icons/configsensor2.png')
		self.botonConfiguracion.setIcon(icon)

	def iconoSoltado(self):
		icon = QIcon(':sigrdap/icons/configsensor.png')
		self.botonConfiguracion.setIcon(icon)

	def configuracion(self):
		if not hasattr(self,'opcionesSensor'):
			self.opcionesSensor = OpcionesSensor(self.online)
		else:
			self.opcionesSensor.show()
			self.opcionesSensor.activateWindow()
		self.opcionesSensor.setSensor(self.online.sensor,self.windowTitle())
		self.close()
		try:
			self.opcionesSensor.setCoordinador(self.coordinador)
		except:
			pass

	#<Métodos para el filtrado
	
	def filtrar(self):
		self.tablaValores.setEnabled(False)
		self.busy.show()
		t1 = threading.Thread(target=self.hiloFiltrar)
		t1.start()
		#self.hiloFiltrar()

	def hiloFiltrar(self,bandera=False):
		fechaInicial = "%04d%02d%02d" % (self.fechaInicial.date().year(), self.fechaInicial.date().month(), self.fechaInicial.date().day())
		fechaFinal = "%04d%02d%02d" % (self.fechaFinal.date().year(), self.fechaFinal.date().month(), self.fechaFinal.date().day())
		horaInicial = "%02d%02d%02d" % (self.horaInicial.time().hour(),self.horaInicial.time().minute(),self.horaInicial.time().second())
		horaFinal = "%02d%02d%02d" % (self.horaFinal.time().hour(),self.horaFinal.time().minute(),self.horaFinal.time().second())
		fechaHoraInicial = "%s%s" % (fechaInicial,horaInicial)
		fechaHoraFinal = "%s%s" % (fechaFinal,horaFinal)
		self.semaforoHistoricos = int((int(fechaHoraInicial) + int(fechaHoraFinal))/1000000)
		while self.semaforoDatosSensor:
			time.sleep(0.1)
		tConsultarHistoricos = threading.Thread(target=self.online.consultarHistoricos,args=(self.online.getSensor().idSensor,fechaHoraInicial,fechaHoraFinal))
		#self.online.consultarHistoricos(self.online.getSensor().idSensor,fechaHoraInicial,fechaHoraFinal)
		tConsultarHistoricos.start()

	def cargarRegistros(self,token):
		if token == self.semaforoHistoricos:
			self.__reiniciarTabla()
			self.cargar100()
			self.busy.hide()
			self.tablaValores.setEnabled(True)
			self.adjustSize()

	def cargar100(self):
		sensor = self.online.sensor
		unidades = self.__unidades(sensor.tipoSensor)
		historicos = self.online.historicos
		fuenteFecha = QFont("Verdana",7)
		fuenteDato = QFont("Verdana",18)
		fuenteUnidades = QFont("Verdana",8)
		rows = self.loadedRows+100
		for registro in historicos[self.loadedRows:]:
			self.tablaValores.insertRow(self.tablaValores.rowCount())
			#HORA Y FECHA
			fecha = "{}-{}-{}".format(registro.fecha[8:10],registro.fecha[5:7],registro.fecha[0:4])
			hora = "%s" % registro.fecha[11:16]
			date = datetime.date(int(fecha[6:10]),int(fecha[3:5]),int(fecha[0:2]))
			time = datetime.time(int(hora[0:2]),int(hora[3:5]),0)
			dateandtime = datetime.datetime.combine(date,time)
			item = FechaWidgetItem(dateandtime)
			item.setFont(fuenteFecha)
			self.tablaValores.setCellWidget(self.tablaValores.rowCount()-1,0,item)
			self.tablaValores.resizeRowToContents(self.tablaValores.rowCount()-1)
			#VALOR
			dato = float("{0:.2f}".format(float(registro.dato)))
			item = QTableWidgetItem(str("%.2f" % dato))
			item.setFont(fuenteDato)
			item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
			item.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
			self.tablaValores.setItem(self.tablaValores.rowCount()-1,1,item)
			#UNIDADES
			item = QTableWidgetItem(unidades)
			item.setFont(fuenteUnidades)
			item.setTextAlignment(Qt.AlignLeft|Qt.AlignVCenter)
			item.setForeground(QBrush(QColor("gray")))
			item.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
			self.tablaValores.setItem(self.tablaValores.rowCount()-1,2,item)

			self.loadedRows += 1
			if self.loadedRows >= rows:
				break
		self.labelValor.setToolTip(str(self.tablaValores.rowCount()))

	def __reiniciarTabla(self):
		self.loadedRows = 0
		while not self.tablaValores.rowCount() == 0:
			self.tablaValores.removeRow(self.tablaValores.rowCount()-1)

	def __estilizarTabla(self):
		self.tablaValores.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.tablaValores.setFocusPolicy(Qt.NoFocus)

	def scrolleado(self,value):
		if not (value == 0):
			#print("%d - %d" % (value,self.tablaValores.verticalScrollBar().maximum()))
			if value == self.tablaValores.verticalScrollBar().maximum():
				if len(self.online.historicos) > self.loadedRows:
					self.cargar100()

	#!filtrar fin>
	
	#<Métodos para graficar

	def graficar(self):
		sensor = self.online.sensor
		i = 0
		dateandtimes = []
		values = []
		for historico in self.online.historicos:
			dateAndTime = datetime.datetime(int(historico.fecha[0:4]),int(historico.fecha[5:7]),int(historico.fecha[8:10]),int(historico.fecha[11:13]),int(historico.fecha[14:16]),int(historico.fecha[17:19]))
			dateandtimes.append(dateAndTime)
			values.append(float(historico.dato))
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
		self.calendario = Calendario(self.online,sensor)
		self.close()

	#!reportes fin>

	def cerrar(self):
		self.hide()

#EVENTOOOOOOS

	def resizeEvent(self, event):
		toReturn = super().resizeEvent(event)
		try:
			sensor = self.online.getSensor()
			if int(sensor.tipoSensor) == 3:
				self.actualizarGrafica(sensor)
		except AttributeError:
			pass
		return toReturn
