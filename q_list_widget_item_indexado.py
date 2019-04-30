# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QListWidgetItem

class QListWidgetItemIndexado(QListWidgetItem):

	def __init__(self,etiqueta,id):
		QListWidgetItem.__init__(self,etiqueta)
		self.idAt = id

	def id(self):
		return self.idAt