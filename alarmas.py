# -*- coding: utf-8 -*-

import threading
import time

import qgis.utils

from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsProject, QgsVectorLayerJoinInfo

from .obtener_capa import ObtenerCapa
from .online import Online

exitFlag = 0

class Alarmas():

	def __init__(self):
		self.iface = qgis.utils.iface
		self.online = Online()
		self.__signals()

	def __signals(self):
		self.online.signalLoggedIn.connect(self.consultarSensores)
		self.online.signalSensoresConsultados.connect(self.actualizar)
		self.online.signalSensoresConsultados.connect(self.revisarSensores)

	def login(self):
		try:
			t3 = threading.Thread(name='login daemon',target=self.online.login)
			t3.start()
		except:
			pass

	def consultarSensores(self,loggedIn):
		if not (loggedIn == 5):
			t2 = threading.Thread(name='daemon',target=self.online.consultarSensores)
			t2.start()

	def actualizar(self):
		try:
			bombas = self.online.consultarBombas()
			layer = ObtenerCapa().capa()
			provider = layer.dataProvider()
			updateMap = {}
			fieldId0 = provider.fields().indexFromName('id')
			fieldId1 = provider.fields().indexFromName('alarma')
			fieldId2 = provider.fields().indexFromName('tipoSensor')
			fieldId3 = provider.fields().indexFromName('bomba')
			fieldId4 = provider.fields().indexFromName('estadoB')
			features = provider.getFeatures()
			#t1 = threading.Thread(target=self.online.actualizarEstados)
			#t1.start()
			diferentes = False
			for feature in features:
				sensor = self.getSensor(feature.attribute(fieldId0))
				bomba = self.getBomba(feature.attribute(fieldId0), bombas)
				if bomba == 0:
					idBomba = 0
					estadoB = 0
				else:
					idBomba = int(bomba['idGrupo'])
					estadoB = int(bomba['estado'])
				updateMap[feature.id()] = {fieldId1:sensor.alarma,fieldId2:sensor.tipoSensor,fieldId3:idBomba,fieldId4:estadoB}
				if not (sensor.alarma == feature.attribute(2) and idBomba == feature.attribute(3) and estadoB == feature.attribute(4)):
					diferentes = True
			if diferentes:
				#print("diferentes")
				provider.changeAttributeValues(updateMap)
				layer.triggerRepaint()
		except:
			pass

	def revisarSensores(self):
		try:
			layer = ObtenerCapa().capa()
			provider = layer.dataProvider()
			fields = layer.fields()
			for sensor in self.online.sensores:
				flag = 1
				for objeto in provider.getFeatures():
					if sensor.idFeature == objeto.attribute(0):
						(x,y) = objeto.geometry().asPoint()
						if not (round(sensor.x,8) == round(x,8) and round(sensor.y,8) == round(y,8)):
							#print("%.02f is this" % sensor.idFeature)
							geometria = QgsGeometry.fromPointXY(QgsPointXY(sensor.x,sensor.y))
							provider.changeGeometryValues({objeto.id():geometria})
							layer.triggerRepaint()
						flag = 0
						break
				if flag:
					#print("%.02f is no good" % sensor.idFeature)
					#print("%.06f - %.06f" % (sensor.x,sensor.y))
					objeto = QgsFeature(layer.fields())
					objeto.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(sensor.x,sensor.y)))
					objeto.setAttributes([sensor.idFeature, sensor.tipoSensor, sensor.alarma])
					provider.addFeatures([objeto])
					layer.triggerRepaint()
		except AttributeError:
			pass
		pass

	def getSensor(self,idFeature):
		sensores = self.online.getSensores()
		for sensor in sensores:
			if sensor.idFeature == idFeature:
				return sensor

	def getBomba(self, idFeature, bombas):
		for bomba in bombas:
			if int(bomba['idFeature']) == idFeature:
				return bomba
		return 0
