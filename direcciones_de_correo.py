# -*- coding: utf-8 -*-

import os
import qgis.utils
import threading

from qgis.core import Qgis

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QLineEdit, QListWidget, QPushButton

from .busy_icon import BusyIcon
from .correo import Correo
from .q_list_widget_item_indexado import QListWidgetItemIndexado
from .validacion import Validacion

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ventana_correos.ui'))

class DireccionesDeCorreo(QtWidgets.QDialog,FORM_CLASS):

	def __init__(self,online,parent=None):
		super(DireccionesDeCorreo, self).__init__(parent)
		self.setupUi(self)
		self.online = online
		self.iface = qgis.utils.iface
		self.__signals()
		self.editando = False
		self.validar()
		self.busy = BusyIcon(self.layout())
		self.busy.startAnimation()
		self.__loading(False)

	def __signals(self):
		self.botonAgregar.clicked.connect(self.agregar)
		self.botonEliminar.clicked.connect(self.eliminar)
		self.listaCorreos.itemDoubleClicked.connect(self.editar)
		self.listaCorreos.itemSelectionChanged.connect(self.seleccionCambiada)
		self.botonRedes.toggled.connect(self.cambiarTipoSubsistema)
		self.online.signalErrorConexion.connect(self.__errorConexion)
		self.online.signalCorreosConsultados.connect(self.cargarLista)

	def __errorConexion(self):
		self.setWindowTitle("Error de conexión")
		self.__habilitarBotones(False)
		error = "Conéctese a internet para hacer uso de esta aplicación"
		self.iface.messageBar().pushMessage("Error de conexión", error, level=Qgis.Critical,duration=3)
		self.adjustSize()

	def __habilitarBotones(self,flag):
		self.botonAgregar.setEnabled(flag)
		self.botonFuentes.setEnabled(flag)
		self.botonRedes.setEnabled(flag)
		self.listaCorreos.setEnabled(flag)
		self.campoCorreo.setEnabled(flag)

	def __loading(self,bandera=True):
		elementos = [self.botonAgregar]
		elementos.extend(self.findChildren(QLineEdit))
		elementos.extend(self.findChildren(QListWidget))
		for elemento in elementos:
			elemento.setEnabled(not bandera)
		self.busy.setVisible(bandera)
		self.adjustSize()

	def mostrar(self):
		if self.isVisible():
			self.hide()
		else:
			self.cambiarLista()
			self.show()

	def cambiarTipoSubsistema(self):
		if self.editando:
			self.editando = False
			self.cambiarBotones()
		self.cambiarLista()

	def cambiarLista(self):
		self.__loading()
		t1 = threading.Thread(target=self.online.consultarCorreos,args=(self.tipoSubsistema(),))
		t1.start()
		#self.cargarLista(self.tipoSubsistema())

	def tipoSubsistema(self):
		tipoSubsistema = 0
		if self.botonRedes.isChecked():
			tipoSubsistema = 1
		return tipoSubsistema
		

	def cargarLista(self):
		self.listaCorreos.clear()
		correos = self.online.getCorreos()
		#correos = self.online.consultarCorreos(tipoSubsistema)
		try:
			if correos[0].idCorreo != 0:
				self.setWindowTitle("Lista de correos")
				self.__habilitarBotones(True)
				for correo in correos:
					itemCorreo = QListWidgetItemIndexado("%s" % correo.getCorreo(),correo.getIdCorreo())
					self.listaCorreos.addItem(itemCorreo)
			else:
				self.__habilitarBotones(False)
				self.setWindowTitle("Error de autenticación")
				error = "Inicie sesión antes de ver la información"
				self.iface.messageBar().pushMessage("Error", error, level=Qgis.Critical,duration=3)
		except IndexError:
			pass
		self.__loading(False)

	def agregar(self):
		if self.validarAlEnviar(self.campoCorreo):
			item = self.listaCorreos.item(self.listaCorreos.count()-1)
			if item == None:
				correo = Correo(1,self.campoCorreo.text(),self.tipoSubsistema())
			else:
				correo = Correo(item.id()+1,self.campoCorreo.text(),self.tipoSubsistema())
			if not self.editando:
				try:
					self.online.insertarCorreo(correo)
					itemCorreo = QListWidgetItemIndexado("%s" % correo.getCorreo(),correo.getIdCorreo())
					self.listaCorreos.addItem(itemCorreo)
					self.campoCorreo.setText('')
					self.iface.messageBar().pushMessage("Aviso", "Correo agregado exitosamente", level=Qgis.Info, duration=3)
				except:
					self.iface.messageBar().pushMessage("Error", "Error al agregar el correo", level=Qgis.Critical, duration=3)
			else:
				itemId = self.listaCorreos.selectedItems()[0].id()
				try:
					correo.setIdCorreo(itemId)
					self.online.editarCorreo(correo)
					self.cambiarLista()
					self.iface.messageBar().pushMessage("Aviso", "Correo editado exitosamente", level=Qgis.Info, duration=3)
				except:
					self.iface.messageBar().pushMessage("Error", "Error al editar el correo", level=Qgis.Critical, duration=3)
				self.editando = False
				self.cambiarBotones()
		else:
			self.iface.messageBar().pushMessage("Error", "Ingrese una dirección de correo válida", level=Qgis.Critical, duration=3)

	def eliminar(self):
		if not self.editando:
			item = self.listaCorreos.selectedItems()[0]
			id = item.id()
			try:
				self.online.eliminarCorreo(id,self.tipoSubsistema())
				self.listaCorreos.takeItem(self.listaCorreos.currentRow())
				del item
				self.iface.messageBar().pushMessage("Aviso", "Correo eliminado exitosamente", level=Qgis.Info, duration=3)
			except:
				self.iface.messageBar().pushMessage("Error", "Error al eliminar el correo", level=Qgis.Critical, duration=3)
			#print self.listaCorreos.currentIndex().row()
		else:
			self.editando = False
			self.cambiarBotones()

	def editar(self):
		item = self.listaCorreos.selectedItems()[0]
		self.campoCorreo.setText(item.text())
		self.campoCorreo.setFocus()
		self.editando = True
		self.cambiarBotones()

	def seleccionCambiada(self):
		self.botonEliminar.setEnabled(True)
		try:
			self.listaCorreos.selectedItems()[0]
		except:
			self.botonEliminar.setEnabled(False)

	def cambiarBotones(self):
		if self.editando:
			self.botonAgregar.setText('EDITAR')
			self.botonEliminar.setText('CANCELAR')
		else:
			self.campoCorreo.setText('')
			self.botonAgregar.setText('AGREGAR')
			self.botonEliminar.setText('ELIMINAR')

	def validar(self):
		self.validacion = Validacion(self.sender)
		regex = "[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
		self.validacion.validarRegExp([self.campoCorreo],regex)#'[\w|]+@[\w]+\.[\w]+')

	def validarAlEnviar(self,elemento):
		if elemento.validator().validate(elemento.text(),0)[0] == 2:
			return True
		else:
			return False