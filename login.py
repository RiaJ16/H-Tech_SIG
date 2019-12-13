# -*- coding: utf-8 -*-

import os
import qgis.utils
import sys
import threading
import time

from qgis.core import *
from qgis.gui import *

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon, QImage, QMovie, QPixmap
from PyQt5.QtWidgets import QLayout
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QSize

from .busy_icon import BusyIcon
from .limpiar_objetos import LimpiarObjetos
from .online import Online
from .validacion import Validacion


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'login.ui'))

class Login(QtWidgets.QDialog,FORM_CLASS,QObject):

	signalConexionExitosa = pyqtSignal()
	signalLoggedOut = pyqtSignal()

	def __init__(self,online,parent=None):
		"""Constructor."""
		QObject.__init__(self)
		super(Login, self).__init__(parent)
		self.setupUi(self)
		self.iface = qgis.utils.iface
		self.online = online
		self.setWindowFlags(Qt.SplashScreen | Qt.WindowStaysOnTopHint)
		self.botonCerrar.enterEvent = self.cerrarEnterEvent
		self.botonCerrar.leaveEvent = self.cerrarLeaveEvent
		img = QImage(":Varios/icons/logosig2.png")
		#img = img.scaled(238, 74, Qt.KeepAspectRatio)
		self.logo.setPixmap(QPixmap.fromImage(img))
		self.busy = BusyIcon(self.layout(), inverted=True)
		self.busy.startAnimation()
		self.loading()
		#self.logo.setScaledContents(True);
		self.layout().setSizeConstraint(QLayout.SetFixedSize)
		self.botonLogin.clicked.connect(self.iniciarConexion)
		self.botonLogout.clicked.connect(self.desconectar)
		self.botonAceptar.clicked.connect(self.close)
		self.botonCerrar.clicked.connect(self.close)
		self.online.signalLoggedIn.connect(self.verificarConexion)
		self.online.signalLoggedOut.connect(self.logout)
		self.online.signalUsuarioConsultado.connect(self.mostrarSaludo)
		t1 = threading.Thread(target=self.online.login)
		t1.start()

	def prueba(self):
		self.online.printSession()

	def inicializar(self):
		self.show()

	def verificarConexion(self,codigo):
		#self.online.printSession()
		self.busy.hide()
		self.botonLogin.setEnabled(True)
		usuario = self.leerDatos()
		#print(codigo)
		if codigo == 6:
			error = "Conéctese a internet para hacer uso de esta aplicación."
			self.iface.messageBar().pushMessage("Error de conexión", error, level=Qgis.Critical,duration=3)
			self.loading()
			self.online.signalLoggedIn.disconnect()
			#t1 = threading.Thread(target=self.reconectar)
			#t1.start()
		elif codigo == 5:
			self.mostrarOcultar(False)
			self.signalConexionExitosa.emit()
			self.editUsuario.setText(usuario)
			#self.estado = 0?
		elif codigo == 4:
			error = "La contraseña es incorrecta."
			self.iface.messageBar().pushMessage("Error de autenticación", error, level=Qgis.Critical,duration=3)
		elif codigo == 3:
			error = "Nombre de usuario o correo electrónico no reconocido."
			self.iface.messageBar().pushMessage("Error de autenticación", error, level=Qgis.Critical,duration=3)
		elif codigo == 2:
			mensaje = "Se inició la sesión correctamente."
			self.iface.messageBar().pushMessage("Aviso", mensaje, level=Qgis.Info,duration=3)
			self.mostrarOcultar(True)
			self.signalConexionExitosa.emit()
			self.__comprobarDirectorio()
			self.guardarDatos()
			LimpiarObjetos().limpiar()
			hiloConsultarUsuario = threading.Thread(target=self.online.consultarUsuario)
			hiloConsultarUsuario.start()
		else:
			hiloConsultarUsuario = threading.Thread(target=self.online.consultarUsuario)
			hiloConsultarUsuario.start()
			self.mostrarOcultar(True)

	def __comprobarDirectorio(self):
		directory = "%s/.sigrdap/Fotos/grupos/%s" % (os.path.expanduser('~'),self.online.idSistema())
		if not os.path.exists(directory):
			os.makedirs(directory)

	def loading(self):
		elementos = [self.spacer1, self.spacer2, self.editUsuario, self.editPassword, self.botonLogin, self.botonLogout, self.botonAceptar, self.botonForgot, self.spacerF1, self.iconUser, self.iconLock]
		for elemento in elementos:
			elemento.setVisible(False)
		self.busy.show()

	def mostrarOcultar(self,bandera):
		conectado = [self.spacerC1, self.botonLogout, self.spacerC2, self.botonAceptar]
		desconectado = [self.spacer1, self.spacer2,self.editUsuario,self.editPassword,self.botonLogin, self.iconUser, self.iconLock, self.botonForgot, self.spacerF1]
		for elemento in conectado:
			elemento.setVisible(bandera)
		for elemento in desconectado:
			elemento.setVisible(not bandera)

	def iniciarConexion(self):
		self.botonLogin.setEnabled(False)
		self.busy.show()
		usuario = self.editUsuario.text()
		password = self.editPassword.text()
		t1 = threading.Thread(target=self.online.login,args=(usuario,password))
		t1.start()

	def guardarDatos(self):
		usuario = self.editUsuario.text()
		path = "{}/.sigrdap".format(os.path.expanduser('~'))
		if not os.path.exists(path):
			os.makedirs(path)
		archivo = open("{}/usuario".format(path),"w")
		archivo.write("{}\n".format(usuario))
		archivo.close()

	def leerDatos(self):
		try:
			archivo = open("{}/.sigrdap/usuario".format(os.path.expanduser('~')),"r")
			usuario = archivo.readline()[:-1]
			archivo.close()
		except:
			usuario = ''
		return usuario

	def mostrarSaludo(self, nombre, genero):
		nombreCorto = nombre.split(' ')[0]
		saludo = ''
		if genero == 1:
			saludo = "Bienvenido"
		elif genero == 2:
			saludo = "Bienvenida"
		elif genero == 3:
			saludo = "Bienvenide"
		if nombreCorto == '':
			self.labelBienvenido.setText("¡{}!".format(saludo, nombreCorto))
		else:
			self.labelBienvenido.setText("¡{}, {}!".format(saludo, nombreCorto))

	def cerrarEnterEvent(self, event):
		icono = QIcon(":General/icons/closeicon.png")
		self.botonCerrar.setIcon(icono)

	def cerrarLeaveEvent(self, event):
		icono = QIcon(":General/icons/closeicon-d.png")
		self.botonCerrar.setIcon(icono)

	def desconectar(self):
		self.botonLogout.setEnabled(False)
		self.busy.show()
		t1 = threading.Thread(target=self.online.logout)
		t1.start()

	def logout(self):
		self.botonLogout.setEnabled(True)
		self.busy.hide()
		self.mostrarOcultar(False)
		self.estado = False
		self.editPassword.setText('')
		self.labelBienvenido.setText("Inicio de sesión")
		self.editUsuario.setText(self.leerDatos())
		self.signalLoggedOut.emit()

	def reconectar(self):
		while(not self.online.login()):
			time.sleep(5)
		self.online.signalLoggedIn.connect(self.verificarConexion)
		t1 = threading.Thread(target=self.online.login)
		t1.start()

	def cerrar(self):
		self.hide()