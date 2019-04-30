import json

class TipoSensor:

	def __init__(self,idTipoSensor='',nombre=''):
		self.idTipoSensor = idTipoSensor
		self.nombre = nombre

	def set(self,registro):
		self.idTipoSensor = registro['idTipoSensor']
		self.nombre = registro['nombre']

	def getIdTipoSensor(self):
		return self.idTipoSensor

	def getNombre(self):
		return self.nombre

	def json(self):
		data = {}
		data['idTipoSensor'] = self.idTipoSensor
		data['nombre'] = self.idUsuario
		jsondoc = json.dumps(data)
		return jsondoc