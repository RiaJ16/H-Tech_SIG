import json

class Historico:

	def __init__(self,idHisto='',idUsuario='',idSensor='',fecha='',dato=''):
		self.idHisto = idHisto
		self.idUsuario = idUsuario
		self.idSensor = idSensor
		self.fecha = fecha
		self.dato = dato

	def set(self,registro):
		self.idHisto = registro['idHisto']
		self.idSensor = registro['idSensor']
		self.fecha = registro['fechaRegistrado']
		self.dato = registro['dato']

	def getIdHisto(self):
		return self.idHisto
	
	def getIdSensor(self):
		return self.idSensor

	def getFecha(self):
		return self.fecha

	def getDato(self):
		return self.dato

	def json(self):
		data = {}
		data['idHisto'] = self.idHisto
		data['idSensor'] = self.idSensor
		data['fecha'] = self.fecha
		data['dato'] = self.dato
		jsondoc = json.dumps(data)
		return jsondoc