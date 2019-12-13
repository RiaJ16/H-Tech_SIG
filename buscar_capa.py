# -*- coding: utf-8 -*-

import os

from qgis.core import *

from PyQt5 import uic
from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QListWidgetItem

from .limpiar_objetos import LimpiarObjetos

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'ventana_capas.ui'))


class BuscarCapa(QDialog,FORM_CLASS):

	def __init__(self,parent=None):
		super(BuscarCapa, self).__init__(parent)
		self.setupUi(self)
		self.botonAceptar.clicked.connect(self.capaSeleccionada)
		self.botonGenerarNuevaCapa.clicked.connect(self.generarNuevaCapa)
		self.listaCapas.itemSelectionChanged.connect(self.seleccionCambiada)
		self.capa = ''

	def leerDatos(self):
		nombreCapa = "capaSensores"
		linea = ''
		path = "%s/.sigrdap" % os.path.expanduser('~')
		print(path)
		try:
			archivo = open("%s/%s" % (path,nombreCapa), "r")
			linea = archivo.readline()
			archivo.close()
			self.obtenerCapa(linea)
		except IOError:
			self.cargarLista()
		return self.capa

	def cargarLista(self):
		for layer in QgsProject.instance().mapLayers().values():
			if layer.type() == QgsMapLayer.VectorLayer:
				if layer.geometryType() == 0:
					item = QListWidgetItem("%s" % layer.name())
					self.listaCapas.addItem(item)
		self.exec_()

	def escribirDatos(self,capa):
		nombreCapa = "capaSensores"
		path = "%s/.sigrdap" % os.path.expanduser('~')
		if not os.path.exists(path):
			os.makedirs(path)
		archivo = open("%s/%s" % (path,nombreCapa), "w")
		archivo.write("%s" % capa.id())
		archivo.close()

	def capaSeleccionada(self):
		capa = ''
		for layer in QgsProject.instance().mapLayers().values():
			if layer.name() == self.listaCapas.selectedItems()[0].text():
				capa = layer
				break
		self.hide()
		self.escribirDatos(capa)
		LimpiarObjetos().limpiar()

	def seleccionCambiada(self):
		try:
			self.listaCapas.selectedItems()[0]
			self.botonAceptar.setEnabled(True)
		except:
			self.botonAceptar.setEnabled(False)

	def generarNuevaCapa(self):
		capa = QgsVectorLayer("Point", "Sensores", "memory")
		proveedor = capa.dataProvider()
		proveedor.addAttributes([QgsField("id", QVariant.Int),QgsField("tipoSensor", QVariant.Int),QgsField("alarma", QVariant.Int),QgsField("bomba", QVariant.Int),QgsField("estadoB", QVariant.Int)])
		capa.updateFields()
		path = "%s/.sigrdap/capa" % os.path.expanduser('~')
		if not os.path.exists(path):
			os.makedirs(path)
		error = QgsVectorFileWriter.writeAsVectorFormat(capa,"%s/capa" % path,"UTF-8", driverName="ESRI Shapefile")
		if error[0] == QgsVectorFileWriter.NoError:
			capa = QgsVectorLayer("%s/capa.shp" % path, "Sensores", "ogr")
		self.reglas(capa)
		QgsProject.instance().addMapLayer(capa)
		self.hide()
		self.escribirDatos(capa)
		LimpiarObjetos().limpiar()

	def reglas(self,capa):
		reglas = (("Presión", "tipoSensor = 1", QgsSimpleMarkerSymbolLayerBase.Circle, False),("Flujo", "tipoSensor = 2", QgsSimpleMarkerSymbolLayerBase.Arrow, True),("Nivel", "tipoSensor = 3", QgsSimpleMarkerSymbolLayerBase.Square, False))
		simbolo = QgsMarkerSymbol() #QgsSymbol.defaultSymbol(capa.geometryType())
		simbolo.setSize(4)
		renderer = QgsRuleBasedRenderer(simbolo)
		renderer.setOrderByEnabled(True)
		root_rule = renderer.rootRule()
		#Definir la regla para las bombas
		regla = root_rule.children()[0].clone()
		regla = self.setRegla(regla, "Bomba", "tipoSensor = 1 and bomba > 0", "#FFFFFF", "#000000", 1, QgsSimpleMarkerSymbolLayerBase.Hexagon, 9)
		subregla = self.setRegla(root_rule.children()[0].clone(), "Encendida", "estadoB = 3", "#E5F7FF", "#2980B9", 1, QgsSimpleMarkerSymbolLayerBase.Hexagon, 9)
		regla.appendChild(subregla)
		subregla = self.setRegla(root_rule.children()[0].clone(), "Apagada", "estadoB < 3", "#FAEBEA", "#E74C3C", 1, QgsSimpleMarkerSymbolLayerBase.Hexagon, 9)
		regla.appendChild(subregla)
		root_rule.appendChild(regla)
		#Reglas para los tipos de sensor
		for etiqueta, expresion, forma, isArrow in reglas:
			regla = root_rule.children()[0].clone()
			regla.setLabel(etiqueta)
			regla.setFilterExpression(expresion)
			regla.symbol().setColor(QColor("#27ae60"))
			regla.symbol().symbolLayer(0).setShape(forma)
			if isArrow:
				regla.symbol().setAngle(90)
				regla.symbol().setSize(8)
			subreglas = (("Correcto","alarma = '1'","#27ae60"),("Fuera de rango (bajo)","alarma = '2'","#f1c40f"),("Fuera de rango (alto)","alarma = '3'","#e74c3c"),("Sin alarma","alarma = '0'","#2980b9"))
			reglaClon = regla.clone()
			for etiqueta, expresion, color in subreglas:
				subregla = reglaClon.clone()
				subregla.setLabel(etiqueta)
				subregla.setFilterExpression(expresion)
				subregla.symbol().setColor(QColor(color))
				regla.appendChild(subregla)
			root_rule.appendChild(regla)
		root_rule.removeChildAt(0)
		clause = QgsFeatureRequest.OrderByClause("tipoSensor")
		orderBy = QgsFeatureRequest.OrderBy([clause])
		renderer.setOrderBy(orderBy)
		capa.setRenderer(renderer)

	def setRegla(self, regla, label, rule, color1, color2, width, shape, size):
		regla.setLabel(label)
		regla.setFilterExpression(rule)
		regla.symbol().setColor(QColor(color1))
		regla.symbol().symbolLayer(0).setStrokeColor(QColor(color2))
		regla.symbol().symbolLayer(0).setStrokeWidth(width)
		regla.symbol().symbolLayer(0).setShape(shape)
		regla.symbol().setSize(size)
		return regla
