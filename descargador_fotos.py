# -*- coding: utf-8 -*-

import ctypes
import os
import threading

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QPixmap

class DescargadorFotos:

	def __init__(self, online, descargar=True):
		self.filename = self._obtenerNombreArchivo(online)
		self.foto = QPixmap(self.filename)
		if self.foto.isNull() and descargar:
			url = self.filename.split('/')
			url = url[len(url)-1]
			t1 = threading.Thread(target=online.descargarFoto, args=(url, self.filename, 1))
			t1.start()
			self.foto = QPixmap(self.filename)

	def _obtenerNombreArchivo(self, online):
		try:
			filename = online.grupo.foto
		except:
			filename = ""
		if filename == "" or filename == None:
			filename = "%s/.sigrdap/Fotos/nodisponible.png" % os.path.expanduser('~')
		else:
			filename = "%s/.sigrdap/Fotos/%s" % (os.path.expanduser('~'),filename)
		return filename

	def obtenerMiniatura(self):
		newHeight = 80
		try:
			newWidth = self.foto.width()*newHeight/self.foto.height()
		except ZeroDivisionError:
			newWidth = 0
		if newWidth > 154:
			newWidth = 154
			newHeight = self.foto.height()*newWidth/self.foto.width()
		miniatura = QIcon(self.foto.scaled(newWidth,newHeight))
		size = QSize(newWidth,newHeight)
		return (miniatura, size)

	def obtenerReduccion(self):
		newWidth = self.foto.width()
		newHeight = self.foto.height()
		screenSize = ctypes.windll.user32.GetSystemMetrics(0)*3/4, ctypes.windll.user32.GetSystemMetrics(1)*3/4
		if newWidth > screenSize[0]:
			newWidth = screenSize[0]
			newHeight = newHeight * newWidth / self.foto.width()
		unmodifiedNewHeight = newHeight
		if newHeight > screenSize[1]:
			newHeight = screenSize[1]
			newWidth = newWidth * newHeight / unmodifiedNewHeight
		html = "<p><img src=\'%s' width='%f' height='%f'></p>" % (self.filename,newWidth,newHeight)
		size = QSize(newWidth,newHeight)
		return (html, size)
