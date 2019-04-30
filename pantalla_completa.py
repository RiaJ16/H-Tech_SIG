import os
import qgis.utils

from PyQt5.QtWidgets import QToolBar, QDockWidget

class PantallaCompleta:

	def __init__(self):
		self.iface = qgis.utils.iface
		self.listaBarras = self.iface.mainWindow().findChildren(QToolBar)
		self.listaPaneles = self.iface.mainWindow().findChildren(QDockWidget)

	def leerEstado(self):
		barrasEstado = []
		panelesEstado = []
		for barra in self.listaBarras:
			barrasEstado.append(barra.isVisible())
		for panel in self.listaPaneles:
			panelesEstado.append(panel.isVisible())
		return barrasEstado,panelesEstado

	def ocultarBarras(self):
		for barra in self.listaBarras:
			barra.setVisible(False)
		for dock in self.listaPaneles:
			dock.setVisible(False)

	def restaurarBarras(self,listaEstado):
		for barra, estado in zip(self.listaBarras, listaEstado[0]):
			barra.setVisible(estado)
		for panel, estado in zip(self.listaPaneles, listaEstado[1]):
			panel.setVisible(estado)

	def guardarBarras(self):
		estado = self.leerEstado()
		barrasEstado = estado[0]
		panelesEstado = estado[1]
		path = "%s\\.sigrdap" % os.environ['HOME']
		if not os.path.exists(path):
			os.makedirs(path)
		archivo = open("%s\\barras" % path,"w")
		for barra in barrasEstado:
			archivo.write("%s\n" % barra)
		archivo.close()
		archivo = open("%s\\paneles" % path,"w")
		for panel in panelesEstado:
			archivo.write("%s\n" % panel)
		archivo.close()

	def cargarBarras(self):
		path = "%s\\.sigrdap" % os.environ['HOME']
		try:
			with open("%s\\barras" % path) as archivo:
				estadoBarras = archivo.readlines()
			estadoBarras = [x.strip() for x in estadoBarras]
		except FileNotFoundError:
			estadoBarras = []
		try:
			with open("%s\\paneles" % path) as archivo:
				estadoPaneles = archivo.readlines()
			estadoPaneles = [x.strip() for x in estadoPaneles]
		except FileNotFoundError:
			estadoPaneles = []
		return estadoBarras,estadoPaneles

	def restaurar(self):
		try:
			estado = self.cargarBarras()
			estadoBarras = estado[0]
			estadoPaneles = estado[1]
			i=0
			for barraPermanente in self.iface.mainWindow().findChildren(QToolBar):
				if estadoBarras[i] == "True":
					barraPermanente.setVisible(True)
				i+=1
			i=0
			for panelPermanente in self.iface.mainWindow().findChildren(QDockWidget):
				if estadoPaneles[i] == "True":
					panelPermanente.setVisible(True)
				i+=1
		except IndexError:
			pass

	def setPresionado(self,presionado):
		path = "%s\\.sigrdap" % os.environ['HOME']
		if not os.path.exists(path):
			os.makedirs(path)
		archivo = open("%s\\pantalla_completa" % path,"w")
		archivo.write("%s" % presionado)
		archivo.close()

	def isPresionado(self):
		path = "%s\\.sigrdap" % os.environ['HOME']
		try:
			with open("%s\\pantalla_completa" % path) as archivo:
				presionado = archivo.readline()
		except FileNotFoundError:
			presionado = 0
		return presionado