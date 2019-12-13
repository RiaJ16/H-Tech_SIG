import json

from PyQt5.QtCore import QTime

from objdict import ObjDict


def convertToQTime(cadena):
    return QTime(int(cadena[0:2]), int(cadena[3:5]))


class Horario:

    def __init__(self, idGrupo=0, dia=0, horaEncendido='', horaApagado=''):
        self._idGrupo = int(idGrupo)
        self._dia = int(dia)
        self._horaEncendido = horaEncendido
        self._horaApagado = horaApagado

    def set(self, registro):
        self._idGrupo = int(registro['idGrupo'])
        self._dia = int(registro['dia'])
        self._horaEncendido = registro['horaEncendido']
        self._horaApagado = registro['horaApagado']

    @property
    def getIdGrupo(self):
        return self._idGrupo

    @property
    def getDia(self):
        return self._dia

    @property
    def getHoraEncendido(self):
        return convertToQTime(self._horaEncendido)

    @property
    def getHoraEncendidoString(self):
        return self._horaEncendido

    def setHoraEncendido(self, horaEncendido):
        self._horaEncendido = horaEncendido

    @property
    def getHoraApagado(self):
        return convertToQTime(self._horaApagado)

    @property
    def getHoraApagadoString(self):
        return self._horaApagado

    def setHoraApagado(self, horaApagado):
        self._horaApagado = horaApagado

    def json(self):
        data = ObjDict()
        data.idGrupo = self._idGrupo
        data.dia = self._dia
        data.horaEncendido = self._horaEncendido
        data.horaApagado = self._horaApagado
        return json.loads(data.dumps())

    def __eq__(self, other):
        if not isinstance(other, Horario):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self._idGrupo == other._idGrupo and self._dia == other._dia and self._horaEncendido == other._horaEncendido and self._horaApagado == other._horaApagado
