import json

class Municipio:

	def __init__(self,idMunicipio='',idEstado='',nombre=''):
		self.idMunicipio = idMunicipio
		self.idEstado = idEstado
		self.nombre = nombre

	def set(self,registro):
		self.idMunicipio = registro['idMunicipio']
		self.idEstado = registro['idEstado']
		self.nombre = registro['nombre']

	def getIdMunicipio(self):
		return self.idMunicipio

	def getIdEstado(self):
		return self.idEstado

	def getNombre(self):
		return self.nombre

	def json(self):
		data = {}
		data['idMunicipio'] = self.idMunicipio
		data['idEstado'] = self.idEstado
		data['nombre'] = self.nombre
		jsondoc = json.dumps(data)
		return jsondoc