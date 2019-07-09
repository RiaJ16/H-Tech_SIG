# -*- coding: utf-8 -*-

import threading
import time

import qgis.utils

from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsProject, QgsVectorLayerJoinInfo

from .alarmas import Alarmas
from .obtener_capa import ObtenerCapa

exitFlag = 0

class LimpiarObjetos():

	def limpiar(self):
		try:
			layer = ObtenerCapa().capa()
			provider = layer.dataProvider()
			fields = layer.fields()
			ids = []
			for objeto in provider.getFeatures():
				ids.append(objeto.id())
			provider.deleteFeatures(ids)
			layer.triggerRepaint()
			Alarmas().revisarSensores()
		except AttributeError:
			pass
		pass