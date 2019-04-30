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
		validator = sender.validator()
		state = validator.validate(sender.text(), 0)[0]
		if state == QValidator.Acceptable:
			color = '#2ecc71' # verde
		elif state == QValidator.Intermediate:
			color = '#f1c40f' # amarillo
		else:
			color = '#e74c3c' # rojo
		sender.setStyleSheet('QLineEdit { border-bottom: 2px solid %s }' % color)