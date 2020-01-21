# -*- coding: UTF8 -*-

from PyQt5.QtGui import QValidator, QDoubleValidator, QRegExpValidator
from PyQt5.QtCore import QRegExp

class Validacion():

	def __init__(self,sender):
		self.sender = sender

	def validarDoble(self,listaCampos):
		validadorDoble = QDoubleValidator()
		for elemento in listaCampos:
			elemento.setValidator(validadorDoble)
			elemento.textChanged.connect(self.validarEstado)
			elemento.textChanged.emit(elemento.text())

	def validarRegExp(self,listaCampos,textregexp):
		regExp = QRegExp(textregexp)
		validadorRegExp = QRegExpValidator(regExp)
		for elemento in listaCampos:
			elemento.setValidator(validadorRegExp)
			elemento.textChanged.connect(self.validarEstado)
			elemento.textChanged.emit(elemento.text())

	def validarEstado(self, *args, **kwargs):
		sender = self.sender()
		try:
			validator = sender.validator()
			state = validator.validate(sender.text(), 0)[0]
			if state == QValidator.Acceptable:
				color = '#2ecc71' # verde
				bgcolor = '#cdeadc'
			elif state == QValidator.Intermediate:
				color = '#f1c40f' # amarillo
				bgcolor = '#ede9cf'
			else:
				color = '#e74c3c' # rojo
				bgcolor = '#ebd8d6'
			sender.setStyleSheet('QLineEdit { background-color: %s; border-bottom: 6px solid %s; } QLineEdit:disabled{color: #7f8c8d; background-color: #bdc3c7; border-bottom: 6px solid #95a5a6;}' % (bgcolor, color))
		except AttributeError:
			pass
