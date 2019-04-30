# -*- coding: utf-8 -*-

import threading
import time

import qgis.utils

from qgis.core import QgsVectorLayerJoinInfo, QgsProject

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
		pass

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
			layer = ObtenerCapa.capa()
			provider = layer.dataProvider()
			updateMap = {}
			fieldId0 = provider.fields().indexFromName('id')
			fieldId1 = provider.fields().indexFromName('alarma')
			fieldId2 = provider.fields().indexFromName('tipoSensor')
			features = provider.getFeatures()
			t1 = threading.Thread(target=self.online.actualizarEstados)
			t1.start()
			diferentes = False
			for feature in features:
				sensor = self.getSensor(feature.attribute(fieldId0))
				updateMap[feature.id()] = {fieldId1:sensor.alarma,fieldId2:sensor.tipoSensor}
				if not (sensor.alarma == feature.attribute(2)):
					diferentes = True
			if diferentes:
				#print("diferentes")
				provider.changeAttributeValues(updateMap)
				layer.triggerRepaint()
		except:
			pass

	def getSensor(self,idFeature):
		sensores = self.online.getSensores()
		for sensor in sensores:
			if sensor.idFeature == idFeature:
				return sensor