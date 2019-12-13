import json

from objdict import ObjDict


class Coordinador:

    def __init__(self, idCoordinador=0, idDispositivo='', nombre='', conectado = -1):
        self._idCoordinador = int(idCoordinador)
        self._idDispositivo = idDispositivo
        self._nombre = nombre
        self._conectado = conectado

    def set(self, registro):
        self._idCoordinador = registro['idCoordinador']
        self._idDispositivo = registro['idDispositivo']
        self._nombre = registro['nombre']
        self._conectado = int(registro['conectado'])

    def setFromBomba(self, registro):
        self._idCoordinador = registro['idCoordinador']
        self._idDispositivo = registro['idDispositivoCoordinador']
        self._nombre = registro['nombreCoordinador']
        self._conectado = int(registro['conectadoCoordinador'])

    @property
    def getIdCoordinador(self):
        return self._idCoordinador

    @property
    def getIdDispositivo(self):
        return self._idDispositivo

    @property
    def getNombre(self):
        return self._nombre

    @property
    def getConectado(self):
        return self._conectado

    def json(self):
        data = ObjDict()
        data.idCoordinador = self._idCoordinador
        data.idDispositivo = self._idDispositivo
        data.nombre = self._nombre
        data.conectado = self._conectado
        return json.loads(data.dumps())

    def __eq__(self, other):
        if not isinstance(other, Coordinador):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self._idCoordinador == other._idCoordinador and self._idDispositivo == other._idDispositivo and self._nombre == other._nombre and self._conectado == other._conectado
