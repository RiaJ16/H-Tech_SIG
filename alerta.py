import json

from objdict import ObjDict

class Alerta:

	def __init__(self, idSensor=0, valor=0.0):
		self.idSensor = idSensor
		try:
			self.valor = float(valor)
		except ValueError:
			self.valor = 0.0

	def set(self, registro):
		try:
			self.idSensor = int(registro['idSensor'])
		except:
			self.idSensor = 0
		try:
			self.valor = float(registro['valor'])
		except:
			self.valor = 0.0

	def setIdSensor(self, idSensor):
		try:
			self.idSensor = int(idSensor)
		except:
			self.idSensor = 0

	def setValor(self, valor):
		try:
			self.valor = float(valor)
		except:
			self.valor = 0.0

	def getIdSensor(self):
		return self.idSensor
	
	def getValor(self):
		return self.valor

	def json(self):
		data = ObjDict()
		data.idSensor = self.idSensor
		data.valor = self.valor
		return json.loads(data.dumps())
