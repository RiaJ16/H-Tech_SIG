# -*- coding: UTF8 -*-

import datetime as dt

from .historico_diario import HistoricoDiario

class ObtenerPresion:

	def __init__(self,online,idSensor):
		self.online = online
		self.idSensor = idSensor
		historicoDiario = HistoricoDiario()

	def minmaxDia(self,fecha,minmax=0):
		historicoDiario = HistoricoDiario()
		try:
			registro = self.online.consultarHistoricoDiario(self.idSensor,fecha,minmax)
			historicoDiario.set(registro)
			finalizado = int(historicoDiario.finalizado)
			dato = historicoDiario.dato
			if not finalizado:
				dato = self.online.consultarPresion(self.idSensor,fecha,minmax)['minmax']
				self.almacenar(dato,fecha,True,minmax)
		except:
			dato = self.online.consultarPresion(self.idSensor,fecha,minmax)['minmax']
			self.almacenar(dato,fecha,False,minmax)
		return dato

	def minimaMes(self,fecha):
		dato = self.online.consultarPresionMes(self.idSensor,fecha,0)['minmax']
		if dato == None:
			dato = '0'
		return dato

	def maximaMes(self,fecha):
		dato = self.online.consultarPresionMes(self.idSensor,fecha,1)['minmax']
		if dato == None:
			dato = '0'
		return dato

	def almacenar(self,dato,fecha,update,minmax=0):
		historicoDiario = HistoricoDiario('',self.idSensor,fecha,minmax,dato,self.comprobarDia(fecha))
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