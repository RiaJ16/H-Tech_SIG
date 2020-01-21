# -*- coding: utf-8 -*-

from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QPushButton


class NewUIMethods:
    startPosition = QPoint(0, 0)

    def __init__(self, window, screenSize, parent=None):
        self.window = window
        self.screenSize = screenSize
        window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint)
        self.kraken = None
        self.botonMinimizar = None
        self.botonFullScreen = None
        self.botonMaximizar = None
        self.botonCerrar = None
        self.botonFlotante = None
        self.dialogo = None
        self.pantallaCompleta = False

    def setMovable(self, frame):
        self.kraken = frame
        frame.mousePressEvent = self.customMousePressEvent
        frame.mouseMoveEvent = self.customMouseMoveEvent
        frame.mouseDoubleClickEvent = self.customMouseDoubleClickEvent

    def setBotonCerrar(self, botonCerrar):
        self.botonCerrar = botonCerrar
        # botonCerrar.enterEvent = self.cerrarEnterEvent
        # botonCerrar.leaveEvent = self.cerrarLeaveEvent
        botonCerrar.clicked.connect(self.window.close)

    def setBotonMaximizar(self, botonMaximizar):
        self.botonMaximizar = botonMaximizar
        botonMaximizar.clicked.connect(self.maximizar)

    def setBotonMinimizar(self, botonMinimizar):
        self.botonMinimizar = botonMinimizar
        botonMinimizar.clicked.connect(self.window.showMinimized)

    def setBotonFullScreen(self, botonFullScreen):
        self.botonFullScreen = botonFullScreen
        self.dialogo = QDialog(self.window)
        self.dialogo.keyPressEvent = self.keyPressEvent
        self.dialogo.setWindowFlags(Qt.SplashScreen)
        self.dialogo.setLayout(QHBoxLayout())
        self.dialogo.setFocusPolicy(Qt.NoFocus)
        self.dialogo.setStyleSheet("background-color: #121212")
        # self.dialogo.setAttribute(Qt.WA_TranslucentBackground)
        self.dialogo.layout().setContentsMargins(0, 0, 0, 0)
        self.dialogo.closeEvent = lambda event: event.ignore()
        self.botonFlotante = QPushButton(self.dialogo)
        self.botonFlotante.setText('')
        self.botonFlotante.setStyleSheet(
            ":enabled{"
            "background-color: #3498db;"
            "border: 5px solid #121212;"
            "border-radius: 45px;"
            "padding: 15px;}"
            ":hover{"
            "background-color: #2980b9}")
        self.botonFlotante.clicked.connect(self.botonFullScreen.clicked)
        icono = QIcon(":general/icons/restorefullicon.png")
        self.botonFlotante.setIcon(icono)
        self.botonFlotante.setIconSize(QSize(50, 50))
        self.dialogo.layout().addWidget(self.botonFlotante)
        botonFullScreen.clicked.connect(self.fullScreen)

    def setWindowTitle(self, title):
        super().setWindowTitle(title)
        try:
            self.logo.setToolTip(title)
        except AttributeError:
            pass

    def customMousePressEvent(self, event):
        self.startPosition = event.pos()
        self.window.mousePressEvent(event)

    def customMouseMoveEvent(self, event):
        if not self.window.isMaximized() and not self.window.isFullScreen():
            delta = event.pos() - self.startPosition
            self.window.move(self.window.pos() + delta)
        self.window.mouseMoveEvent(event)

    def customMouseDoubleClickEvent(self, event):
        self.maximizar()
        self.window.mouseDoubleClickEvent(event)

    def cerrarEnterEvent(self, event):
        icono = QIcon(":general/icons/closeicon.png")
        self.botonCerrar.setIcon(icono)

    def cerrarLeaveEvent(self, event):
        icono = QIcon(":general/icons/closeicon-d.png")
        self.botonCerrar.setIcon(icono)

    def maximizar(self):
        if not self.pantallaCompleta:
            if self.window.isMaximized():
                self.window.showNormal()
                icono = QIcon(":general/icons/maximizeicon.png")
            else:
                self.window.showMaximized()
                icono = QIcon(":general/icons/restoreicon.png")
            self.botonMaximizar.setIcon(icono)
        else:
            print("D:")

    def fullScreen(self):
        if self.pantallaCompleta:
            self.mostrarBotonFlotante(False)
            self.window.showNormal()
            self.botonMaximizar.setEnabled(True)
            icono = QIcon(":general/icons/fullicon.png")
            iconoMaximizar = QIcon(":general/icons/maximizeicon.png")
        else:
            self.window.showFullScreen()
            self.kraken.hide()
            self.mostrarBotonFlotante()
            self.botonMaximizar.setEnabled(False)
            icono = QIcon(":general/icons/restorefullicon.png")
            iconoMaximizar = QIcon(":general/icons/restoreicon-i.png")
        self.pantallaCompleta = self.window.isFullScreen()
        self.botonFullScreen.setIcon(icono)
        self.botonMaximizar.setIcon(iconoMaximizar)

    def mostrarBotonFlotante(self, flag=True):
        if flag:
            xPos = 65
            yPos = self.screenSize.height() - 150
            self.dialogo.move(xPos, yPos)
            self.dialogo.show()
        else:
            self.dialogo.hide()
            self.kraken.show()

    def keyPressEvent(self, event):
        if event.key() != Qt.Key_Escape:
            QDialog().keyPressEvent(event)
        else:
            event.ignore()
