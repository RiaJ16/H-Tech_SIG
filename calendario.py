# -*- coding: UTF8 -*-

import locale
import os
import qgis.utils
import time

from functools import partial

from qgis.core import *
from qgis.gui import *

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QIcon, QPixmap

from .reportes import Reportes

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'calendario.ui'))

class Calendario(QtWidgets.QWidget, FORM_CLASS):

	def __init__(self,online,sensor,parent=None):
		"""Constructor."""
		super(Calendario, self).__init__(parent)
		self.setupUi(self)
		self.datos = dict()
		self.online = online
		self.sensor = sensor
		self.__cambiarContexto()
		self.barraDeProgreso.setVisible(False)
		if self.cambioDeMes(self.calendario.selectedDate().year(),self.calendario.selectedDate().month()):
			self.show()
		self.__signals()

	def __signals(self):
		self.calendario.selectionChanged.connect(self.cambioDeDia)
		self.calendario.currentPageChanged.connect(self.cambioDeMes)
		self.botonDia.clicked.connect(self.generarReporteDelDia)
		self.botonMes.clicked.connect(self.generarReporteDelMes)
		self.botonPersonalizado.clicked.connect(self.__elegirFechas)

	def cambioDeDia(self):
		self.totalDia.setText("%.2f" % 0)
		self.maxDia.setText("%.2f" % 0)
		year = self.calendario.yearShown()
		month = self.calendario.monthShown()
		day = self.calendario.selectedDate().day()
		mes = "%04d%02d01" % (year,month)
		fecha = '%s%02d' % (mes[0:6],day)
		for historial in self.datos[mes]['historial_del_dia']:
			if historial['fecha'] == fecha:
				if historial['minmax'] == '0':
					self.totalDia.setText("%.2f" % float(historial['dato']))
				elif historial['minmax'] == '1':
					self.maxDia.setText("%.2f" % float(historial['dato']))

	def cambioDeMes(self,year,month):
		self.totalMes.setText("%.2f" % 0)
		self.maxMes.setText("%.2f" % 0)
		mes = "%04d%02d01" % (year,month)
		try:
			if mes not in self.datos:
				self.datos[mes] = self.online.consultarHistorial(self.sensor.idSensor,mes)
			for historial in self.datos[mes]['historial_del_mes']:
				if historial['minmax'] == '0':
					self.totalMes.setText("%.2f" % float(historial['dato']))
				elif historial['minmax'] == '1':
					self.maxMes.setText("%.2f" % float(historial['dato']))
			self.cambioDeDia()
			return True
		except TypeError:
			self.hide()
			return False

	def generarReporteDelDia(self):
		reportes = Reportes(self.online)
		year = self.calendario.yearShown()
		month = self.calendario.monthShown()
		day = self.calendario.selectedDate().day()
		fecha = '%04d%02d%02d' % (year,month,day)
		mes = "%s01" % fecha[0:6]
		dato = []
		for historial in self.datos[mes]['historial_del_dia']:
			if historial['fecha'] == fecha:
				dato.append(float(historial['dato']))
		try:
			reportes.generarReporteDelDia(self.sensor,fecha,dato)
			self.labelEstado.setText("Almacenado satisfactoriamente en la ruta indicada")
		except IndexError:
			self.labelEstado.setText("No se generó el reporte")
		except PermissionError:
			self.labelEstado.setText("No se generó el reporte. Archivo ocupado")
		except FileNotFoundError:
			self.labelEstado.setText('')

	def generarReporteDelMes(self):
		reportes = Reportes(self.online)
		year = self.calendario.yearShown()
		month = self.calendario.monthShown()
		mes = '%04d%02d01' % (year,month)
		try:
			reportes.generarReporteDelMes(self.sensor,mes,self.datos[mes])
			self.labelEstado.setText("Almacenado satisfactoriamente en la ruta indicada")
		except IndexError:
			self.labelEstado.setText("No se generó el reporte")
		except PermissionError:
			self.labelEstado.setText("No se generó el reporte. Archivo ocupado")
		except FileNotFoundError:
			self.labelEstado.setText('')

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

	def __elegirFechas(self):
		self.__bloquearInterfaz()
		self.labelEstado.setText("Elige el primer día")
		self.calendario.selectionChanged.disconnect()
		self.calendario.clicked.connect(self.__elegirSegundoDia)

	def __elegirSegundoDia(self):
		self.labelEstado.setText("Elige el último día")
		fechaInicial = self.calendario.selectedDate().toPyDate()
		self.labelFechas.setText(fechaInicial.strftime("Del %d de %B de %Y al..."))
		self.calendario.clicked.disconnect()
		self.calendario.clicked.connect(partial(self.generarReportePersonalizado,fechaInicial))

	def generarReportePersonalizado(self,fechaInicial):
		fechaFinal = self.calendario.selectedDate().toPyDate()
		if fechaFinal > fechaInicial:
			self.labelFechas.setText('%s %s' % (fechaInicial.strftime("Del %d de %B de %Y al"),fechaFinal.strftime("%d de %B de %Y")))
			reportes = Reportes(self.online)
			try:
				reportes.generarReportePersonalizado(self.sensor,fechaInicial,fechaFinal,self.datos)
				self.labelFechas.setText('')
				self.labelEstado.setText("Almacenado satisfactoriamente en la ruta indicada")
			except IndexError:
				self.labelFechas.setText('')
				self.labelEstado.setText("No se generó el reporte")
			except PermissionError:
				self.labelFechas.setText('')
				self.labelEstado.setText("No se generó el reporte. Archivo ocupado")
			except FileNotFoundError:
				self.labelFechas.setText('')
				self.labelEstado.setText('')
		else:
			self.labelFechas.setText('')
			self.labelEstado.setText("No se generó el reporte. La fecha inicial tiene que ser menor que la final")
		self.__bloquearInterfaz(False)
		self.calendario.clicked.disconnect()
		self.calendario.selectionChanged.connect(self.cambioDeDia)

	def __bloquearInterfaz(self,flag=True):
		self.botonDia.setEnabled(not flag)
		self.botonMes.setEnabled(not flag)
		self.labelTotalDia.setEnabled(not flag)
		self.totalDia.setEnabled(not flag)
		self.totalDiaU.setEnabled(not flag)
		self.labelTotalMes.setEnabled(not flag)
		self.totalMes.setEnabled(not flag)
		self.totalMesU.setEnabled(not flag)
		self.labelMaxDia.setEnabled(not flag)
		self.maxDia.setEnabled(not flag)
		self.maxDiaU.setEnabled(not flag)
		self.labelMaxMes.setEnabled(not flag)
		self.maxMes.setEnabled(not flag)
		self.maxMesU.setEnabled(not flag)
		icon = QIcon()
		if flag:
			icon.addPixmap(QPixmap(':Calendario/icons/rep-cancelar.png'))
			self.botonPersonalizado.setToolTip("Cancelar")
			self.botonPersonalizado.disconnect()
			self.botonPersonalizado.clicked.connect(self.__cancelar)
		else:
			icon.addPixmap(QPixmap(':Calendario/icons/rep-personalizable.png'))
		self.botonPersonalizado.setIcon(icon)

	def __cancelar(self):
		self.labelEstado.setText('')
		self.labelFechas.setText('')
		self.botonPersonalizado.setToolTip("Generar reporte personalizado")
		self.__bloquearInterfaz(False)
		self.calendario.clicked.disconnect()
		self.calendario.selectionChanged.connect(self.cambioDeDia)
		self.botonPersonalizado.disconnect()
		self.botonPersonalizado.clicked.connect(self.__elegirFechas)