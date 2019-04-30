# -*- coding: UTF8 -*-

import xlsxwriter

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QTextCodec

class Reportes:

	def __init__(self,online):
		self.online = online
		QTextCodec.setCodecForCStrings(QTextCodec.codecForName("UTF8"))

	def generarReporteDelDia(self,idSensor,fecha,tipoSensor):
		tipoSensorTexto = self.conector.consultarNombreID(tipoSensor)
		filename = self.obtenerRuta('%sD' % tipoSensorTexto[0].upper(),fecha,idSensor)
		libro = xlsxwriter.Workbook(filename)
		hoja = libro.add_worksheet()
		datos = self.conector.consultarHistorialFechas(idSensor,fecha,fecha,True)
		hoja.write(0,0,"Sensor %d" % idSensor)
		hoja.write(1,0,"Fecha")
		hoja.write(1,1,"Hora")
		col = 2
		for dia, hora, dato in datos:
			hoja.write(col,0,dia)
			hoja.write(col,1,hora)
			hoja.write(col,2,dato)
			col += 1
		if tipoSensor == 2:
			self.agregadosFlujoD(hoja,col)
		else:
			self.agregadosPresionD(hoja,col)
		libro.close()
		return filename

	def agregadosFlujoD(self,hoja,col):
		hoja.write(1,2,"Flujo (lps)")
		hoja.write(col,0,"Promedio")
		hoja.write(col,2,"=AVERAGE(C3:C%d)" % col)
		col += 1
		hoja.write(col,0,"Gasto promedio (m³)".decode('utf-8'))
		hoja.write(col,2,"=C%d*60*60*24/1000" % col)

	def agregadosPresionD(self,hoja,col):
		hoja.write(1,2,"Presión (mca)".decode('utf-8'))
		hoja.write(col,0,"Presión promedio".decode('utf-8'))
		hoja.write(col,2,"=AVERAGE(C3:C%d)" % col)

	def generarReporteDelMes(self,idSensor,mes,tipoSensor):
		tipoSensorTexto = self.conector.consultarNombreID(tipoSensor)
		filename = self.obtenerRuta('%sM' % tipoSensorTexto[0].upper(),mes,idSensor)
		libro = xlsxwriter.Workbook(filename)
		hoja = libro.add_worksheet()
		datos = self.conector.consultarDatosDelMes(idSensor,mes)
		hoja.write(0,0,"Sensor %d" % idSensor)
		hoja.write(1,0,"Fecha")
		col = 2
		for dia, dato in datos:
			hoja.write(col,0,dia)
			hoja.write(col,1,dato)
			col += 1
		if tipoSensor == 2:
			self.agregadosFlujoM(hoja,col)
		else:
			self.agregadosPresionM(idSensor,mes,hoja)
		libro.close()
		return filename

	def agregadosFlujoM(self,hoja,col):
		hoja.write(1,1,"Volumen acumulado (m³)".decode('utf-8'))
		hoja.write(col,0,"Total")
		hoja.write(col,1,"=SUM(B3:B%d)" % col)

	def agregadosPresionM(self,idSensor,mes,hoja):
		datos = self.conector.consultarDatosDelMes(idSensor,mes,1)
		col = 2
		for dia, dato in datos:
			hoja.write(col,2,dato)
			col += 1
		hoja.write(1,1,"Presión mínima (mca)".decode('utf-8'))
		hoja.write(1,2,"Presión máxima (mca)".decode('utf-8'))
		hoja.write(col,2,"=SUM(C3:C%d)" % col)
		hoja.write(col,0,"Mes")
		hoja.write(col,1,"=MIN(B3:B%d)" % col)
		hoja.write(col,2,"=MAX(C3:C%d)" % col)

	def obtenerRuta(self,prefijo,fecha,idSensor):
		fileDialog = QFileDialog()
		fileDialog.setAcceptMode(QFileDialog.AcceptSave)
		filename=fileDialog.getSaveFileName(None,"Title","REPORTE%s%04d%s" % (prefijo,idSensor,fecha.replace('-','')),"Libro de Excel (*.xlsx)")
		return filename