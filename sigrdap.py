# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SIGRDAP
								 A QGIS plugin
 Sistema de Información Geográfica que permite realizar operaciones relacionadas con una Red de Distribución de Agua Potable
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
							  -------------------
		begin				 : 2018-05-11
		git sha				 : $Format:%H$
		copyright			 : (C) 2018 by Jair Nájera / HTech
		email				 : riaj.16.erre@gmail.com
 ***************************************************************************/

/***************************************************************************
 *																		   *
 *	 This program is free software; you can redistribute it and/or modify  *
 *	 it under the terms of the GNU General Public License as published by  *
 *	 the Free Software Foundation; either version 2 of the License, or	   *
 *	 (at your option) any later version.								   *
 *																		   *
 ***************************************************************************/
"""
import locale
import os.path
import platform

from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QApplication

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QActionGroup

from .resources import *

from .abstract_worker import *
from .administrar_grupos import AdministrarGrupos
from .alarmas import Alarmas
from .boton_nuevo import BotonNuevo
from .buscar_capa import BuscarCapa
from .click_lienzo import ClickLienzo
from .direcciones_de_correo import DireccionesDeCorreo
from .dragon.dragon import Dragon
#from .dual import Dual
from .limpiar_objetos import LimpiarObjetos
from .login import Login
from .online import Online
from .pantalla_completa import PantallaCompleta
from .tiempo_real import TiempoReal

class SIGRDAP:

	#app = QApplication.instance()
	#qss_file = open(r"C:\Program Files\QGIS 3.8\apps\qgis\resources\themes\Night Mapping\Style.qss").read()
	#app.setStyleSheet(qss_file)
	#QApplication.instance().setStyle("windowsvista")
	#QApplication.instance().setStyle("fusion")

	sistema = 0
	sistemaString = platform.system().lower()
	if sistemaString == "windows":
		sistema = 0
	elif sistemaString == "linux" or sistemaString == "linux2":
		sistema = 1
	elif sistemaString == "darwin":
		sistema = 2

	#locale.setlocale(locale.LC_ALL, 'es_MX.utf8')
	try:
		locale.setlocale(locale.LC_ALL, 'es-MX')
	except locale.Error:
		try:
			locale.setlocale(locale.LC_ALL, 'es-ES')
		except locale.Error:
			pass

	def __init__(self, iface):
		self.iface = iface

		# initialize plugin directory
		self.plugin_dir = os.path.dirname(__file__)

		# initialize locale
		locale = QSettings().value('locale/userLocale')[0:2]
		locale_path = os.path.join(
			self.plugin_dir,
			'i18n',
			'SIGRDAP_{}.qm'.format(locale))

		if os.path.exists(locale_path):
			self.translator = QTranslator()
			self.translator.load(locale_path)

			if qVersion() > '4.3.3':
				QCoreApplication.installTranslator(self.translator)

		# Declare instance attributes
		self.actions = []
		self.menu = self.tr(u'&SIGRDAP')
		# TODO: We are going to let the user set this up in a future iteration
		self.toolbar = self.iface.addToolBar(u'SIGRDAP')
		self.toolbar.setObjectName(u'SIGRDAP')

		#print "** INITIALIZING SIGRDAP"

		self.pluginIsActive = False

	def _errorConexion(self):
		self.internet = False
		error = "Conéctese a internet para hacer uso de esta aplicación"
		self.iface.messageBar().pushMessage("Error de conexión", error, level=Qgis.Critical,duration=3)

	# noinspection PyMethodMayBeStatic
	def tr(self, message):
		# noinspection PyTypeChecker,PyArgumentList,PyCallByClass
		return QCoreApplication.translate('SIGRDAP', message)

	def add_action(
		self,
		icon_path,
		text,
		callback,
		icon_path_active=None,
		enabled_flag=True,
		add_to_menu=True,
		add_to_toolbar=True,
		status_tip=None,
		whats_this=None,
		parent=None):

		icon = QIcon()
		icon.addPixmap(QPixmap(icon_path), QIcon.Normal)
		icon.addPixmap(QPixmap(icon_path), QIcon.Disabled)
		icon.addPixmap(QPixmap(icon_path_active), QIcon.Active)
		action = QAction(icon, text, parent)
		action.triggered.connect(callback)
		action.setEnabled(enabled_flag)

		if status_tip is not None:
			action.setStatusTip(status_tip)

		if whats_this is not None:
			action.setWhatsThis(whats_this)

		if add_to_toolbar:
			self.toolbar.addAction(action)

		if add_to_menu:
			self.iface.addPluginToMenu(
				self.menu,
				action)

		self.actions.append(action)

		return action

	def initGui(self):
		"""Create the menu entries and toolbar icons inside the QGIS GUI."""
		self.geometria = QApplication.instance().desktop().screenGeometry()
		self.acciones()
		self.ocultarIconos()
		self.online = Online()
		self.online.login(first=True)
		self.online.signalErrorConexion.connect(self._errorConexion)
		#self.toolbar.setIconSize(QSize(48,48))
		self.online.signalPermisos.connect(self.ocultarIconos)
		self.guiExtras()
		self.exclusivas()
		self.actions[7].setChecked(int(PantallaCompleta().isPresionado()))
		self.alarma = Alarmas()
		self.tiempoReal = TiempoReal()
		self.tiempoReal.signalActualizar.connect(self.slotActualizarTiempoReal)
		self.actualizarTiempoReal()
		self.toolbar.visibilityChanged.connect(self.aumentarIconos)
		#self.limpiar()

	def ocultarIconos(self,permiso=3):
		flag = False
		if permiso < 2:
			flag = True
		self.actions[1].setVisible(flag)
		self.actions[2].setVisible(flag)
		self.actions[3].setVisible(flag)
		self.actions[4].setVisible(flag)

	def aumentarIconos(self):
		self.toolbar.setIconSize(QSize(48,48))

	def accionMover(self):
		accion = self.iface.actionPan()
		icon = QIcon()
		icon.addPixmap(QPixmap(':sigrdap/icons/mover.png'), QIcon.Normal)
		#icon.addPixmap(QPixmap(icon_path), QIcon.Disabled)
		icon.addPixmap(QPixmap(':sigrdap/icons/mover2.png'), QIcon.Active)
		accion.setIcon(icon)
		accion.setToolTip("Navegar el mapa")
		self.toolbar.addAction(accion)

	def acciones(self):
		self.add_action(
			':sigrdap/icons/usuario.png',
			text=self.tr(u'Iniciar sesión'),
			callback=self.iniciarSesion,
			icon_path_active=':sigrdap/icons/usuario2.png',
			parent=self.iface.mainWindow())
		self.accionMover()
		self.add_action(
			':sigrdap/icons/nuevo.png',
			text=self.tr(u'Agregar sensor'),
			callback=self.run,
			icon_path_active=':sigrdap/icons/nuevo2.png',
			parent=self.iface.mainWindow())
		self.add_action(
			':sigrdap/icons/mover_s.png',
			text=self.tr(u'Mover sensor'),
			callback=self.mover,
			icon_path_active=':sigrdap/icons/mover_s2.png',
			parent=self.iface.mainWindow())
		self.actions[2].setCheckable(True)
		self.add_action(
			':sigrdap/icons/edit.png',
			text=self.tr(u'Editar sensor'),
			callback=self.editar,
			icon_path_active=':sigrdap/icons/edit2.png',
			parent=self.iface.mainWindow())
		self.actions[3].setCheckable(True)
		self.add_action(
			':sigrdap/icons/eliminar.png',
			text=self.tr(u'Eliminar sensor'),
			callback=self.eliminar,
			icon_path_active=':sigrdap/icons/eliminar2.png',
			parent=self.iface.mainWindow())
		self.actions[4].setCheckable(True)
		self.add_action(
			':sigrdap/icons/historial.png',
			text=self.tr(u'Consultar historial'),
			callback=self.historial,
			icon_path_active=':sigrdap/icons/historial2.png',
			parent=self.iface.mainWindow())
		self.actions[5].setCheckable(True)
		self.add_action(
			':sigrdap/icons/bomba2.png',
			text=self.tr(u'Consultar bombas'),
			callback=self.historialBomba,
			icon_path_active=':sigrdap/icons/bomba.png',
			enabled_flag=True,
			parent=self.iface.mainWindow())
		self.actions[6].setCheckable(True)
		#self.actions[6].setVisible(False)
		self.add_action(
			':sigrdap/icons/picture.png',
			text=self.tr(u'Administrar grupos'),
			callback=self.grupos,
			icon_path_active=':sigrdap/icons/picture2.png',
			enabled_flag=True,
			parent=self.iface.mainWindow())
		self.add_action(
			':sigrdap/icons/email.png',
			text=self.tr(u'Administrar correos electrónicos'),
			callback=self.administrarCorreos,
			icon_path_active=':sigrdap/icons/email2.png',
			enabled_flag=True,
			parent=self.iface.mainWindow())
		self.add_action(
			':sigrdap/icons/monitor.png',
			text=self.tr(u'Monitor'),
			callback=self.monitor,
			icon_path_active=':sigrdap/icons/monitor2.png',
			enabled_flag=True,
			parent=self.iface.mainWindow())
		self.add_action(
			':sigrdap/icons/fullscreen.png',
			text=self.tr(u'Pantalla completa'),
			callback=self.togglePantallaCompleta,
			icon_path_active=':sigrdap/icons/fullscreen2.png',
			enabled_flag=True,
			parent=self.iface.mainWindow())
		self.actions[10].setCheckable(True)

	def guiExtras(self):
		self.iface.mainWindow().setWindowTitle("QGIS - H-Tech SIG")
		self.iface.mainWindow().setWindowIcon(QIcon(":/sigrdap/icons/logo.png"))

	#--------------------------------------------------------------------------

	def onClosePlugin(self):
		"""Cleanup necessary items here when plugin dockwidget is closed"""

		# disconnects
		self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
		self.pluginIsActive = False

	def unload(self):
		"""Removes the plugin menu item and icon from QGIS GUI."""

		#print "** UNLOAD SIGRDAP"
		self.tiempoReal.stop()
		for action in self.actions:
			self.iface.removePluginMenu(
				self.tr(u'&SIGRDAP'),
				action)
			self.iface.removeToolBarIcon(action)
		# remove the toolbar
		del self.toolbar
		print("bye")

	#--------------------------------------------------------------------------

	def run(self):
		"""Run method that loads and starts the plugin"""

		if not self.pluginIsActive:
			self.pluginIsActive = False

			# connect to provide cleanup on closing of dockwidget
			#self.dockwidget.closingPlugin.connect(self.onClosePlugin)
			self.nuevo()

	def iniciarSesion(self):
		self.deshabilitarAcciones()
		if not hasattr(self,'login'):
			self.login = Login(self.online)
			self.login.signalLoggedOut.connect(self.ocultarIconos)
		self.login.inicializar()

	def nuevo(self):
		self.deshabilitarAcciones(1)
		if not hasattr(self,'botonNuevo'):
			self.botonNuevo = BotonNuevo(self.online)
			try:
				self.botonNuevo.signalNoCapa.connect(self.seleccionarCapa)
			except:
				pass
			#self.botonNuevo.signalCambio.connect(self.conexionZigBee.actualizarTablaDatos)
		self.botonNuevo.inicializar()

	def mover(self):
		self.deshabilitarAcciones(2)
		if self.actions[2].isChecked():
			self.clickLienzo = ClickLienzo(3,self.online)
			try:
				self.clickLienzo.signalNoCapa.connect(self.seleccionarCapa)
				self.clickLienzo.signalCambio.connect(self.conexionZigBee.actualizarTablaDatos)
			except:
				pass

	def editar(self):
		self.deshabilitarAcciones(3)
		if self.actions[3].isChecked():
			self.clickLienzo = ClickLienzo(2,self.online)
			try:
				self.clickLienzo.signalNoCapa.connect(self.seleccionarCapa)
				self.clickLienzo.signalCambio.connect(self.conexionZigBee.actualizarTablaDatos)
			except:
				pass

	def eliminar(self):
		self.deshabilitarAcciones(4)
		if self.actions[4].isChecked():
			self.clickLienzo = ClickLienzo(4,self.online)
			try:
				self.clickLienzo.signalNoCapa.connect(self.seleccionarCapa)
				self.clickLienzo.signalCambio.connect(self.conexionZigBee.actualizarTablaDatos)
			except:
				pass

	def historial(self):
		self.deshabilitarAcciones(5)
		if self.actions[5].isChecked():
			self.clickLienzo = ClickLienzo(1,self.online)
			self.clickLienzo.signalNoCapa.connect(self.seleccionarCapa)

	def historialBomba(self):
		self.deshabilitarAcciones(6)
		if self.actions[6].isChecked():
			self.clickLienzo = ClickLienzo(0,self.online)
			self.clickLienzo.signalNoCapa.connect(self.seleccionarCapa)

	def modoDual(self):
		if not hasattr(self,'dual'):
			self.dual = Dual(self.online,self.toolbar)
		if self.dual.isVisible():
			self.actions[6].setChecked(False)
			self.dual.hide()
		else:
			self.actions[6].setChecked(True)
			self.dual.show()

	def grupos(self):
		#self.deshabilitarAcciones(5)
		if hasattr(self,'administrarGrupos'):
			self.administrarGrupos = None
		self.administrarGrupos = AdministrarGrupos(self.online)
		self.administrarGrupos.inicializar()

	def administrarCorreos(self):
		if not hasattr(self,'direccionesDeCorreo'):
			self.direccionesDeCorreo = DireccionesDeCorreo(self.online)
		self.direccionesDeCorreo.mostrar()
		if self.direccionesDeCorreo.isVisible():
			self.actions[7].setChecked(True)
		else:
			self.actions[7].setChecked(False)

	def monitor(self):
		if not hasattr(self,'dragon'):
			self.dragon = Dragon(self.geometria, contexto=True)
		else:
			if self.dragon.running:
				self.dragon.showNormal()
				self.dragon.activateWindow()
			else:
				self.dragon = Dragon(self.geometria, contexto=True)

	def togglePantallaCompleta(self):
		if not hasattr(self,'pantallaCompleta'):
			self.pantallaCompleta = PantallaCompleta()
			self.pantallaCompleta.restaurar()
		if(self.actions[10].isChecked()):
			self.pantallaCompleta.guardarBarras()
			self.pantallaCompleta.ocultarBarras()
			self.pantallaCompleta.setPresionado(1)
		else:
			self.pantallaCompleta.restaurar()
			self.pantallaCompleta.setPresionado(0)
		self.toolbar.setVisible(True)

	#FUNCIÓN PARA DESHABILITAR LAS OTRAS ACCIONES CADA VEZ QUE SE ACTIVA UNA DISTINTA
	
	def deshabilitarAcciones(self,actual=0):
		if hasattr(self,'login'):
			self.login.cerrar()
			del self.login
		if hasattr(self,'clickLienzo'):
			self.clickLienzo.cerrar()
			#self.clickLienzo.signalCambio.disconnect()
			del self.clickLienzo
		if hasattr(self,'botonNuevo'):
			self.botonNuevo.cerrar()
			#self.botonNuevo.signalCambio.disconnect()
			del self.botonNuevo
		if hasattr(self,'direccionesDeCorreo'):
			self.direccionesDeCorreo.hide()
			del self.direccionesDeCorreo
		for action in self.actions:
			if action is not self.actions[10]:
			#if action is not self.actions[6] and action is not self.actions[7]:
				if action is not self.actions[actual]:
					action.setChecked(False)
		self.iface.actionPan().setChecked(False)

	def exclusivas(self):
		group = QActionGroup(self.iface.mainWindow())
		group.setExclusive(True)
		for action in self.actions:
			group.addAction(action)
		accion = self.iface.actionPan()
		group.addAction(accion)
		#group.removeAction(self.actions[6])
		group.removeAction(self.actions[10])

	def actualizarTiempoReal(self):
		start_worker(self.tiempoReal,self.iface,'Iniciado el monitoreo en tiempo real')

	def slotActualizarTiempoReal(self):
		self.alarma.login()

	def limpiar(self):
		self.limpiarObjetos = LimpiarObjetos()
		self.limpiarObjetos.limpiar()

	def seleccionarCapa(self):
		buscarCapa = BuscarCapa()
		buscarCapa.cargarLista()
'''
───────────────────────────────
───────────────████─███────────
──────────────██▒▒▒█▒▒▒█───────
─────────────██▒────────█──────
─────────██████──██─██──█──────
────────██████───██─██──█──────
────────██▒▒▒█──────────███────
────────██▒▒▒▒▒▒───▒──██████───
───────██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒███─
──────██▒▒▒▒─────▒▒▒▒▒▒▒▒▒▒▒▒█─
──────██▒▒▒───────▒▒▒▒▒▒▒█▒█▒██
───────██▒▒───────▒▒▒▒▒▒▒▒▒▒▒▒█ Yoshi reminds you: The most important thing is how you feel about yourself. YOSHIIIII!
────────██▒▒─────█▒▒▒▒▒▒▒▒▒▒▒▒█
────────███▒▒───██▒▒▒▒▒▒▒▒▒▒▒▒█
─────────███▒▒───█▒▒▒▒▒▒▒▒▒▒▒█─
────────██▀█▒▒────█▒▒▒▒▒▒▒▒██──
──────██▀██▒▒▒────█████████────
────██▀███▒▒▒▒────█▒▒██────────
█████████▒▒▒▒▒█───██──██───────
█▒▒▒▒▒▒█▒▒▒▒▒█────████▒▒█──────
█▒▒▒▒▒▒█▒▒▒▒▒▒█───███▒▒▒█──────
█▒▒▒▒▒▒█▒▒▒▒▒█────█▒▒▒▒▒█──────
██▒▒▒▒▒█▒▒▒▒▒▒█───█▒▒▒███──────
─██▒▒▒▒███████───██████────────
──██▒▒▒▒▒██─────██─────────────
───██▒▒▒██─────██──────────────
────█████─────███──────────────
────█████▄───█████▄────────────
──▄█▓▓▓▓▓█▄─█▓▓▓▓▓█▄────────────
──█▓▓▓▓▓▓▓▓██▓▓▓▓▓▓▓█───────────
──█▓▓▓▓▓▓▓▓██▓▓▓▓▓▓▓█───────────
──▀████████▀▀███████▀──────────'''