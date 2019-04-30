# -*- coding: UTF8 -*-

import datetime as dt

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from .historico_diario import HistoricoDiario

class SumarVolumen(QObject):

	sumando = pyqtSignal(int)

	def __init__(self,online):
		QObject.__init__(self)
		self.online = online

	def obtenerSuma(self,idSensor,fecha,forzar):
		historicoDiario = HistoricoDiario()
		try:
			registro = self.online.consultarHistoricoDiario(idSensor,fecha)
			historicoDiario.set(registro)
			finalizado = int(historicoDiario.finalizado)
			dato = historicoDiario.dato
			if not finalizado:
				dato = self.obtenerValores(idSensor,fecha)
				self.almacenar(dato,fecha,idSensor,True)
		except:
			dato = self.obtenerValores(idSensor,fecha)
			self.almacenar(dato,fecha,idSensor,False)
		return dato

	def obtenerValores(self,idSensor,fecha):
		try:
			historicos = self.online.consultarQuinceMinutos(idSensor,fecha)
			acumulado = 0
			for historico in historicos:
				acumulado += (float(historico.dato)*60*15/1000)
			if acumulado == 0:
				acumuladoSt = '%.2f' % 0
			else:
				acumuladoSt = '%.2f' % acumulado
		except:
			acumuladoSt = '%.2f' % 0
		return acumuladoSt

	def almacenar(self,dato,fecha,idSensor,update):
		historicoDiario = HistoricoDiario('',idSensor,fecha,0,dato,self.comprobarDia(fecha))
		if update:
			self.online.actualizarHistoricoDiario(historicoDiario)
		else:
			self.online.insertarHistoricoDiario(historicoDiario)

	def comprobarDia(self,fecha):
		hoy = dt.date.today()
		hoyInt = int('%04d%02d%02d' % (hoy.year,hoy.month,hoy.day))
		fecha = int(fecha)
		if fecha < hoyInt:
			return 1
		else:
			return 0