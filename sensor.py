import json

from objdict import ObjDict

class Sensor:

	def __init__(self,idSensor=0,idDispositivo=0,idFeature=0,calle='',colonia='',cp=0,tipoSensor=0,municipio=0,area=0.0,datoMaximo=0.0,datoMinimo=0.0,alarma=0,altura=0,datoActual=0,grupo=0,estado=0,correoEnviado=0,online=0,maximo=30,x=0,y=0,idSubsistema=0):
		self.idSensor = idSensor
		self.idDispositivo = idDispositivo
		self.idFeature = idFeature
		self.calle = calle
		self.colonia = colonia
		self.cp = cp
		self.tipoSensor = tipoSensor
		self.municipio = municipio
		if area == '':
			self.area = 0.0
		else:
			self.area = float(area)
		if datoMaximo == '':
			self.datoMaximo = 0.0
		else:
			self.datoMaximo = float(datoMaximo)
		if datoMinimo == '':
			self.datoMinimo = 0.0
		else:
			self.datoMinimo = float(datoMinimo)
		self.alarma = int(alarma)
		if altura == '':
			self.altura = 0.0
		else:
			self.altura = float(altura)
		self.datoActual = datoActual
		self.grupo = grupo
		self.estado = estado
		self.correoEnviado = correoEnviado
		self.online = online
		if maximo == '':
			self.maximo = 30
		else:
			self.maximo = maximo
		if x == '':
			self.x = 0.0
		else:
			self.x = float(x)
		if y == '':
			self.y = 0.0
		else:
			self.y = float(y)
		self.idSubsistema = idSubsistema

	def set(self,registro):
		try:
			self.idSensor = int(registro['idSensor'])
			self.idDispositivo = registro['idDispositivo']
			self.idFeature = int(registro['idFeature'])
			self.calle = registro['calle']
			self.colonia = registro['colonia']
			self.cp = registro['cp']
			try:
				self.tipoSensor = int(registro['tipoSensor'])
			except:
				self.tipoSensor = registro['tipoSensor']
			try:
				self.municipio = int(registro['municipio'])
			except:
				self.municipio = registro['municipio']
			self.area = float(registro['area'])
			self.datoMaximo = float(registro['datoMaximo'])
			self.datoMinimo = float(registro['datoMinimo'])
			self.alarma = int(registro['alarma'])
			self.altura = float(registro['altura'])
			self.datoActual = float(registro['datoActual'])
			try:
				self.grupo = int(registro['grupo'])
			except:
				self.grupo = registro['grupo']
			self.estado = int(registro['estado'])
			self.correoEnviado = int(registro['correoEnviado'])
			self.online = int(registro['online'])
			self.maximo = int(registro['maximo'])
			try:
				self.tipoSensorTexto = registro['tipoSensorTexto']
				self.municipioTexto = registro['municipioTexto']
				self.grupoTexto = registro['grupoTexto']
			except:
				pass
			try:
				self.x = float(registro['x'])
				self.y = float(registro['y'])
			except:
				pass
			try:
				self.idSubsistema = int(registro['idSubsistema'])
			except:
				pass
		except TypeError:
			self.idSensor = 0

	def json(self):
		data = ObjDict()
		data.idSensor = self.idSensor
		data.idDispositivo = self.idDispositivo
		data.idFeature = self.idFeature
		data.calle = self.calle
		data.colonia = self.colonia
		data.cp = self.cp
		data.tipoSensor = self.tipoSensor
		data.municipio = self.municipio
		data.area = self.area
		data.datoMaximo = self.datoMaximo
		data.datoMinimo = self.datoMinimo
		data.alarma = self.alarma
		data.altura = self.altura
		data.datoActual = self.datoActual
		data.grupo = self.grupo
		data.estado = self.estado
		data.correoEnviado = self.correoEnviado
		data.online = self.online
		data.maximo = self.maximo
		data.x = self.x
		data.y = self.y
		data.idSubsistema = self.idSubsistema
		return json.loads(data.dumps())