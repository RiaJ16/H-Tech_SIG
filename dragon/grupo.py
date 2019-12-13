import json

from objdict import ObjDict


class Grupo:

    def __init__(self,idGrupo=0,idSubsistema=0,nombre='',descripcion='',foto=''):
        self._idGrupo = int(idGrupo)
        self._idSubsistema = int(idSubsistema)
        self._nombre = nombre
        self._descripcion = descripcion
        self._foto = foto

    def set(self,registro):
        self._idGrupo = registro['idGrupo']
        self._idSubsistema = registro['idSubsistema']
        self._nombre = registro['nombre']
        self._descripcion = registro['descripcion']
        self._foto = registro['foto']

    @property
    def getIdGrupo(self):
        return self._idGrupo

    @property
    def getIdSubsistema(self):
        return self._idSubsistema

    @property
    def getNombre(self):
        return self._nombre

    @property
    def getDescripcion(self):
        return self._descripcion

    @property
    def getFoto(self):
        return self._foto

    def json(self):
        data = ObjDict()
        data.idGrupo = self._idGrupo
        data.idSubsistema = self._idSubsistema
        data.nombre = self._nombre
        data.descripcion = self._descripcion
        data.foto = self._foto
        return json.loads(data.dumps())

    def jsonData(self):
        data = ObjDict()
        data.idGrupo = self._idGrupo
        data.idSubsistema = self._idSubsistema
        data.nombre = self._nombre
        data.descripcion = self._descripcion
        data.foto = self._foto
        return data
