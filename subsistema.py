import json

from objdict import ObjDict

class Subsistema:

	def __init__(self,idSubsistema=0,nombre='',tipo=0):
		self.idSubsistema = idSubsistema
		self.nombre = nombre
		self.tipo = tipo

	def set(self,registro):
		self.idSubsistema = registro['idSubsistema']
		self.nombre = registro['nombre']
		self.tipo = registro['tipo']

	def json(self):
		data = ObjDict()
		data.idSubsistema = self.idSubsistema
		data.nombre = self.nombre
		data.tipo = self.tipo
		return json.loads(data.dumps())