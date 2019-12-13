# -*- coding: UTF8 -*-

import shutil
import json
import os
import pickle
import requests

from requests.exceptions import ConnectionError
from uuid import getnode as get_mac

from PyQt5.QtCore import QObject, pyqtSignal

from .bomba import Bomba
from .coordinador import Coordinador
from .horario import Horario
from .subsistema import Subsistema


class Online(QObject):
    signalErrorConexion = pyqtSignal()
    signalLoggedIn = pyqtSignal(int)
    signalLoggedOut = pyqtSignal(int)
    signalBombasConsultadas = pyqtSignal()
    signalPassword = pyqtSignal(str)

    CONSULTAR_GRUPOS = 6
    CONSULTAR_PASSWORD_IOT = 26
    CONSULTAR_COORDINADOR = 27
    CONSULTAR_BOMBAS_POR_SUBSISTEMA = 101
    CONSULTAR_SUBSISTEMAS_BOMBAS = 102
    ACTUALIZAR_ESTADO_BOMBA = 103
    CONSULTAR_HORARIOS = 104

    URL = 'https://webservice.htech.mx'
    TIMEOUT = 10

    def login(self, usuario="", password="", sendSignal=True):
        androidToken = "B%d" % get_mac()
        sesion = self.__leerSesion()
        try:
            if usuario == '' and password == '':
                r = sesion.post('%s/login.php' % self.URL, timeout=5)
            else:
                r = sesion.post('%s/login.php' % self.URL,
                                data={'usuario': usuario, 'password': password, 'token': androidToken},
                                timeout=self.TIMEOUT)
            self.__guardarSesion(sesion)
            sesion.close()
            if sendSignal:
                try:
                    self.signalLoggedIn.emit(int(r.text))
                except ValueError:
                    self.signalErrorConexion.emit()
            if r.text == '5':
                return False
            else:
                return True
        except ConnectionError:
            if sendSignal:
                # self.signalLoggedIn.emit(6)
                self.signalErrorConexion.emit()
            return False
        except requests.exceptions.ReadTimeout:
            self.signalErrorConexion.emit()
            return False

    def logout(self):
        sesion = self.__leerSesion()
        try:
            r = sesion.post('%s/logout.php' % self.URL, timeout=self.TIMEOUT)
            sesion.close()
            self.__guardarSesion(sesion)
            self.signalLoggedOut.emit(0)
            if hasattr(self, '_idSistema'):
                del self._idSistema
        except ConnectionError:
            self.signalLoggedOut.emit(1)

    def __guardarSesion(self, sesion):
        path = '%s\\.htech_monitor\\' % os.path.expanduser('~')
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            with open('%s\\sesion' % path, 'wb') as f:
                pickle.dump(sesion, f)
        except FileNotFoundError:
            print("error")

    def __leerSesion(self):
        sesion = requests.session()
        try:
            with open('%s\\.htech_monitor\\sesion' % os.path.expanduser('~'), 'rb') as f:
                sesion = pickle.load(f)
        except FileNotFoundError:
            pass
        return sesion

    def consultar(self, args, seed=False):
        try:
            sesion = self.__leerSesion()
            r = sesion.post('%s/consultar.php' % self.URL, data=args, timeout=self.TIMEOUT)
            sesion.close()
            if r.text == '0' and not seed:
                self.login(sendSignal=False)
                return self.consultar(args, True)
            else:
                jsondoc = r.json()
                if jsondoc == 0:
                    jsondoc = [jsondoc]
                return jsondoc
        except ConnectionError:
            self.signalErrorConexion.emit()
            return []
        except requests.exceptions.ReadTimeout:
            self.signalErrorConexion.emit()
            return []

    def consultarBombasPorSubsistema(self, idSubsistema):
        args = {'opcion': self.CONSULTAR_BOMBAS_POR_SUBSISTEMA, 'id_subsistema': idSubsistema}
        jsondoc = self.consultar(args)
        bombas = []
        try:
            for registro in jsondoc:
                bomba = Bomba()
                bomba.set(registro)
                if bomba.getIdCoordinador > 0:
                    #coordinador = self.consultarCoordinador(bomba.getIdCoordinador)
                    coordinador = Coordinador()
                    coordinador.setFromBomba(registro)
                    bomba.setCoordinador(coordinador)
                bombas.append(bomba)
            self._bombas = bombas
            self.signalBombasConsultadas.emit()
        except TypeError:
            pass
        return bombas

    def consultarSubsistemasBombas(self):
        args = {'opcion': self.CONSULTAR_SUBSISTEMAS_BOMBAS}
        jsondoc = self.consultar(args)
        subsistemas = []
        for registro in jsondoc:
            subsistema = Subsistema()
            subsistema.set(registro)
            subsistemas.append(subsistema)
        return subsistemas

    def consultarPasswordIoT(self, idDispositivo, flagCoordinador, flagSignal=False):
        args = {'opcion': self.CONSULTAR_PASSWORD_IOT, 'id_dispositivo': idDispositivo, 'flag_coordinador': flagCoordinador}
        data = self.consultar(args)
        if flagSignal:
            try:
                self.signalPassword.emit(data[0]['password'])
            except (IndexError, TypeError, ValueError) as error:
                self.signalPassword.emit(str(data))
        return data

    def actualizarEstadoBomba(self, idGrupo, estado):
        args = {'opcion': self.ACTUALIZAR_ESTADO_BOMBA, 'id_grupo': idGrupo, 'estado': estado}
        try:
            self.consultar(args)
            return True
        except:
            return False

    def consultarHorarios(self, idGrupo):
        args = {'opcion': self.CONSULTAR_HORARIOS, 'id_grupo': idGrupo}
        jsondoc = self.consultar(args)
        horarios = []
        for registro in jsondoc:
            horario = Horario()
            horario.set(registro)
            horarios.append(horario)
        return horarios

    def consultarCoordinador(self, idCoordinador):
        args = {'opcion': self.CONSULTAR_COORDINADOR, 'id_coordinador': idCoordinador}
        jsondoc = self.consultar(args)
        coordinador = Coordinador()
        coordinador.set(jsondoc[0])
        return coordinador

    @property
    def getBombas(self):
        return self._bombas

# (>'-')> <('-'<) ^('-')^ v('-')v (>'-')> (^-^) If you're tired, just do a happy dance. Poyo!!!
