import os

from qgis.core import QgsProject

class ObtenerCapa:

	_idCapa = ''

	def capa(self):
		capa = ''
		for layer in QgsProject.instance().mapLayers().values():
			if layer.id() == self._leerCapa():
				capa = layer
				break
		return capa

	def _leerCapa(self):
		if self.idCapa == '':
			nombreCapa = "capaSensores4"
			linea = ''
			path = "%s/.sigrdap" % os.path.expanduser('~')
			try:
				archivo = open("%s/%s" % (path,nombreCapa), "r")
				idCapa = archivo.readline()
				archivo.close()
			except IOError:
				idCapa = ''
			#print(self.idCapa)
			self.idCapa = idCapa
		else:
			idCapa = self.idCapa
		return idCapa

	@property
	def idCapa(self):
		return self._idCapa

	@idCapa.setter
	def idCapa(self,idCapa):
		self._idCapa = idCapa