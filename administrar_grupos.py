# -*- coding: UTF8 -*-

import os
import qgis.utils
import threading

from qgis.core import *
from qgis.gui import *

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QComboBox, QFileDialog, QPushButton

from shutil import copyfile

from .busy_icon import BusyIcon
from .grupo import Grupo
from .sensor import Sensor

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'ventana_grupos.ui'))

class AdministrarGrupos(QtWidgets.QWidget,FORM_CLASS):

	editando = False
	cambiandoFoto = False
	totalGrupos = -1
	listaTokens = []

	def __init__(self,online,parent=None):
		super(AdministrarGrupos, self).__init__(parent)
		self.setupUi(self)
		self.iface = qgis.utils.iface
		self.online = online
		self.busy = BusyIcon(self.layout())
		self.busy.startAnimation()
		self.__loading(False)
		self.__tipoSubsistemaCambiado()
		self.__signals()
		t1 = threading.Thread(target=self.online.consultarTotalGrupos)
		t1.start()
		#self.setSizeGripEnabled(False)

	def __signals(self):
		self.selectorGrupo.currentIndexChanged.connect(self.__grupoCambiado)
		self.selectorSubsistema.currentIndexChanged.connect(self.__cambiarSubsistema)
		self.botonCargar.clicked.connect(self.buscarFoto)
		self.botonGuardarCambios.clicked.connect(self.guardarCambios)
		self.botonEditar.clicked.connect(self.editar)
		self.botonAgregarGrupo.clicked.connect(self.agregarGrupo)
		self.botonRedes.toggled.connect(self.__tipoSubsistemaCambiado)
		self.online.signalSubsistemasConsultados.connect(self.__llenarListaSubsistemas)
		self.online.signalGrupos.connect(self.__llenarListaGrupos)
		self.online.signalErrorConexion.connect(self.__errorDeConexion)
		self.online.signalNotLoggedIn.connect(self.__errorLogin)
		self.online.signalTotalGrupos.connect(self.__actualizarTotalGrupos)
		self.online.signalFotoDescargada.connect(self.fotoDescargada)

	def __actualizarTotalGrupos(self,totalGrupos):
		self.totalGrupos = totalGrupos

	def __loading(self,bandera=True):
		elementos = [self.botonFuentes,self.botonRedes,self.botonEditar,self.botonAgregarGrupo]
		elementos.extend(self.findChildren(QComboBox))
		#elementos.extend(self.findChildren(QListWidget))
		for elemento in elementos:
			elemento.setEnabled(not bandera)
		if self.listaTokens == []:
			self.busy.setVisible(bandera)
		self.adjustSize()

	def inicializar(self):
		self.labelUrl.setVisible(False)
		self.editorNombre.setVisible(False)
		self.show()

	def __tipoSubsistemaCambiado(self):
		self.__loading(True)
		t1 = threading.Thread(target=self.online.consultarSubsistemasPorTipo,args=(self.tipoSubsistema(),))
		t1.start()

	def __llenarListaSubsistemas(self):
		self.selectorSubsistema.currentIndexChanged.disconnect(self.__cambiarSubsistema)
		self.selectorSubsistema.clear()
		self.selectorSubsistema.currentIndexChanged.connect(self.__cambiarSubsistema)
		self.listaSubsistemas = self.online.getSubsistemas()
		if self.listaSubsistemas != []:
			for subsistema in self.listaSubsistemas:
				self.selectorSubsistema.addItem(subsistema.nombre)
		else:
			self.selectorGrupo.clear()
			self.__loading(False)
			self.botonEditar.setEnabled(False)
			self.botonAgregarGrupo.setEnabled(False)
			self.labelUrl.setText("nosubsistemas.png")
			self.cargarFoto()

	def __cambiarSubsistema(self):
		self.__loading(True)
		#print("index: %s, subsistema %s" % (self.selectorSubsistema.currentIndex(),self.listaSubsistemas[self.selectorSubsistema.currentIndex()].idSubsistema))
		t1 = threading.Thread(target=self.online.consultarGruposPorSubsistema,args=(self.listaSubsistemas[self.selectorSubsistema.currentIndex()].idSubsistema,))
		t1.start()

	def __llenarListaGrupos(self):
		self.selectorGrupo.currentIndexChanged.disconnect(self.__grupoCambiado)
		self.selectorGrupo.clear()
		self.selectorGrupo.currentIndexChanged.connect(self.__grupoCambiado)
		self.listaGrupos = self.online.getGrupos()
		#print(self.listaGrupos)
		if self.listaGrupos != []:
			for grupo in self.listaGrupos:
				self.selectorGrupo.addItem(grupo.nombre) 
			self.__loading(False)
		else:
			self.__loading(False)
			self.labelUrl.setText("nogrupos.png")
			self.cargarFoto()
			self.botonEditar.setEnabled(False)
			self.areaDescripcion.setText('')

	def __grupoCambiado(self):
		if self.listaGrupos != []:
			idSeleccionado = self.obtenerId()
			urlFoto = self.__consultarGrupo(idSeleccionado).getFoto()
			self.labelUrl.setText(urlFoto)
			self.botonGuardarCambios.setEnabled(False)
			self.cargarCampos(idSeleccionado)
			self.areaDescripcion.setAlignment(Qt.AlignJustify)
		else:
			pass

	def __consultarGrupo(self,id):
		for grupo in self.listaGrupos:
			if int(grupo.idGrupo) == id:
				return grupo

	def tipoSubsistema(self):
		tipoSubsistema = 0
		if self.botonRedes.isChecked():
			tipoSubsistema = 1
		return tipoSubsistema

	def cargarCampos(self,id):
		grupo = self.__consultarGrupo(id)
		self.areaDescripcion.setText(grupo.descripcion)
		self.editorNombre.setText(grupo.nombre)
		self.cargarFoto()

	def buscarFoto(self):
		self.dialogo = QFileDialog()
		self.dialogo.setAcceptMode(QFileDialog.AcceptOpen)
		filename = self.dialogo.getOpenFileName(filter="Imagen(*.jpg;*.jpeg;*.png)")
		if not filename[0] == '':
			self.cambiandoFoto = True
			self.labelUrl.setText(filename[0])
			self.botonGuardarCambios.setEnabled(True)
			self.cargarFoto(False)

	def cargarFoto(self,guardado=True):
		isGrupo = True
		token = self.generarToken()
		if self.labelUrl.text() == "" or self.labelUrl.text() == None:
			self.labelUrl.setText("nodisponible.png")
		filename = self.labelUrl.text()
		if filename == 'nodisponible.png' or filename == 'nosubsistemas.png' or filename == 'nogrupos.png':
			isGrupo = False
		if guardado:
			filename = "%s\\.sigrdap/Fotos/%s" % (os.environ['HOME'],filename)
		foto = QPixmap(filename)
		if foto.isNull():
			url = filename.split('/')
			url = url[len(url)-1]
			if self.comprobarToken(token):
				self.busy.setVisible(True)
				self.listaTokens.append(token)
				t1 = threading.Thread(target=self.online.descargarFoto,args=(url,filename,token,isGrupo))
				t1.start()
			#self.online.descargarFoto(url,filename,self.generarToken(),isGrupo)
			foto = QPixmap(filename)
		baseWidth = 576
		baseHeight = 324
		newWidth = foto.width()
		newHeight = foto.height()
		#print(""+str(newWidth)+" "+str(newHeight))
		if newWidth > baseWidth:
			newWidth = baseWidth
			newHeight = newHeight * newWidth / foto.width()
		adjustedHeight = newHeight
		if newHeight > baseHeight:
			newHeight = baseHeight
			newWidth = newWidth * newHeight / adjustedHeight
		#print(""+str(newWidth)+" "+str(newHeight))
		self.labelFoto.setPixmap(foto.scaled(newWidth,newHeight))
		#self.adjustSize()

	def generarToken(self):
		a = 1
		b = 0
		c = 0
		if self.botonRedes.isChecked():
			a = 2
		b = self.selectorSubsistema.currentIndex()+1
		c = self.selectorGrupo.currentIndex()+1
		abc = '%d%03d%03d' % (a,b,c)
		token = int(abc)
		return token

	def comprobarToken(self,token):
		for item in self.listaTokens:
			if item == token:
				return False
		return True

	def fotoDescargada(self,token):
		#print(token)
		if token == self.generarToken():
			self.cargarFoto()
		try:
			self.listaTokens.remove(token)
		except ValueError:
			pass
		if self.listaTokens == []:
			self.busy.setVisible(False)
			self.adjustSize()
		
	def obtenerId(self):
		listaIdGrupos = []
		for grupo in self.listaGrupos:
			listaIdGrupos.append(int(grupo.getIdGrupo()))
		try:
			idSeleccionado = listaIdGrupos[self.selectorGrupo.currentIndex()]
		except IndexError:
			#print("Selector = %d" % self.selectorGrupo.currentIndex())
			idSeleccionado = 0
		return idSeleccionado

	def editar(self):
		self.editando = True
		self.modoEdicion()

	def modoEdicion(self,guardando=False):
		flag = self.botonAgregarGrupo.isEnabled()
		self.__habilitarBotones(not flag)
		if flag:
			self.botonEditar.setText("CANCELAR")
			self.botonEditar.setEnabled(True)
		else:
			try:
				if self.listaGrupos == []:
					self.botonEditar.setEnabled(False)
			except AttributeError:
				pass
			self.botonEditar.setText("EDITAR")
			if self.editando and not guardando:
				self.__grupoCambiado()
				self.cambiandoFoto = False
				#print(":0")
		self.selectorSubsistema.setEnabled(not flag)
		self.botonCargar.setEnabled(flag)
		self.areaDescripcion.setEnabled(flag)
		self.botonGuardarCambios.setEnabled(flag)
		if flag:
			self.selectorGrupo.setVisible(False)
			self.editorNombre.setVisible(True)
		else:
			self.editorNombre.setVisible(False)
			self.selectorGrupo.setVisible(True)

	def guardarCambios(self):
		self.modoEdicion(True)
		if self.editando:
			self.actualizarGrupo()
			#print("actualizando")
		else:
			self.nuevoGrupo()
			#print("nuevo")

	def actualizarGrupo(self):
		idSeleccionado = self.obtenerId()
		if self.cambiandoFoto:
			url = self.copiarFoto(self.labelUrl.text())
			url = self.online.actualizarFotoGrupo(url,idSeleccionado)
			url = url.split('../images/')[1]
		else:
			url = self.labelUrl.text()
		grupo = Grupo(idSeleccionado,self.listaSubsistemas[self.selectorSubsistema.currentIndex()].idSubsistema,self.editorNombre.text(),self.areaDescripcion.toPlainText()[0:450],url)
		self.online.editarGrupo(grupo)
		self.listaGrupos[self.selectorGrupo.currentIndex()] = grupo
		self.selectorGrupo.setItemText(self.selectorGrupo.currentIndex(),grupo.nombre)

	def agregarGrupo(self):
		self.editando = False
		self.modoAgregar()

	def modoAgregar(self):
		self.editorNombre.setText("")
		self.areaDescripcion.setText("")
		self.labelUrl.setText("")
		self.modoEdicion()

	def nuevoGrupo(self):
		url = self.labelUrl.text()
		if self.cambiandoFoto:
			url = self.copiarFoto(url)
		if self.totalGrupos != -1:
			self.totalGrupos = self.totalGrupos+1
			grupo = Grupo(self.totalGrupos,self.listaSubsistemas[self.selectorSubsistema.currentIndex()].idSubsistema,self.editorNombre.text(),self.areaDescripcion.toPlainText()[0:450],url)
			self.online.insertarGrupo(grupo)
			self.listaGrupos.append(grupo)
			self.selectorGrupo.addItem(self.editorNombre.text())
			self.selectorGrupo.setCurrentIndex(self.selectorGrupo.count()-1)

	def copiarFoto(self,source):
		extension = os.path.splitext(source)[1]
		#print(self.online.__leerCookies())
		destination = "%s\.sigrdap\Fotos\grupos\\%s\gpo%d%s" % (os.environ['HOME'],self.online.idSistema(),self.obtenerId(),extension)
		copyfile(source,destination)
		self.cambiandoFoto = False
		return destination

	def __habilitarBotones(self,flag):
		elementos = self.findChildren(QPushButton)
		elementos.append(self.botonAgregarGrupo)
		for elemento in elementos:
			elemento.setEnabled(flag)

	def __errorLogin(self):
		self.setWindowTitle("Error de autenticación")
		error = "Inicie sesión antes de ver la información"
		self.iface.messageBar().pushMessage("Error", error, level=Qgis.Critical,duration=3)
		self.__loading(False)
		self.__habilitarBotones(False)

	def __errorDeConexion(self):
		self.setWindowTitle("Error de conexión")
		error = "Conéctese a internet para hacer uso de esta aplicación"
		self.iface.messageBar().pushMessage("Error de conexión", error, level=Qgis.Critical,duration=3)
		self.__loading(False)
		self.__habilitarBotones(False)

	'''def closeEvent(self,event):
		print("cerrar")
		QtWidgets.QWidget.closeEvent(self,event)'''