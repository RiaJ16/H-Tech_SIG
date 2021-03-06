# -*- coding: utf-8 -*-

import os
import threading
import time

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QImage, QMovie
from PyQt5.QtWidgets import QLayout
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QSize

from .busy_icon import BusyIcon
from .q_dialog_next import QDialogNext
try:
    from strings import strings_login as strings
    from ui.resources import *
except ModuleNotFoundError:
    from .strings import strings_login as strings
    from .ui.resources import *


class Login(QDialogNext):

    signalConexionExitosa = pyqtSignal()
    signalLoggedOut = pyqtSignal()
    signalNotLoggedIn = pyqtSignal()

    def __init__(self, online, statusBar, contexto = False, parent=None):
        """Constructor."""
        QObject.__init__(self)
        super(Login, self).__init__(parent)
        if not contexto:
            uic.loadUi("ui/login.ui", self)
        else:
            uic.loadUi(os.path.join(os.path.dirname(__file__), 'ui/login.ui'), self)
        super().setMovable(self.kraken)
        super().setBotonCerrar(self.botonCerrar)
        self.online = online
        self.statusBar = statusBar
        #self.setupUi(self)
        #img = QImage(":/images/images/H-Tech Monitor.png")
        #img = img.scaled(475, 148, Qt.KeepAspectRatio)
        #self.logo.setPixmap(QPixmap.fromImage(img))
        self.busy = BusyIcon(self.layout())
        self.busy.startAnimation()
        self.loading()
        self._signals()
        self.layout().setSizeConstraint(QLayout.SetFixedSize)
        t1 = threading.Thread(target=self.online.login)
        t1.start()

    def _signals(self):
        self.botonLogin.clicked.connect(self.iniciarConexion)
        self.botonLogout.clicked.connect(self.desconectar)
        self.botonAceptar.clicked.connect(self.close)
        self.online.signalLoggedIn.connect(self.verificarConexion)
        self.online.signalLoggedOut.connect(self.logout)
        self.online.signalErrorConexion.connect(self.errorConexion)
        self.online.signalUsuarioConsultado.connect(self.mostrarSaludo)

    def inicializar(self):
        self.show()
        self.activateWindow()

    def verificarConexion(self, codigo):
        self.busy.hide()
        self.botonLogin.setEnabled(True)
        usuario = self.leerDatos()
        #print(codigo)
        if codigo == 6:
            self.loading()
            self.online.signalLoggedIn.disconnect()
        elif codigo == 5:
            self.mostrarOcultar(False)
            self.editUsuario.setText(usuario)
            self.signalNotLoggedIn.emit()
        elif codigo == 4:
            pass
        elif codigo == 3:
            pass
        elif codigo == 2:
            self.mostrarOcultar(True)
            self.signalConexionExitosa.emit()
        elif codigo == 1:
            self.signalConexionExitosa.emit()
            self.mostrarOcultar(True)
        elif codigo == 0:
            self.signalConexionExitosa.emit()
            self.mostrarOcultar(True)
        if codigo == 2 or codigo == 1 or codigo == 0:
            hiloConsultarUsuario = threading.Thread(target=self.online.consultarUsuario)
            hiloConsultarUsuario.start()
        try:
            self.statusBar.showMessage(strings.general[codigo], 5000)
        except KeyError:
            pass

    def loading(self):
        elementos = [self.spacer1, self.spacer2, self.editUsuario, self.editPassword, self.botonLogin, self.botonLogout, self.botonAceptar, self.botonForgot, self.spacerF1, self.iconUser, self.iconLock]
        for elemento in elementos:
            elemento.setVisible(False)
        self.adjustSize()
        self.adjustSize()

    # self.busy.show()

    def mostrarOcultar(self, bandera):
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
        t1 = threading.Thread(target=self.online.login, args=(usuario, password))
        t1.start()

    def guardarDatos(self):
        usuario = self.editUsuario.text()
        path = '%s/.htech_monitor/' % os.path.expanduser('~')
        if not os.path.exists(path):
            os.makedirs(path)
        archivo = open("{}/usuario".format(path), "w")
        archivo.write("{}\n".format(usuario))
        archivo.close()

    def leerDatos(self):
        try:
            archivo = open('%s/.htech_monitor/' % os.path.expanduser('~'), "r")
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
            saludo = "Bienvenid@"
        if nombreCorto == '':
            self.labelBienvenido.setText("¡{}!".format(saludo, nombreCorto))
        else:
            self.labelBienvenido.setText("¡{}, {}!".format(saludo, nombreCorto))

    def desconectar(self):
        self.botonLogout.setEnabled(False)
        # self.busy.show()
        t1 = threading.Thread(target=self.online.logout)
        t1.start()

    def logout(self):
        self.botonLogout.setEnabled(True)
        # self.busy.hide()
        self.mostrarOcultar(False)
        self.estado = False
        self.editPassword.setText('')
        self.labelBienvenido.setText("Inicio de sesión")
        self.editUsuario.setText(self.leerDatos())
        self.signalLoggedOut.emit()

    def errorConexion(self):
        self.busy.setVisible(False)
        self.statusBar.showMessage(strings.general[6])
        t1 = threading.Thread(target=self.reconectar)
        t1.start()

    def reconectar(self):
        time.sleep(5)
        self.online.login()

    def cerrar(self):
        self.hide()
