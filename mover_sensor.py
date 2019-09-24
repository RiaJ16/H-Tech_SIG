# -*- coding: UTF8 -*-

import os
import qgis.utils
import threading

from qgis.core import QgsGeometry, QgsPointXY
from qgis.gui import QgsHighlight, QgsMapToolEmitPoint

from PyQt5 import QtCore, uic
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtWidgets import QDialog, QLayout

from .busy_icon import BusyIcon
from .obtener_capa import ObtenerCapa
from .online import Online
from .validacion import Validacion


class MoverSensor(QObject):

	signalEditado = pyqtSignal()

	def __init__(self):
		QObject.__init__(self)
		self.iface = qgis.utils.iface
		self.lienzo = self.iface.mapCanvas()
		self.capaActiva = ObtenerCapa().capa()
		self.h_list = []
		self.online = Online()
		self._signals()

	def _signals(self):
		self.online.signalSensorConsultado.connect(self.consultarSensor)
		self.online.signalConsultarGrupo.connect(self.actualizarFoto)
		self.online.signalErrorConexion.connect(self._errorConexion)

	def _errorConexion(self):
		try:
			self.widget.setWindowTitle("Error de conexión")
			self.widget.labelGrupo.setText("Error de conexión")
			self.loading(False)
			self.widget.boton.setEnabled(False)
			self._mostrarOcultar(False)
			error = "Conéctese a internet para hacer uso de esta aplicación."
			self.widget.etiqueta.setText(error)
		except NameError:
			error = "Conéctese a internet para hacer uso de esta aplicación."
		self.iface.messageBar().pushMessage("Error de conexión", error, level=Qgis.Critical,duration=3)

	def _errorLogin(self):
		try:
			self.widget.setWindowTitle("Error de autenticación")
			self.widget.labelGrupo.setText("Error de autenticación")
			self.loading(False)
			self.widget.boton.setEnabled(False)
			self.__mostrarOcultar(False)
			error = "No se ha iniciado la sesión. Inicie sesión y vuelva a intentarlo."
			self.etiqueta.setText(error)
		except NameError:
			error = "No se ha iniciado la sesión. Inicie sesión y vuelva a intentarlo."
		self.iface.messageBar().pushMessage("Error", error, level=Qgis.Critical,duration=3)

	def _mostrarOcultar(self,flag):
		self.widget.labelFoto.setVisible(flag)
		self.widget.labelDireccion.setVisible(flag)
		self.widget.labelTipo.setVisible(flag)
		self.widget.adjustSize()

	def pasarObjetoGeografico(self, objetoGeografico):
		self.objetoGeografico = objetoGeografico

	def consultarSensor(self):
		try:
			sensor = self.online.getSensor()
			#self.idSensor = sensor.idSensor
			if sensor.idSensor == 0:
				self._errorLogin()
			else:
				self.widget.labelDireccion.setText("<b><font color='#2980b9'>Ubicación:</font></b> %s, %s, %s, %s" % (sensor.calle,sensor.colonia,sensor.cp,sensor.municipioTexto))
				self.widget.labelTipo.setText("<b><font color='#2980b9'>Tipo:</font></b> %s" % sensor.tipoSensorTexto)
				self.widget.labelGrupo.setText("<b>%s</b>" % sensor.grupoTexto.upper())
				t1 = threading.Thread(target=self.online.consultarGrupoPorId,args=(sensor.grupo,))
				t1.start()
		except:
			self.widget.etiqueta.setText("Este objeto no está asociado con ningún sensor.")
			self.loading(False)

	def crearBarra(self):
		if not hasattr(self, 'widget'):
			self.widget = QDialog()
			uic.loadUi(os.path.join(os.path.dirname(__file__), 'mover_sensor.ui'), self.widget)
			self.widget.textoX.textChanged.connect(self.resaltarPunto)
			self.widget.textoY.textChanged.connect(self.resaltarPunto)
			self.widget.boton.setEnabled(False)
			self.widget.boton.clicked.connect(self.editar)
			self.widget.layout().setSizeConstraint(QLayout.SetFixedSize)
			self.busy = BusyIcon(self.widget.layout())
			self.busy.startAnimation()
			self.busy.hide()
			self.widget.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		self.widget.closeEvent = self.closeEvent
		t1 = threading.Thread(target=self.online.consultarSensorPorIdFeature,args=(self.objetoGeografico.attribute('id'),))
		t1.start()
		self.loading(True)
		self.widget.setVisible(True)
		self.validacion = Validacion(self.widget.sender)
		self.validacion.validarDoble([self.widget.textoX,self.widget.textoY])
		self._obtenerCoordenadas()

	def _obtenerCoordenadas(self):
		self.guardaClick = QgsMapToolEmitPoint(self.lienzo)
		self.lienzo.setMapTool(self.guardaClick)
		self.guardaClick.canvasClicked.connect(self.onClicked)

	def onClicked(self, punto):
		self.widget.textoX.setText(str(punto.x()))
		self.widget.textoY.setText(str(punto.y()))
		self.widget.boton.setEnabled(True)
		self.resaltarPunto()

	def editar(self):
		idSensor = self.online.getSensor().idSensor
		x = self.widget.textoX.text()
		y = self.widget.textoY.text()
		self.online.actualizarCoordenadas(idSensor, x, y)
		self.moverObjetoGeografico(x, y)
		self.widget.close()

	def moverObjetoGeografico(self, x, y):
		provider = self.capaActiva.dataProvider()
		geometria = QgsGeometry.fromPointXY(QgsPointXY(float(x),float(y)))
		provider.changeGeometryValues({self.objetoGeografico.id():geometria})
		self.capaActiva.triggerRepaint()

	def resaltarPunto(self):
		try:
			x = float(self.widget.textoX.text())
			y = float(self.widget.textoY.text())
			for h in range(len(self.h_list)):
				self.h_list.pop(h)
			h = QgsHighlight(self.iface.mapCanvas(), QgsGeometry.fromPointXY(QgsPointXY(x, y)), self.capaActiva)
			h.setColor(QColor(232, 65, 24, 255))
			h.setWidth(4)
			h.setFillColor(QColor(251, 197, 49, 255))
			self.h_list.append(h)
		except ValueError:
			pass

	def actualizarFoto(self):
		try:
			filename = self.online.grupo.foto
		except:
			filename = ""
		if filename == "" or filename == None:
			filename = "%s/.sigrdap/Fotos/nodisponible.png" % os.path.expanduser('~')
		else:
			filename = "%s/.sigrdap/Fotos/%s" % (os.path.expanduser('~'),filename)
		foto = QPixmap(filename)
		if foto.isNull():
			url = filename.split('/')
			url = url[len(url)-1]
			t1 = threading.Thread(target=self.online.descargarFoto,args=(url,filename))
			t1.start()
			foto = QPixmap(filename)
		newHeight = 80
		try:
			newWidth = foto.width()*newHeight/foto.height()
		except:
			newWidth = 0
		if newWidth > 154:
			newWidth = 154
			newHeight = foto.height()*newWidth/foto.width()
		self.widget.labelFoto.setPixmap(foto.scaled(newWidth,newHeight))
		self.widget.adjustSize()
		newWidth = foto.width()
		newHeight = foto.height()
		if newWidth > 1024:
			newWidth = 1024
			newHeight = newHeight * newWidth / foto.width()
		html = "<p><img src=\'%s' width='%f' height='%f'></p>" % (filename,newWidth,newHeight)
		self.widget.labelFoto.setToolTip(html)
		self.loading(False)

	def loading(self, flag=True):
		self.busy.setVisible(flag)
		self.widget.boton.setEnabled(not flag)
		self.widget.adjustSize()

	def closeEvent(self, event):
		self.signalEditado.emit()
		self.capaActiva.removeSelection()
		for h in range(len(self.h_list)):
			self.h_list.pop(h)
		self.widget.textoX.setText('')
		self.widget.textoY.setText('')