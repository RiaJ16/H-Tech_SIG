# -*- coding: UTF8 -*-

import shutil
import json
import os
import pickle
import requests

from requests.exceptions import ConnectionError

from PyQt5.QtCore import QObject, pyqtSignal

from uuid import getnode as get_mac

from .correo import Correo
from .grupo import Grupo
from .historico import Historico
from .municipio import Municipio
from .sensor import Sensor
from .subsistema import Subsistema
from .tipo_sensor import TipoSensor

class Online(QObject):

	signalMunicipios = pyqtSignal()
	signalTiposSensor = pyqtSignal()
	signalGrupos = pyqtSignal()
	signalGenerarId = pyqtSignal(int)
	signalErrorConexion = pyqtSignal()
	signalNotLoggedIn = pyqtSignal()
	signalLoggedIn = pyqtSignal(int)
	signalLoggedOut = pyqtSignal(int)
	signalSensorConsultado = pyqtSignal()
	signalSensoresConsultados = pyqtSignal()
	signalConsultarId = pyqtSignal(int)
	signalConsultarGrupo = pyqtSignal()
	signalHistoricos = pyqtSignal(int)
	signalCorreosConsultados = pyqtSignal()
	signalSubsistemasConsultados = pyqtSignal()
	signalTotalGrupos = pyqtSignal(int)
	signalFotoDescargada = pyqtSignal(int)

	CONSULTAR_ULTIMO_ID = 0
	COMPROBAR_ID_FEATURE = 1
	CONSULTAR_SENSORES = 2
	CONSULTAR_HISTORICOS = 24
	CONSULTAR_MUNICIPIOS = 4
	CONSULTAR_TIPOS_SENSOR = 5
	CONSULTAR_GRUPOS = 6
	CONSULTAR_ID_FROM_ID_FEATURE = 7
	CONSULTAR_SENSOR_POR_ID = 8
	CONSULTAR_SENSOR_POR_ID_NOMBRES = 9
	CONSULTAR_SENSOR_POR_ID_FEATURE = 10
	IS_EMPTY = 11
	CONSULTAR_GRUPO_POR_ID = 12
	SEPARAR_SENSORES = 13
	CONSULTAR_CORREOS = 14
	ELIMINAR_CORREO = 15
	CONSULTAR_SISTEMA = 17
	CONSULTAR_USUARIO = 18
	CONSULTAR_SUBSISTEMAS_POR_TIPO = 19
	CONSULTAR_GRUPOS_POR_SUBSISTEMA = 21
	CONSULTAR_TOTAL_GRUPOS = 22
	
	INSERTAR_SENSOR = 0
	EDITAR_SENSOR = 1
	INSERTAR_GRUPO = 2
	EDITAR_GRUPO = 3
	INSERTAR_CORREO = 4
	EDITAR_CORREO = 5
	
	CONSULTAR_HISTORICO_DIARIO = 0
	INSERTAR_HISTORICO_DIARIO = 1
	ACTUALIZAR_HISTORICO_DIARIO = 2
	CONSULTAR_PRESION = 3
	CONSULTAR_PRESION_MES = 4
	CONSULTAR_QUINCE_MINUTOS = 5
	CONSULTAR_ACUMULADO_DEL_MES = 6

	IP = "https://webservice.htech.mx"
	IMAGES_DIR = "http://images.htech.mx/images/grupos/"
	TIMEOUT = 10

	def login(self,usuario="",password="",sendSignal=True):
		androidToken = get_mac()
		sesion = self.__leerSesion()
		try:
			if(usuario == '' and password == ''):
				r = sesion.post('%s/login.php' % self.IP,timeout=5)
			else:
				r = sesion.post('%s/login.php' % self.IP,data={'usuario':usuario,'password':password,'token':androidToken},timeout=self.TIMEOUT)
			self.__guardarSesion(sesion)
			sesion.close()
			if sendSignal:
				try:
					self.signalLoggedIn.emit(int(r.text))
				except ValueError:
					self.signalErrorConexion.emit()
			if r.text == '5':
				return (False)
			else:
				return (True)
		except ConnectionError:
			if sendSignal:
				#self.signalLoggedIn.emit(6)
				self.signalErrorConexion.emit()
			return (False)

	def printSession(self):
		r = requests.post('%s/cookies.php' % self.IP,timeout=self.TIMEOUT)#,cookies=cookies)
		#print(r.text)

	def logout(self):
		sesion = self.__leerSesion()
		try:
			r = sesion.post('%s/logout.php' % self.IP,timeout=self.TIMEOUT)
			sesion.close()
			self.__guardarSesion(sesion)
			self.signalLoggedOut.emit(0)
			if hasattr(self,'_idSistema'):
				del self._idSistema
		except ConnectionError:
			self.signalLoggedOut.emit(1)

	def __guardarSesion(self,sesion):
		path = '%s\.sigrdap\\' % os.environ['HOME']
		if not os.path.exists(path):
			os.makedirs(path)
		try:
			with open('%s\.sigrdap\sesion' % os.environ['HOME'],'wb') as f:
				pickle.dump(sesion,f)
		except:
			pass

	def __leerSesion(self):
		sesion = requests.session()
		try:
			with open('%s\.sigrdap\sesion' % os.environ['HOME'],'rb') as f:
				sesion = pickle.load(f)
		except:
			pass
		return sesion

	def idSistema(self):
		if not hasattr(self,'_idSistema'):
			args = {'opcion':self.CONSULTAR_SISTEMA}
			jsondoc = self.consultar(args)
			#print(jsondoc)
			self._idSistema = jsondoc[0]['idSistema']
		return self._idSistema

	def consultar(self,args,seed=False):
		try:
			sesion = self.__leerSesion()
			r = sesion.post('%s/consultar.php' % self.IP,data=args,timeout=self.TIMEOUT)
			sesion.close()
			if r.text == '0' and not seed:
				self.login(sendSignal=False)
				return self.consultar(args,True)
			else:
				jsondoc = r.json()
				if jsondoc == 0:
					jsondoc = [jsondoc]
				return jsondoc
		except ConnectionError:
			self.signalErrorConexion.emit()
			return []
		except requests.exceptions.ReadTimeout:
			self.signalErrorConexion.emit()
			return []

	def insertar(self,args,elemento):
		sesion = self.__leerSesion()
		url = '%s/insertar.php' % self.IP
		try:
			jsondoc = elemento.json()
			jsondoc.update(args)
			r = sesion.post(url,json=jsondoc,timeout=self.TIMEOUT)
			sesion.close()
			return True
		except ConnectionError:
			self.signalErrorConexion.emit()
			return False
		#print(r.status_code)
		#print(r.text)

	def consultarSensores(self):
		args = {'opcion':self.CONSULTAR_SENSORES}
		jsondoc = self.consultar(args)
		sensores = []
		try:
			for registro in jsondoc:
				sensor = Sensor()
				sensor.set(registro)
				sensores.append(sensor)
		except:
			pass
		self.sensores = sensores
		self.signalSensoresConsultados.emit()
		return sensores

	def consultarHistoricos(self,idSensor,fechaInicial='0',fechaFinal='22220208140200',seed=False):
		sesion = self.__leerSesion()
		r = sesion.post('%s/consultar.php' % self.IP,
			data={'opcion':self.CONSULTAR_HISTORICOS,'id_sensor':idSensor,'fecha_inicial':fechaInicial,'fecha_final':fechaFinal},timeout=self.TIMEOUT)
		sesion.close()
		if r.text == '0' and not seed:
			self.login(sendSignal=False)
			self.consultarHistoricos(idSensor,fechaInicial,fechaFinal,True)
		else:
			jsondoc = r.json()
			historicos = []
			try:
				for registro in jsondoc:
					historico = Historico()
					historico.set(registro)
					historicos.append(historico)
			except:
				pass
				#pedir logueo
			self.historicos = historicos
			token = int((int(fechaInicial) + int(fechaFinal))/1000000)
			self.signalHistoricos.emit(token)

	def consultarMunicipios(self):
		args = {'opcion':self.CONSULTAR_MUNICIPIOS}
		jsondoc = self.consultar(args)
		municipios = []
		try:
			for registro in jsondoc:
				municipio = Municipio()
				municipio.set(registro)
				municipios.append(municipio)
		except:
			pass
		self.municipios = municipios
		self.signalMunicipios.emit()

	def consultarTiposSensor(self):
		args = {'opcion':self.CONSULTAR_TIPOS_SENSOR}
		jsondoc = self.consultar(args)
		tiposSensor = []
		try:
			for registro in jsondoc:
				tipoSensor = TipoSensor()
				tipoSensor.set(registro)
				tiposSensor.append(tipoSensor)
		except:
			pass
		self.tiposSensor = tiposSensor
		self.signalTiposSensor.emit()

	def consultarGrupos(self):
		args = {'opcion':self.CONSULTAR_GRUPOS}
		jsondoc = self.consultar(args)
		try:
			if jsondoc[0] == 0:
				return '0'
		except IndexError:
			return '1'
		grupos = []
		try:
			for registro in jsondoc:
				grupo = Grupo()
				grupo.set(registro)
				grupos.append(grupo)
		except:
			pass
		self.grupos = grupos
		self.signalGrupos.emit()
		return grupos

	def consultarGrupoPorId(self,idGrupo):
		args = {'opcion':self.CONSULTAR_GRUPO_POR_ID,'id_grupo':idGrupo}
		jsondoc = self.consultar(args)
		grupo = Grupo()
		try:
			grupo.set(jsondoc[0])
		except:
			pass
		self.grupo = grupo
		self.signalConsultarGrupo.emit()

	def generarId(self):
		args = {'opcion':self.CONSULTAR_ULTIMO_ID}
		jsondoc = self.consultar(args)
		try:
			id = int(jsondoc[0]['idSensor'])
		except:
			id = 0
		self.signalGenerarId.emit(id+1)

	def consultarIdFromIdFeature(self,idFeature):
		args = {'opcion':self.CONSULTAR_ID_FROM_ID_FEATURE,'id_feature':idFeature}
		jsondoc = self.consultar(args)
		try:
			id = int(jsondoc[0]['idSensor'])
		except:
			id = 0
		self.signalConsultarId.emit(id)
		return id

	def consultarSensorPorId(self,idSensor):
		args = {'opcion':self.CONSULTAR_SENSOR_POR_ID,'id_sensor':idSensor}
		jsondoc = self.consultar(args)
		sensor = Sensor()
		sensor.set(jsondoc[0])
		self.signalSensorConsultado.emit()
		self.sensor = sensor

	def consultarSensorPorIdNombres(self,idSensor):
		args = {'opcion':self.CONSULTAR_SENSOR_POR_ID_NOMBRES,'id_sensor':idSensor}
		jsondoc = self.consultar(args)
		sensor = Sensor()
		sensor.set(jsondoc[0])
		self.signalSensorConsultado.emit()
		self.sensor = sensor

	def consultarSensorPorIdFeature(self,idFeature):
		args = {'opcion':self.CONSULTAR_SENSOR_POR_ID_FEATURE,'id_feature':idFeature}
		jsondoc = self.consultar(args)
		sensor = Sensor()
		try:
			sensor.set(jsondoc[0])
			self.sensor = sensor
			self.signalSensorConsultado.emit()
		except:
			pass

	def consultarCorreos(self,tipoSubsistema):
		args = {'opcion':self.CONSULTAR_CORREOS,'tipo_subsistema':tipoSubsistema}
		jsondoc = self.consultar(args)
		correos = []
		for registro in jsondoc:
			correo = Correo()
			correo.set(registro)
			correos.append(correo)
		self.correos = correos
		self.signalCorreosConsultados.emit()

	def consultarSubsistemasPorTipo(self,tipoSubsistema):
		args = {'opcion':self.CONSULTAR_SUBSISTEMAS_POR_TIPO,'tipo_subsistema':tipoSubsistema}
		jsondoc = self.consultar(args)
		if jsondoc == [0]:
			self.signalNotLoggedIn.emit()
		else:
			subsistemas = []
			for registro in jsondoc:
				subsistema = Subsistema()
				subsistema.set(registro)
				subsistemas.append(subsistema)
			self.subsistemas = subsistemas
			self.signalSubsistemasConsultados.emit()

	def consultarGruposPorSubsistema(self,idSubsistema):
		args = {'opcion':self.CONSULTAR_GRUPOS_POR_SUBSISTEMA,'id_subsistema':idSubsistema}
		jsondoc = self.consultar(args)
		grupos = []
		for registro in jsondoc:
			grupo = Grupo()
			grupo.set(registro)
			grupos.append(grupo)
		self.grupos = grupos
		self.signalGrupos.emit()

	def consultarTotalGrupos(self):
		args = {'opcion':self.CONSULTAR_TOTAL_GRUPOS}
		data = self.consultar(args)
		id = 0
		try:
			if not (data == []):
				id = int(data[0]['idGrupo'])
			self.signalTotalGrupos.emit(id)
		except TypeError:
			pass

	def eliminarCorreo(self,idCorreo,tipoSubsistema):
		args = {'opcion':self.ELIMINAR_CORREO,'id_correo':idCorreo,'tipo_subsistema':tipoSubsistema}
		try:
			self.consultar(args)
			return True
		except:
			return False

	def insertarSensor(self,sensor):
		args = {'opcion':self.INSERTAR_SENSOR}
		return self.insertar(args,sensor)

	def editarSensor(self,sensor):
		args = {'opcion':self.EDITAR_SENSOR}
		return self.insertar(args,sensor)

	def insertarGrupo(self,grupo):
		args = {'opcion':self.INSERTAR_GRUPO}
		return self.insertar(args,grupo)

	def editarGrupo(self,grupo):
		args = {'opcion':self.EDITAR_GRUPO}
		return self.insertar(args,grupo)

	def insertarCorreo(self,correo):
		args = {'opcion':self.INSERTAR_CORREO}
		return self.insertar(args,correo)

	def editarCorreo(self,correo):
		args = {'opcion':self.EDITAR_CORREO}
		return self.insertar(args,correo)

	def actualizarAlarmas(self):
		url = '%s/alarmas.php' % self.IP
		sesion = self.__leerSesion()
		r = sesion.post(url,timeout=2)
		sesion.close()
		return r.status_code
		
	def eliminarSensor(self,idSensor,seed=False):
		url = '%s/eliminar.php' % self.IP
		sesion = self.__leerSesion()
		try:
			r = sesion.post(url,data={'id_sensor':idSensor},timeout=self.TIMEOUT)
			sesion.close()
			texto = r.text
			if r.text == '0' and not seed:
				self.login(sendSignal=False)
				texto = self.eliminarSensor(True)
			return texto
		except ConnectionError:
			self.signalErrorConexion.emit()
			return '3'

	def actualizarFotoGrupo(self,imagenUrl,grupo,seed=False):
		url = '%s/fotos.php' % self.IP
		sesion = self.__leerSesion()
		imageFileDescriptor = open(imagenUrl,'rb')
		files = {'imagen':imageFileDescriptor}
		try:
			r = sesion.post(url,data={'grupo':grupo},files=files)
			sesion.close()
			imageFileDescriptor.close()
			texto = r.text
			if r.text == '1' and not seed:
				self.login(sendSignal=False)
				texto = self.actualizarFotoGrupo(imagenUrl,grupo,True)
			return texto
		except ConnectionError:
			self.signalErrorConexion.emit()
			return '2'

	def descargarFoto(self,url,directorio,token=0,isGrupo=True):
		if isGrupo:
			url = '%s%s/%s' % (self.IMAGES_DIR,self.idSistema(),url)
		else:
			url = '%s/%s' % (self.IMAGES_DIR,url)
		try:
			r = requests.get(url,stream=True)
			with open(directorio,'wb') as out_file:
				shutil.copyfileobj(r.raw,out_file)
			if token != 0:
				self.signalFotoDescargada.emit(token)
		except:
			pass

	def obtenerFoto(self,idGrupo):
		pass

	def getSensor(self):
		return self.sensor

	def getGrupos(self):
		return self.grupos

	def getGrupo(self):
		return self.grupo

	def getHistoricos(self):
		return self.historicos

	def getSensores(self):
		return self.sensores

	def getCorreos(self):
		return self.correos

	def getSubsistemas(self):
		return self.subsistemas

	def isEmpty(self,idSensor):
		args = {'opcion':self.IS_EMPTY,'id_sensor':idSensor}
		jsondoc = self.consultar(args)
		registros = int(jsondoc[0]['registros'])
		if registros > 0:
			return False
		else:
			return True

#Históricos diarios

	def consultarReportes(self,args,seed=False):
		sesion = self.__leerSesion()
		r = sesion.post('%s/reportes.php' % self.IP,data=args,timeout=self.TIMEOUT)
		sesion.close()
		if r.text == '0' and not seed:
			self.login(sendSignal=False)
			return self.consultar(args,True)
		else:
			jsondoc = r.json()
			if jsondoc == 0:
				jsondoc = [jsondoc]
			return jsondoc

	def insertarHistoricoDiario(self,historicoDiario):
		args = {'opcion':self.INSERTAR_HISTORICO_DIARIO}
		sesion = self.__leerSesion()
		url = '%s/reportes.php' % self.IP
		try:
			jsondoc = historicoDiario.json()
			#print(jsondoc)
			jsondoc.update(args)
			r = sesion.post(url,json=jsondoc,timeout=self.TIMEOUT)
			sesion.close()
			return True
		except ConnectionError:
			self.signalErrorConexion.emit()
			return False

	def actualizarHistoricoDiario(self,historicoDiario):
		args = {'opcion':self.ACTUALIZAR_HISTORICO_DIARIO}
		sesion = self.__leerSesion()
		url = '%s/reportes.php' % self.IP
		try:
			jsondoc = historicoDiario.json()
			jsondoc.update(args)
			r = sesion.post(url,json=jsondoc,timeout=self.TIMEOUT)
			sesion.close()
			return True
		except ConnectionError:
			self.signalErrorConexion.emit()
			return False

	def consultarHistoricoDiario(self,idSensor,fecha,minmax=0):
		args = {'opcion':self.CONSULTAR_HISTORICO_DIARIO,'id_sensor':idSensor,'fecha':fecha,'minmax':minmax}
		jsondoc = self.consultarReportes(args)
		#self.signalSensorConsultado.emit()
		return jsondoc[0]

	#Presión

	def consultarPresion(self,idSensor,fecha,minmax=0):
		args = {'opcion':self.CONSULTAR_PRESION,'id_sensor':idSensor,'fecha':fecha,'minmax':minmax}
		jsondoc = self.consultarReportes(args)
		return jsondoc[0]

	def consultarPresionMes(self,idSensor,fecha,minmax=0):
		args = {'opcion':self.CONSULTAR_PRESION_MES,'id_sensor':idSensor,'fecha':fecha,'minmax':minmax}
		jsondoc = self.consultarReportes(args)
		return jsondoc[0]

	#Flujo

	def consultarQuinceMinutos(self,idSensor,fecha):
		args = {'opcion':self.CONSULTAR_QUINCE_MINUTOS,'id_sensor':idSensor,'fecha':fecha}
		jsondoc = self.consultarReportes(args)
		historicos = []
		for registro in jsondoc:
			historico = Historico()
			historico.set(registro)
			historicos.append(historico)
		return historicos

	def consultarAcumuladoDelMes(self,idSensor,fecha):
		args = {'opcion':self.CONSULTAR_ACUMULADO_DEL_MES,'id_sensor':idSensor,'fecha':fecha}
		jsondoc = self.consultarReportes(args)
		try:
			suma = '%.2f' % float(jsondoc[0]['suma'])
		except:
			suma = '0'
		return suma

#Detectar click a más de un sensor a la vez

	def separarSensores(self,idSensores):
		args = {'opcion':self.SEPARAR_SENSORES,'id_sensor':idSensores}
		jsondoc = self.consultar(args)
		sensores = []
		try:
			for registro in jsondoc:
				sensor = Sensor()
				sensor.set(registro)
				sensores.append(sensor)
		except:
			pass
		return sensores

	def actualizarEstados(self):
		try:
			sesion = self.__leerSesion()
			#r = sesion.post('%s/estados.php' % self.IP,timeout=self.TIMEOUT)
			sesion.close()
		except ConnectionError:
			pass
		except requests.exceptions.ReadTimeout:
			pass
			
#(>'-')> <('-'<) ^('-')^ v('-')v (>'-')> (^-^) If you're tired, just do a happy dance. Poyo!!!