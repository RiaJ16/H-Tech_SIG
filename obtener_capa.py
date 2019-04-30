from qgis.core import QgsProject

class ObtenerCapa:

	def capa():
		capa = ''
		for layer in QgsProject.instance().mapLayers().values():
			if layer.name() == "Sensores":
				capa = layer
				break
		return capa