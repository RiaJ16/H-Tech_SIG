# -*- coding: UTF8 -*-

from PyQt5.QtWidgets import QTableWidgetItem

class WidgetItemMas(QTableWidgetItem):

	def __init__(self,texto,idFeature):
		QTableWidgetItem.__init__(self,texto)
		self._idFeature = idFeature

	def idFeature(self):
		return self._idFeature