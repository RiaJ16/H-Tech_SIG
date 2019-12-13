import ctypes
import math
import os
import threading
import time

from functools import partial

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, QSize, Qt
from PyQt5.QtGui import QCursor, QFont, QIcon, QMovie, QPixmap
from PyQt5.QtWidgets import QAbstractItemView, QAction, QGridLayout, QMainWindow, QMenu

from .busy_icon import BusyIcon
from .custom_qwidget import CustomQWidget
from .indexed_qtable_widget_item import IndexedQTableWidgetItem
from .login import Login
from .online import Online
from .programar_horarios import ProgramarHorarios
from .publisher import Publisher
try:
    from strings import strings_dragon as strings
    from ui.resources import *
except ModuleNotFoundError:
    from .strings import strings_dragon as strings
    from .ui.resources import *


class Dragon(QMainWindow):
    running = True
    bombas = []
    indicesSeleccionados = []
    pantallas = []
    signalBombasActualizadas = pyqtSignal()
    signalNuevaInformacion = pyqtSignal()
    signalNuevaBomba = pyqtSignal()
    signalSubsistemasConsultados = pyqtSignal()

    def __init__(self, contexto=False, parent=None):
        super(Dragon, self).__init__(parent)
        self.contexto = contexto
        if not contexto:
            uic.loadUi("ui/main.ui", self)
        else:
            uic.loadUi(os.path.join(os.path.dirname(__file__), 'ui/main.ui'), self)
        self.online = Online()
        self.login = Login(self.online, self.statusBar(), contexto)
        self.fixUi()
        self.busy = BusyIcon(self.statusBar())
        self.busy.startAnimation()
        self.busy.show()
        # self.login()
        #self.signalBombasActualizadas.connect(self.loadingTest)
        self.signalNuevaInformacion.connect(self.actualizarPantallas)
        self.signalNuevaBomba.connect(self.cargarListaBombas)
        # self.resized.connect(self.resizeIcons)
        self.tablaBombas.itemSelectionChanged.connect(self.definirIndicesSeleccionados)
        self._signals()
        self.show()

    def _signals(self):
        self.botonLogin.clicked.connect(self.mostrarVentanaLogin)
        self.login.signalConexionExitosa.connect(self.loggedIn)
        self.login.signalNotLoggedIn.connect(self.notLoggedIn)
        self.login.signalLoggedOut.connect(self.loggedOut)
        self.botonOcultarTodos.clicked.connect(self.tablaBombas.clearSelection)
        self.botonMostrarTodos.clicked.connect(self.tablaBombas.selectAll)
        self.botonSeleccionarUno.clicked.connect(self.seleccionarUno)
        self.botonSeleccionarVarios.clicked.connect(self.seleccionarVarios)
        self.signalSubsistemasConsultados.connect(self.subsistemasConsultados)
        self.online.signalBombasConsultadas.connect(self.slotActualizarBombas)

    def seleccionarUno(self):
        self.tablaBombas.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def seleccionarVarios(self):
        self.tablaBombas.setSelectionMode(QAbstractItemView.MultiSelection)

    def hiloActualizar(self):
        hiloActualizarBombas = threading.Thread(target=self.loopActualizarBombas, name="Hilo actualizar bombas")
        hiloActualizarBombas.start()

    def mostrarVentanaLogin(self):
        self.login.inicializar()

    def loggedIn(self):
        self.botonLogin.setText("Cerrar sesión")
        self.running = True
        self.cargarListaSubsistemas()

    def notLoggedIn(self):
        self.busy.hide()
        self.botonLogin.setText("Iniciar sesión")

    def loggedOut(self):
        self.notLoggedIn()
        self.running = False
        try:
            self.selectorSubsistema.currentIndexChanged.disconnect(self.subsistemaCambiado)
        except:
            pass
        self._reiniciarSelector(self.selectorSubsistema)
        self.subsistemas = []
        self._reiniciarTabla(self.tablaBombas)
        self.bombas = []
        self.cargarPantallas()

    def fixUi(self):
        self.tablaBombas.setFocusPolicy(Qt.NoFocus)
        icon = QIcon()
        icon.addPixmap(QPixmap(':/main/logored.png'))
        action = QAction(QIcon(), 'test', None)
        # self.toolBar.addAction(action)
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.scrollArea.setLayout(layout)
        # self.setWindowFlags(Qt.FramelessWindowHint)

    def cargarListaSubsistemas(self):
        self.busy.show()
        t1 = threading.Thread(target=self.consultarSubsistemas, name="Hilo consultar subsistemas")
        t1.start()

    def consultarSubsistemas(self):  # SLOT
        self.subsistemas = self.online.consultarSubsistemasBombas()
        self.signalSubsistemasConsultados.emit()
        self.selectorSubsistema.currentIndexChanged.connect(self.subsistemaCambiado)
        self.hiloActualizar()

    def subsistemasConsultados(self):
        self.busy.hide()
        self._reiniciarSelector(self.selectorSubsistema)
        for subsistema in self.subsistemas:
            self.selectorSubsistema.addItem(subsistema.nombre)

    @staticmethod
    def _reiniciarSelector(selector):
        while not selector.count() == 0:
            selector.removeItem(selector.count() - 1)

    def cargarListaBombas(self):
        bombas = self.bombas
        self._reiniciarTabla(self.tablaBombas)
        # self.tablaBombas.setCursor(Qt.PointingHandCursor)
        for bomba in bombas:
            self.tablaBombas.insertRow(self.tablaBombas.rowCount())
            item = IndexedQTableWidgetItem(bomba.getNombre.upper(), bomba.getIdGrupo)
            self.tablaBombas.setItem(self.tablaBombas.rowCount() - 1, 0, item)
        if self.tablaBombas.rowCount() > 0:
            self.tablaBombas.selectAll()

    def definirIndicesSeleccionados(self):
        if self.tablaBombas.selectedItems():
            self.indicesSeleccionados = []
            for item in self.tablaBombas.selectedItems():
                self.indicesSeleccionados.append(item.row())
        self.cargarPantallas()

    def cargarPantallas(self):
        bombas = []
        for row in range(0, self.tablaBombas.rowCount()):
            if self.tablaBombas.item(row, 0).isSelected():
                bombas.append(self.bombas[row])
        '''for indice in self.indicesSeleccionados:
            bombas.append(self.bombas[indice])'''
        layout = self.scrollArea.layout()
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()
        total = len(bombas)
        columns = self._getColumns(total)
        rows = math.ceil(total / columns)
        col = 0
        row = 0
        for bomba in bombas:
            pantalla = CustomQWidget()
            pantalla.signalDibujado.connect(partial(self.slotResizeIcons, pantalla))
            if not self.contexto:
                uic.loadUi("ui/pantalla.ui", pantalla)
            else:
                uic.loadUi(os.path.join(os.path.dirname(__file__), "ui/pantalla.ui"), pantalla)
            pantalla.setProperty("state", "pantalla")
            pantalla.labelEstado.setVisible(False)
            # pantalla.imagenBomba.setPixmap(pantalla.imagenBomba.pixmap().scaledToHeight(250))
            # pantalla.imagenBomba.setMovie(QMovie(":/images/images/bomba-animated.gif"))
            self.actualizarEstadoPantalla(pantalla, bomba.getEstado)
            pantalla.datoPresion.setText(bomba.getPresion)
            pantalla.datoFlujo.setText(bomba.getFlujo)
            pantalla.datoVoltaje1.setText(bomba.getVoltaje1)
            pantalla.datoVoltaje2.setText(bomba.getVoltaje2)
            pantalla.datoVoltaje3.setText(bomba.getVoltaje3)
            pantalla.datoCorriente1.setText(bomba.getCorriente1)
            pantalla.datoCorriente2.setText(bomba.getCorriente2)
            pantalla.datoCorriente3.setText(bomba.getCorriente3)
            elementos = [(bomba.getFase1, pantalla.iconFase1, pantalla.iconFase1Off)]
            elementos.append((bomba.getFase2, pantalla.iconFase2, pantalla.iconFase2Off))
            elementos.append((bomba.getFase3, pantalla.iconFase3, pantalla.iconFase3Off))
            for dato, iconoOn, iconoOff in elementos:
                if dato == 1:
                    iconoOn.setVisible(True)
                    iconoOff.setVisible(False)
                else:
                    iconoOn.setVisible(False)
                    iconoOff.setVisible(True)
            pantalla.interruptor.clicked.connect(partial(self.cambiarEstado, pantalla, bomba))
            pantalla.opciones.clicked.connect(partial(self.mostrarMenu, bomba))
            pantalla.modo.clicked.connect(partial(self.cambiarModo, bomba))
            pantalla.labelId.setText(str(bomba.getNombre))
            pantalla.labelEstado.setText('')
            pantalla.labelEstado.setText(str(bomba.getEstado))
            # pantalla.labelId.setText(str(bomba.getIdGrupo))
            pantalla.conectadoOn.setVisible(False)
            pantalla.conectadoOff.setVisible(False)
            if bomba.getModoOperacion == 0:
                icon = QIcon()
                icon.addPixmap(QPixmap(':/icons/icons/icon_manual.png'))
                pantalla.modo.setIcon(icon)
            elif bomba.getModoOperacion == 1:
                icon = QIcon()
                icon.addPixmap(QPixmap(':/icons/icons/icon_automatico.png'))
            self.revisarConectado(bomba, pantalla)
            layout.addWidget(pantalla, row, col)
            if col < columns - 1:
                col += 1
            else:
                col = 0
                row += 1
        self.resizeAllIcons()

    def revisarConectado(self, bomba, pantalla):
        conectado = bomba.getConectado
        if bomba.getIdCoordinador > 0:
            coordinador = bomba.getCoordinador
            conectado = coordinador.getConectado
        if conectado > 0:
            pantalla.labelId.setEnabled(True)
            pantalla.conectadoOn.setVisible(True)
            pantalla.conectadoOff.setVisible(False)
        else:
            pantalla.labelId.setEnabled(False)
            pantalla.conectadoOn.setVisible(False)
            pantalla.conectadoOff.setVisible(True)

    def slotResizeIcons(self, pantalla):
        self.resizeIcons(pantalla)
        pantalla.disconnect()

    def resizeAllIcons(self):
        layout = self.scrollArea.layout()
        for i in range(0, layout.count()):
            pantalla = layout.itemAt(i).widget()
            try:
                self.resizeIcons(pantalla)
            except AttributeError:
                pass

    def resizeIcons(self, pantalla):
        iconUrls = (':/icons/icons/presion.png', ':/icons/icons/flujo.png', ':/icons/icons/voltaje.png',
                    ':/icons/icons/corriente.png')
        labels = (pantalla.iconPresion, pantalla.iconFlujo, pantalla.iconVoltaje, pantalla.iconCorriente)
        for iconUrl, label in zip(iconUrls, labels):
            height = int(label.size().height())
            width = int(label.size().width())
            icon = QPixmap(iconUrl)
            if height < width:
                label.setPixmap(icon.scaledToHeight(height, Qt.SmoothTransformation))
            else:
                label.setPixmap(icon.scaledToWidth(width, Qt.SmoothTransformation))
        iconUrls = (':/icons/icons/ledon.png', ':/icons/icons/ledon.png',
                    ':/icons/icons/ledon.png', ':/icons/icons/ledoff.png', ':/icons/icons/ledoff.png',
                    ':/icons/icons/ledoff.png')
        labels = (
            pantalla.iconFase1, pantalla.iconFase2, pantalla.iconFase3, pantalla.iconFase1Off, pantalla.iconFase2Off,
            pantalla.iconFase3Off)
        for iconUrl, label in zip(iconUrls, labels):
            height = int(label.size().height())
            icon = QPixmap(iconUrl)
            label.setPixmap(icon.scaledToHeight(height * .5, Qt.SmoothTransformation))
        # iconBomba = QPixmap(':/images/images/bomba-off.png')
        # pantalla.imagenBomba.setPixmap(iconBomba.scaled(pantalla.imagenBomba.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        estado = int(pantalla.labelEstado.text())
        if estado == 0 or estado == 1:
            iconBomba = QPixmap(':/images/images/bomba-off.png')
            pantalla.imagenBomba.setPixmap(
                iconBomba.scaled(pantalla.imagenBomba.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        elif estado == 2 or estado == 3:
            self.bombaEncendida(pantalla)
        firstLabels = (pantalla.datoPresion, pantalla.datoFlujo)
        labels = (pantalla.datoVoltaje1, pantalla.datoVoltaje2, pantalla.datoVoltaje3, pantalla.datoCorriente1,
                  pantalla.datoCorriente2, pantalla.datoCorriente3)
        fontSizeFirst = int(labels[0].size().height() / 1.5)
        fontSize = int(labels[0].size().height() / 4.5)
        screenSize = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
        if screenSize < (1536, 864):
            fuente = 9
            maxFuente = 18
        else:
            fuente = 11
            maxFuente = 28
        if fontSize < fuente:
            fontSize = fuente
        if fontSizeFirst < fuente:
            fontSizeFirst = fuente
        if fontSize > maxFuente:
            fontSize = maxFuente
        if fontSizeFirst > maxFuente:
            fontSizeFirst = maxFuente
        for label in labels:
            label.setFont(QFont('Verdana', fontSize, QFont.Medium))
        for label in firstLabels:
            label.setFont(QFont('Verdana', fontSizeFirst, QFont.Medium))
        labels = (
            pantalla.uniPresion, pantalla.uniFlujo, pantalla.uniVoltaje1, pantalla.uniVoltaje2, pantalla.uniVoltaje3,
            pantalla.uniCorriente1, pantalla.uniCorriente2, pantalla.uniCorriente3)
        for label in labels:
            label.setFont(QFont('Verdana', fontSize / 1.5))
        labels = (pantalla.labelF1, pantalla.labelF2, pantalla.labelF3)
        for label in labels:
            label.setFont(QFont('Verdana', fontSize / 1.5, QFont.Bold))

    def actualizarPantallas(self):
        layout = self.scrollArea.layout()
        for i in range(0, layout.count()):
            pantalla = layout.itemAt(i).widget()
            try:
                bomba = self.bombas[self.indicesSeleccionados[i]]
            except IndexError:
                break
            pantalla.datoPresion.setText(bomba.getPresion)
            pantalla.datoFlujo.setText(bomba.getFlujo)
            pantalla.datoVoltaje1.setText(bomba.getVoltaje1)
            pantalla.datoVoltaje2.setText(bomba.getVoltaje2)
            pantalla.datoVoltaje3.setText(bomba.getVoltaje3)
            pantalla.datoCorriente1.setText(bomba.getCorriente1)
            pantalla.datoCorriente2.setText(bomba.getCorriente2)
            pantalla.datoCorriente3.setText(bomba.getCorriente3)
            self.revisarConectado(bomba, pantalla)
            elementos = [(bomba.getFase1, pantalla.iconFase1, pantalla.iconFase1Off),
                         (bomba.getFase2, pantalla.iconFase2, pantalla.iconFase2Off),
                         (bomba.getFase3, pantalla.iconFase3, pantalla.iconFase3Off)]
            for dato, iconoOn, iconoOff in elementos:
                if dato == 1:
                    iconoOn.setVisible(True)
                    iconoOff.setVisible(False)
                else:
                    iconoOn.setVisible(False)
                    iconoOff.setVisible(True)
            # pantalla.labelNombre.setText(str(bomba.getNombre))
            try:
                pantalla.interruptor.clicked.disconnect()
            except:
                pass
            try:
                pantalla.modo.clicked.disconnect()
            except:
                pass
            if bomba.getModoOperacion == 0:
                icon = QIcon()
                icon.addPixmap(QPixmap(':/icons/icons/icon_manual.png'))
                pantalla.modo.setIcon(icon)
            elif bomba.getModoOperacion == 1:
                icon = QIcon()
                icon.addPixmap(QPixmap(':/icons/icons/icon_automatico.png'))
                pantalla.modo.setIcon(icon)
            pantalla.interruptor.clicked.connect(partial(self.cambiarEstado, pantalla, bomba))
            #pantalla.modo.clicked.connect(partial(self.cambiarModo, bomba))
            self.actualizarEstadoPantalla(pantalla, bomba.getEstado)

    def actualizarEstadoPantalla(self, pantalla, estado):
        pantalla.labelEstado.setText(str(estado))
        if estado == 0:
            pantalla.interruptor.setEnabled(True)
            icon = QIcon()
            icon.addPixmap(QPixmap(':/buttons/icons/icon_off.png'))
            pantalla.interruptor.setIcon(icon)
            pantalla.barraEstado.setProperty("state", "off")
            pantalla.interruptor.setProperty("state", "off")
            pantalla.opciones.setProperty("state", "off")
            pantalla.modo.setProperty("state", "off")
            iconBomba = QPixmap(':/images/images/bomba-off.png')
            size = pantalla.imagenBomba.size()
            pantalla.imagenBomba.setPixmap(iconBomba.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        elif estado == 1:
            # pantalla.interruptor.setEnabled(False)
            icon = QIcon()
            icon.addPixmap(QPixmap(':/buttons/icons/icon_off.png'))
            pantalla.barraEstado.setProperty("state", "turning off")
            iconBomba = QPixmap(':/images/images/bomba-off.png')
            size = pantalla.imagenBomba.size()
            pantalla.imagenBomba.setPixmap(iconBomba.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        elif estado == 2:
            # pantalla.interruptor.setEnabled(False)
            icon = QIcon()
            icon.addPixmap(QPixmap(':/buttons/icons/icon_on.png'))
            pantalla.barraEstado.setProperty("state", "turning on")
            self.bombaEncendida(pantalla)
        elif estado == 3:
            pantalla.interruptor.setEnabled(True)
            icon = QIcon()
            icon.addPixmap(QPixmap(':/buttons/icons/icon_on.png'))
            pantalla.interruptor.setIcon(icon)
            pantalla.barraEstado.setProperty("state", "on")
            pantalla.interruptor.setProperty("state", "on")
            pantalla.opciones.setProperty("state", "on")
            pantalla.modo.setProperty("state", "on")
            self.bombaEncendida(pantalla)
        pantalla.barraEstado.setStyle(self.style())
        pantalla.interruptor.setStyle(self.style())
        pantalla.opciones.setStyle(self.style())

    @staticmethod
    def _getColumns(total):
        for i in range(1, total):
            division = total / i
            if i >= division:
                return i
        return 1

    def _reiniciarTabla(self, tabla):
        try:
            self.tablaBombas.itemSelectionChanged.disconnect(self.definirIndicesSeleccionados)
        except:
            pass
        while not tabla.rowCount() == 0:
            tabla.removeRow(tabla.rowCount() - 1)
        self.tablaBombas.itemSelectionChanged.connect(self.definirIndicesSeleccionados)

    def cambiarEstado(self, pantalla, bomba):
        flagCoordinador = 1
        if bomba.getIdCoordinador == 0:
            flagCoordinador = 0
            password = self.online.consultarPasswordIoT(bomba.getIdDispositivo, 0)
        if flagCoordinador:
            coordinador = self.online.consultarCoordinador(bomba.getIdCoordinador)
            password = self.online.consultarPasswordIoT(coordinador.getIdDispositivo, 1)
        if self.comprobarPassword(password):
            if flagCoordinador:
                topic = "/sensores/%s" % coordinador.getIdDispositivo
            else:
                topic = "/sensores/%s" % bomba.getIdDispositivo
            cadena = ''
            if bomba.getEstado == 0:
                pantalla.barraEstado.setProperty("state", "turning on")
                if flagCoordinador:
                    cadena = "{\"Tipo\":\"Config\",\"Cadena\":\"WB1_%s\"}" % bomba.getIdDispositivo
                else:
                    cadena = "{\"Tipo\":\"Config\",\"Cadena\":\"WB1\"}"
                # self.online.actualizarEstadoBomba(bomba.getIdGrupo, 2)
                self.statusBar().showMessage(strings.general[3], 7000)
            elif bomba.getEstado == 3:
                pantalla.barraEstado.setProperty("state", "turning off")
                if flagCoordinador:
                    cadena = "{\"Tipo\":\"Config\",\"Cadena\":\"WB0_%s\"}" % bomba.getIdDispositivo
                else:
                    cadena = "{\"Tipo\":\"Config\",\"Cadena\":\"WB0\"}"
                # self.online.actualizarEstadoBomba(bomba.getIdGrupo, 1)
                self.statusBar().showMessage(strings.general[4], 7000)
            password = password[0]['password']
            #print(topic, cadena)
            Publisher().publicar(topic, cadena, password)

            pantalla.barraEstado.setStyle(self.style())
            if bomba.getEstado == 0:
                icon = QIcon()
                icon.addPixmap(QPixmap(':/buttons/icons/icon_on.png'))
                pantalla.interruptor.setIcon(icon)
            elif bomba.getEstado == 3:
                icon = QIcon()
                icon.addPixmap(QPixmap(':/buttons/icons/icon_off.png'))
                pantalla.interruptor.setIcon(icon)
            pantalla.interruptor.setEnabled(False)

    @staticmethod
    def bombaEncendida(pantalla):
        movie = QMovie(":/images/images/bomba-animated.gif")
        labelSize = pantalla.imagenBomba.size()
        ORIGINAL_WIDTH = 1412
        ORIGINAL_HEIGHT = 1080
        width = labelSize.width()
        height = labelSize.height()
        if labelSize.height() > labelSize.width():
            width = labelSize.width()
            height = width * ORIGINAL_HEIGHT / ORIGINAL_WIDTH
        else:
            height = labelSize.height()
            width = height * ORIGINAL_WIDTH / ORIGINAL_HEIGHT
        size = QSize(width, height)
        movie.setScaledSize(size)
        movie.setCacheMode(1)
        pantalla.imagenBomba.setMovie(movie)
        movie.start()

    def loopActualizarBombas(self):
        while self.running:
            try:
                self.actualizarBombas()
                self.signalBombasActualizadas.emit()
                # print("actualizaado")
                for i in range(0, 5):
                    if self.running:
                        time.sleep(1)
            except TypeError:
                # print("holi")
                pass

    def subsistemaCambiado(self):
        self.busy.show()
        self.actualizarBombas()
        # self.cargarListaBombas()
        # self.cargarPantallas()

    def actualizarBombas(self):
        try:
            idSubsistema = int(self.subsistemas[self.selectorSubsistema.currentIndex()].idSubsistema)
        except IndexError:
            idSubsistema = -1
        t1 = threading.Thread(target=self.online.consultarBombasPorSubsistema, args=(idSubsistema,),
                              name="Hilo consultar bombas por subsistema")
        t1.start()

    def slotActualizarBombas(self):
        bombas = self.online.getBombas
        i = 0
        cambio = False
        if not (len(bombas) == len(self.bombas)):
            self.bombas = bombas
            self.signalNuevaBomba.emit()
        for bomba in bombas:
            try:
                if not (bomba == self.bombas[i]):
                    # print("cambió")
                    cambio = True
                    break
            except IndexError:
                pass
            i += 1
        self.bombas = bombas
        if cambio:
            self.signalNuevaInformacion.emit()
        self.busy.hide()

    def comprobarPassword(self, password):
        if password == 1:
            self.statusBar().showMessage(strings.general[1], 7000)
            return False
        elif password == 2:
            self.statusBar().showMessage(strings.general[2], 7000)
            return False
        return True

    def programarHorarios(self, bomba):
        publisher = Publisher()
        ProgramarHorarios(bomba, publisher, self.online, self.contexto)

    def mostrarMenu(self, bomba):
        menu = QMenu()
        menu.setStyleSheet(
            "QMenu{background-color: black; color: white; font-family: Verdana; font-size: 11pt;}"
            "QMenu:item:active:selected{background-color: #444444;}")
        accionHorarios = QAction("Programar horarios", menu)
        icon = QIcon()
        icon.addPixmap(QPixmap(':/icons/icons/datetime.png'))
        accionHorarios.setIcon(icon)
        accionHorarios.triggered.connect(partial(self.programarHorarios, bomba))
        menu.addAction(accionHorarios)
        menu.exec(QCursor.pos())

    def cambiarModo(self, bomba):
        self.online.signalPassword.connect(partial(self.cambiarModoSlot, bomba))
        if bomba.getIdCoordinador == 0:
            self.online.consultarPasswordIoT(bomba.getIdDispositivo, 0, True)
        else:
            self.online.consultarPasswordIoT(bomba.getCoordinador.getIdDispositivo, 1, True)

    def cambiarModoSlot(self, bomba, password):
        try:
            self.comprobarPassword(int(password))
        except ValueError:
            if bomba.getIdCoordinador == 0:
                topic = "/sensores/%s" % bomba.getIdDispositivo
            else:
                topic = "/sensores/%s" % bomba.getCoordinador.getIdDispositivo
            cadena = '{"Tipo":"Config","Cadena":"Wq0"}'
            if bomba.getModoOperacion == 0:
                cadena = '{"Tipo":"Config","Cadena":"Wq1"}'
            Publisher().publicar(topic, cadena, password)
        self.online.signalPassword.disconnect()

    def resizeEvent(self, event):
        toReturn = super().resizeEvent(event)
        self.resizeAllIcons()
        return toReturn

    def contextMenuEvent(self, event):
        toReturn = super().contextMenuEvent(event)
        return toReturn

    def closeEvent(self, event):
        self.running = False
        return super().closeEvent(event)
