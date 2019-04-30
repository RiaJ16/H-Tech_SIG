import json

from objdict import ObjDict

class Correo:

	def __init__(self,idCorreo='',correo='',tipoSubsistema=0):
		try:
			self.idCorreo = int(idCorreo)
		except:
			self.idCorreo = ''
		self.correo = correo
		self.tipoSubsistema = tipoSubsistema

	def set(self,registro):
		try:
			self.idCorreo = int(registro['idCorreo'])
		except:
			self.idCorreo = 0
		try:
			self.correo = registro['correo']
		except:
			self.correo = ''
		try:
			self.tipoSubsistema = int(registro['tipoSubsistema'])
		except:
			self.tipoSubsistema = 0

	def setIdCorreo(self,idCorreo):
		self.idCorreo = idCorreo

	def setCorreo(self,correo):
		self.correo = correo

	def setTipoSubsistema(self,tipoSubsistema):
		self.tipoSubsistema = tipoSubsistema

	def getIdCorreo(self):
		return self.idCorreo
	
	def getCorreo(self):
		return self.correo

	def getTipoSubsistema(self):
		return self.tipoSubsistema

	def json(self):
		data = ObjDict()
		data.idCorreo = self.idCorreo
		data.correo = self.correo
		data.tipoSubsistema = self.tipoSubsistema
		return json.loads(data.dumps())