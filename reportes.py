# -*- coding: UTF8 -*-

import datetime
import xlsxwriter

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QTextCodec

class Reportes:

	def __init__(self,online):
		self.online = online

	def generarReporteDelDia(self,sensor,fecha,dato):
		filename = self.obtenerRuta('%sD' % sensor.tipoSensorTexto[0].upper(),fecha,sensor)
		libro = xlsxwriter.Workbook(filename)
		formatoTitulo = libro.add_format({'bold': True, 'font_color': "#3498db",'font_size': "20"})
		formatoTitulares = libro.add_format({'bold': True, 'align': 'center', 'font_color': 'white', 'bg_color': "#3498db",'font_size': "12"})
		formatoFechaHora = libro.add_format({'bold': True, 'border_color': "#3498db", 'right': True, 'num_format': 'hh:mm AM/PM'})
		formatoDia = libro.add_format({'bold': True, 'font_color': "#3498db",'font_size': "15"})
		hoja = libro.add_worksheet()
		hoja.set_column('A:A', 22)
		hoja.set_column('B:B', 15)
		hoja.write(0,0,sensor.grupoTexto.upper(),formatoTitulo)
		fechaFormat = datetime.date(int(fecha[0:4]),int(fecha[4:6]),int(fecha[6:8]))
		hoja.write(1,0,("%s" % fechaFormat.strftime("%d de %B de %Y")).upper(),formatoDia)
		hoja.write(2,0,"Fecha y hora",formatoTitulares)
		col = 3
		datos = self.online.consultarHistoricos(sensor.idSensor,fecha,fecha+"235959")
		datos.reverse()
		for historico in datos:
			fecha = datetime.date(int(historico.fecha[0:4]),int(historico.fecha[5:7]),int(historico.fecha[8:10]))
			hora = datetime.time(int(historico.fecha[11:13]),int(historico.fecha[14:16]),int(historico.fecha[17:19]))
			fechaHora = datetime.datetime.combine(fecha,hora)
			hoja.write(col,0,fechaHora,formatoFechaHora)
			hoja.write(col,1,float(historico.dato))
			col += 1
		if sensor.tipoSensor == 2:
			self.agregadosFlujoD(hoja,col,formatoTitulares,dato)
		else:
			self.agregadosPresionD(hoja,col,formatoTitulares,dato)
		libro.close()
		return filename

	def agregadosFlujoD(self,hoja,col,formatoTitulares,dato):
		hoja.write(2,1,"Flujo (lps)",formatoTitulares)
		hoja.write(col,0,"Volumen calculado (m³)",formatoTitulares)
		hoja.write(col,1,dato[0])

	def agregadosPresionD(self,hoja,col,formatoTitulares,dato):
		hoja.write(2,1,"Presión (mca)",formatoTitulares)
		hoja.write(col,0,"Presión mínima",formatoTitulares)
		hoja.write(col,1,dato[0])
		col += 1
		hoja.write(col,0,"Presión máxima",formatoTitulares)
		hoja.write(col,1,dato[1])

	def generarReporteDelMes(self,sensor,mes,historial):
		filename = self.obtenerRuta('%sM' % sensor.tipoSensorTexto[0].upper(),mes[0:6],sensor)
		libro = xlsxwriter.Workbook(filename)
		formatoTitulo = libro.add_format({'bold': True, 'font_color': "#3498db",'font_size': "20"})
		formatoTitulares = libro.add_format({'bold': True, 'align': 'center', 'font_color': 'white', 'bg_color': "#3498db",'font_size': "12"})
		formatoFecha = libro.add_format({'bold': True, 'border_color': "#3498db", 'right': True, 'num_format': 'd-mmm-yyyy'})
		formatoMes = libro.add_format({'bold': True, 'font_color': "#3498db",'font_size': "15"})
		historialDelMes = historial['historial_del_mes']
		fecha = datetime.date(int(historialDelMes[0]['mes'][0:4]),int(historialDelMes[0]['mes'][5:7]),int(historialDelMes[0]['mes'][8:10]))
		hoja = libro.add_worksheet()
		hoja.set_column('A:A', 23)
		hoja.set_column('B:B', 23)
		hoja.write(0,0,sensor.grupoTexto.upper(),formatoTitulo)
		hoja.write(1,0,("%s" % fecha.strftime("%B de %Y")).upper(),formatoMes)
		hoja.write(2,0,"Fecha",formatoTitulares)
		col = 3
		col2 = 3
		for historico in historial['historial_del_dia']:
			fecha = datetime.date(int(historico['fecha'][0:4]),int(historico['fecha'][4:6]),int(historico['fecha'][6:8]))
			if historico['minmax'] == '0':
				hoja.write(col,0,fecha,formatoFecha)
				hoja.write(col,1,float(historico['dato']))
				col += 1
			elif historico['minmax'] == '1':
				hoja.write(col2,2,float(historico['dato']))
				col2 += 1
		if sensor.tipoSensor == 1:
			hoja.set_column('C:C', 23)
			self.agregadosPresionM(hoja,formatoTitulares,col,historial['historial_del_mes'])
		elif sensor.tipoSensor == 2:
			self.agregadosFlujoM(hoja,formatoTitulares,col,historial['historial_del_mes'])
		libro.close()
		return filename

	def agregadosFlujoM(self,hoja,formatoTitulares,col,historialDelMes):
		hoja.write(2,1,"Volumen calculado (m³)",formatoTitulares)
		hoja.write(col,0,"Total del mes (m³)",formatoTitulares)
		hoja.write(col,1,float(historialDelMes[0]['dato']))

	def agregadosPresionM(self,hoja,formatoTitulares,col,historialDelMes):
		hoja.write(2,1,"Presión mínima (mca)",formatoTitulares)
		hoja.write(2,2,"Presión máxima (mca)",formatoTitulares)
		hoja.write(col,0,"Presión del mes (mca)",formatoTitulares)
		hoja.write(col,1,float(historialDelMes[0]['dato']))
		hoja.write(col,2,float(historialDelMes[1]['dato']))

	def generarReportePersonalizado(self,sensor,fechaInicial,fechaFinal,historial):
		filename = self.obtenerRutaPersonalizado('%sC' % sensor.tipoSensorTexto[0].upper(),sensor,fechaInicial.strftime('%Y%m%d'),fechaFinal.strftime('%Y%m%d'))
		libro = xlsxwriter.Workbook(filename)
		formatoTitulo = libro.add_format({'bold': True, 'font_color': "#3498db",'font_size': "20"})
		formatoTitulares = libro.add_format({'bold': True, 'align': 'center', 'font_color': 'white', 'bg_color': "#3498db",'font_size': "12"})
		formatoFecha = libro.add_format({'bold': True, 'border_color': "#3498db", 'right': True, 'num_format': 'd-mmm-yyyy'})
		formatoMes = libro.add_format({'bold': True, 'font_color': "#3498db",'font_size': "15"})
		hoja = libro.add_worksheet()
		hoja.set_column('A:A', 25)
		hoja.set_column('B:B', 23)
		hoja.write(0,0,sensor.grupoTexto.upper(),formatoTitulo)
		hoja.write(1,0,"Del %s al %s" % (fechaInicial.strftime('%d de %B de %Y'),fechaFinal.strftime('%d de %B de %Y')),formatoMes)
		hoja.write(2,0,"Fecha",formatoTitulares)
		mesInicial = fechaInicial.strftime('%Y%m01')
		meses = []
		historicosNoFiltrados = []
		historicos = []
		for mes in historial:
			meses.append(mes)
		meses.sort()
		for mes in meses:
			historicosNoFiltrados.extend(historial[mes]['historial_del_dia'])
		col = 3
		col2 = 3
		agregar = False
		for historico in historicosNoFiltrados:
			if int(historico['fecha']) >= int(fechaInicial.strftime('%Y%m%d')):
				agregar = True
			if agregar:
				historicos.append(historico)
			if historico['fecha'] == fechaFinal.strftime('%Y%m%d'):
				if sensor.tipoSensor == 1:
					if historico['minmax'] == '1':
						break
				else:
					break
		for historico in historicos:
			if historico['minmax'] == '0':
				fecha = datetime.date(int(historico['fecha'][0:4]),int(historico['fecha'][4:6]),int(historico['fecha'][6:8]))
				hoja.write(col,0,fecha,formatoFecha)
				hoja.write(col,1,float(historico['dato']))
				col += 1
			elif historico['minmax'] == '1':
				hoja.write(col2,2,float(historico['dato']))
				col2 += 1
		if sensor.tipoSensor == 1:
			hoja.set_column('C:C', 23)
			self.agregadosPresionP(hoja,formatoTitulares,col)
		elif sensor.tipoSensor == 2:
			self.agregadosFlujoP(hoja,formatoTitulares,col)
		libro.close()
		return filename

	def agregadosFlujoP(self,hoja,formatoTitulares,col):
		hoja.write(2,1,"Volumen calculado (m³)",formatoTitulares)
		hoja.write(col,0,"Total del periodo (m³)",formatoTitulares)
		hoja.write(col,1,'=SUM(B4:B%d)' % col)

	def agregadosPresionP(self,hoja,formatoTitulares,col):
		hoja.write(2,1,"Presión mínima (mca)",formatoTitulares)
		hoja.write(2,2,"Presión máxima (mca)",formatoTitulares)
		hoja.write(col,0,"Presión del periodo (mca)",formatoTitulares)
		hoja.write(col,1,'=MIN(B4:B%d)' % col)
		hoja.write(col,2,'=MAX(C4:C%d)' % col)

	def obtenerRuta(self,prefijo,fecha,sensor):
		fileDialog = QFileDialog()
		fileDialog.setAcceptMode(QFileDialog.AcceptSave)
		filename=fileDialog.getSaveFileName(None,"Title","REPORTE%s%04d%s-%s" % (prefijo,sensor.idSensor,fecha.replace('-',''),sensor.grupoTexto.replace(' ','_')),"Libro de Excel (*.xlsx)")[0]
		return filename

	def obtenerRutaPersonalizado(self,prefijo,sensor,fechaInicial,fechaFinal):
		fileDialog = QFileDialog()
		fileDialog.setAcceptMode(QFileDialog.AcceptSave)
		filename=fileDialog.getSaveFileName(None,"Title","REPORTE%s%04d%s%s-%s" % (prefijo,sensor.idSensor,fechaInicial,fechaFinal,sensor.grupoTexto.replace(' ','_')),"Libro de Excel (*.xlsx)")[0]
		return filename