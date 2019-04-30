# -*- coding: UTF8 -*-

import os
import qgis.utils
import time

from functools import partial

from qgis.core import *
from qgis.gui import *

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QValidator, QDoubleValidator, QCursor
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QPushButton, QTableWidgetItem, QWidget

from .obtener_presion import ObtenerPresion
from .reportes import Reportes
from .sumar_volumen import SumarVolumen

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'calendario.ui'))

class Calendario(QtWidgets.QWidget, FORM_CLASS):

	def __init__(self,online,sensor,parent=None):
		"""Constructor."""
		super(Calendario, self).__init__(parent)
		self.setupUi(self)
		self.online = online
		self.sensor = sensor
		self.sumarVolumen = SumarVolumen(self.online)
		self.obtenerPresion = ObtenerPresion(self.online,sensor.idSensor)
		self.__cambiarContexto()
		self.__signals()
		self.barraDeProgreso.setVisible(False)
		self.show()
		self.cambioDeDia()

	def __signals(self):
		self.calendario.selectionChanged.connect(partial(self.cambioDeDia,forzar=False))
		self.calendario.currentPageChanged.connect(self.cambioDeMes)
		self.cambioDeMes(self.calendario.selectedDate().year(),self.calendario.selectedDate().month())
		self.sumarVolumen.sumando.connect(self.jair)
		self.botonDia.clicked.connect(self.generarReporteDelDia)
		self.botonMes.clicked.connect(self.generarReporteDelMes)

	def cambioDeDia(self,forzar=False,cambioDeMes=True,actualizarMes=False,day=1):
		year = self.calendario.yearShown()
		month = self.calendario.monthShown()
		if not actualizarMes:
			day = self.calendario.selectedDate().day()
		fecha = '%04d%02d%02d' % (year,month,day)
		#maxima = 0
		try:
			valid_date = time.strptime(fecha,'%Y%m%d')
			if self.sensor.tipoSensor == 1:
				try:
					suma = '%.2f' % float(self.obtenerPresion.minmaxDia(fecha,0))
					self.totalDiaU.setText("mca")
					self.maxDiaU.setText("mca")
				except TypeError:
					suma = 'Indefinido'
					self.totalDiaU.setText("")
					self.maxDiaU.setText("")
				try:
					maxima = '%.2f' % float(self.obtenerPresion.minmaxDia(fecha,1))
				except TypeError:
					maxima = 'Indefinido'
			elif self.sensor.tipoSensor == 2:
				suma = self.sumarVolumen.obtenerSuma(self.sensor.idSensor,fecha,forzar)
				maxima = '%.2f' % 0
		except ValueError:
			suma = 'Invalid date!'
		if not actualizarMes:
			self.totalDia.setText(suma)
			self.maxDia.setText(maxima)
		if cambioDeMes:
			self.cambioDeMes(self.calendario.selectedDate().year(),self.calendario.selectedDate().month())

	def cambioDeMes(self,year,month):
		mes = "%04d%02d" % (year,month)
		if self.sensor.tipoSensor == 1:
			suma = "%.2f" % float(self.obtenerPresion.minimaMes(mes))
			maxima = "%.2f" % float(self.obtenerPresion.maximaMes(mes))
		elif self.sensor.tipoSensor == 2:
			suma = self.online.consultarAcumuladoDelMes(self.sensor.idSensor,mes)
			maxima = '%.2f' % 0
		self.totalMes.setText(suma)
		self.maxMes.setText(maxima)

	def actualizarMes(self):
		day = 1
		self.labelEstado.setText("Recalculando...")
		self.barraDeProgreso.setVisible(True)
		while day<=31:
			self.cambioDeDia(True,False,True,day)
			day += 1
			self.barraDeProgreso.setValue(day)
		self.cambioDeMes(self.calendario.yearShown(),self.calendario.monthShown())
		self.barraDeProgreso.setVisible(False)
		self.labelEstado.setText("¡Listo!")

	def generarReporteDelDia(self):
		reportes = Reportes(self.online)
		year = self.calendario.yearShown()
		month = self.calendario.monthShown()
		day = self.calendario.selectedDate().day()
		fecha = '%04d-%02d-%02d' % (year,month,day)
		try:
			self.labelEstado.setText("Almacenado satisfactoriamente en %s" % reportes.generarReporteDelDia(self.sensor.idSensor,fecha,self.sensor.tipoSensor))
		except:
			self.labelEstado.setText("No se generó el reporte")

	def generarReporteDelMes(self):
		reportes = Reportes(self.conector)
		year = self.calendario.yearShown()
		month = self.calendario.monthShown()
		mes = '%04d-%02d' % (year,month)
		try:
			self.labelEstado.setText("Almacenado satisfactoriamente en %s" % str(reportes.generarReporteDelMes(self.sensor.idSensor,mes,self.sensor.tipoSensor)))
		except:
			self.labelEstado.setText("No se generó el reporte")

	def jair(self,i):
		self.labelEstado.setText(str(i))

	def cerrar(self):
		self.close()

	def __cambiarContexto(self):
		if self.sensor.tipoSensor == 1:
			flag = True
		elif self.sensor.tipoSensor == 2:
			flag = False
		if flag:
			self.labelTotalDia.setText("Presión mínima del día:")
			self.totalDiaU.setText("mca")
			self.labelTotalMes.setText("Presión mínima del mes:")
			self.totalMesU.setText("mca")
		else:
			self.labelTotalDia.setText("Total del día:")
			self.totalDiaU.setText("m³")
			self.labelTotalMes.setText("Total del mes:")
			self.totalMesU.setText("m³")
		self.labelMaxDia.setVisible(flag)
		self.maxDia.setVisible(flag)
		self.maxDiaU.setVisible(flag)
		self.labelMaxMes.setVisible(flag)
		self.maxMes.setVisible(flag)
		self.maxMesU.setVisible(flag)