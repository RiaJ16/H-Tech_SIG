# -*- coding: UTF8 -*-

from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLayout, QWidget

class HtmlWidgetItem(QWidget):

	def __init__(self,texto,css):
		QWidget.__init__(self)
		self.__build(texto,css)

	def __build(self,texto,css):
		item = QWidget()
		itemText = QLabel("<style>%s</style> %s" % (css,texto))
		itemLayout = QHBoxLayout()
		itemLayout.addWidget(itemText)
		itemLayout.setSizeConstraint(QLayout.SetFixedSize)
		self.setLayout(itemLayout)