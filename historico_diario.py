import json

from objdict import ObjDict

class HistoricoDiario:

	def __init__(self,idUsuario='',idSensor='',fecha='',minmax='',dato='',finalizado=0):
		self.idUsuario = idUsuario
		self.idSensor = idSensor
		self.fecha = fecha
		self.minmax = minmax
		self.dato = dato
		self.finalizado = finalizado

	def set(self,registro):
		self.idSensor = registro['idSensor']
		self.fecha = registro['fecha']
		self.minmax = registro['minmax']
		self.dato = registro['dato']
		self.finalizado = registro['finalizado']
	
	def getIdSensor(self):
		return self.idSensor

	def getFecha(self):
		return self.fecha

	def getMinmax(self):
		return self.minmax

	def getDato(self):
		return self.dato

	def isFinalizado(self):
		return self.finalizado

	def json(self):
		data = ObjDict()
		data.idSensor = self.idSensor
		data.fecha = self.fecha
		data.minmax = self.minmax
		data.dato = self.dato
		data.finalizado = self.finalizado
		return json.loads(data.dumps())