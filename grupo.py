import json

from objdict import ObjDict

class Grupo:

	def __init__(self,idGrupo='',idSubsistema=0,nombre='',descripcion='',foto=''):
		self.idGrupo = idGrupo
		self.idSubsistema = int(idSubsistema)
		self.nombre = nombre
		self.descripcion = descripcion
		self.foto = foto

	def set(self,registro):
		self.idGrupo = registro['idGrupo']
		self.idSubsistema = registro['idSubsistema']
		self.nombre = registro['nombre']
		self.descripcion = registro['descripcion']
		self.foto = registro['foto']

	def getIdGrupo(self):
		return self.idGrupo

	def getIdSubsistema(self):
		return self.idSubsistema

	def getNombre(self):
		return self.nombre

	def getDescripcion(self):
		return self.descripcion

	def getFoto(self):
		return self.foto

	def json(self):
		data = ObjDict()
		data.idGrupo = self.idGrupo
		data.idSubsistema = self.idSubsistema
		data.nombre = self.nombre
		data.descripcion = self.descripcion
		data.foto = self.foto
		return json.loads(data.dumps())