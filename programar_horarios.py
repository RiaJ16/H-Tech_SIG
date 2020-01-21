import json
import os

from PyQt5 import uic
from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QDialog, QWidget

from .dragon.horario import Horario
from .publisher import Publisher
from .q_dialog_next import QDialogNext


class ProgramarHorarios(QDialogNext):

	def __init__(self, bomba, publisher, online, contexto = False, parent=None):
		super(ProgramarHorarios, self).__init__(parent)
		self.widget = QWidget()
		uic.loadUi(os.path.join(os.path.dirname(__file__), 'kraken.ui'), self)
		self.kraken.setStyleSheet("QFrame{background-color: #ecf0f1;}")
		uic.loadUi(os.path.join(os.path.dirname(__file__), 'dragon/ui/scheduler.ui'), self.widget)
		self.widget.kraken.hide()
		self.layout().addWidget(self.widget)
		self.bomba = bomba
		self.publisher = publisher
		self.online = online
		self.setMovable(self.kraken)
		self.setBotonCerrar(self.botonCerrar)
		self.horarios = []
		self.cargarHorarios()
		self._signals()
		self.fixUi()
		self.exec_()

	def fixUi(self):
		self.setWindowTitle(self.bomba.getNombre)

	def _signals(self):
		self.widget.botonEnviar.clicked.connect(self.enviar)

	def enviar(self):
		horarios = []
		#password = self.online.consultarPasswordIoT(self.bomba.getIdDispositivo, 0)[0]['password']
		password = '@T3CN010G14*.!'
		topic = "/sensores/%s" % self.bomba.getIdDispositivo
		encendidos = (
			self.widget.encendidoLunes, self.widget.encendidoMartes, self.widget.encendidoMiercoles, self.widget.encendidoJueves,
			self.widget.encendidoViernes, self.widget.encendidoSabado, self.widget.encendidoDomingo)
		apagados = (
			self.widget.apagadoLunes, self.widget.apagadoMartes, self.widget.apagadoMiercoles, self.widget.apagadoJueves, self.widget.apagadoViernes,
			self.widget.apagadoSabado, self.widget.apagadoDomingo)
		checkboxes = (
			self.widget.checkLunes, self.widget.checkMartes, self.widget.checkMiercoles, self.widget.checkJueves, self.widget.checkViernes,
			self.widget.checkSabado,
			self.widget.checkDomingo)
		if not self.widget.checkGlobal.isChecked():
			for i, (encendido, apagado) in enumerate(zip(encendidos, apagados)):
				horario = Horario(self.bomba.getIdGrupo, i + 1, encendido.time().toString(), apagado.time().toString())
				horarios.append(horario)
			for i, (horarioNew, horarioOld, checkbox) in enumerate(zip(horarios, self.horarios, checkboxes)):
				if checkbox.checkState() == 0:
					horarioNew.setHoraApagado("00:00:00")
					horarioNew.setHoraEncendido("00:00:00")
				if not (horarioNew == horarioOld):
					if not (horarioNew.getHoraEncendidoString == horarioOld.getHoraEncendidoString):
						cadena = '{"Tipo":"Config","Cadena":"WQ1%s%d"}' % (horarioNew.getHoraEncendido.toString(
							"hhmm"), i + 1)
						Publisher().publicar(topic, cadena, password)
						self.horarios[i] = horarioNew
						print("publicado")
					if not (horarioNew.getHoraApagadoString == horarioOld.getHoraApagadoString):
						cadena = '{"Tipo":"Config","Cadena":"WQ0%s%d"}' % (
						horarioNew.getHoraApagado.toString("hhmm"), i + 1)
						Publisher().publicar(topic, cadena, password)
						self.horarios[i] = horarioNew
						print("publicado")
		else:
			horario = Horario(self.bomba.getIdGrupo, 0, self.widget.encendidoLunes.time().toString(), self.widget.apagadoLunes.time().toString())
			cadena = '{"Tipo":"Config","Cadena":"WQ1%s%d"}' % (horario.getHoraEncendido.toString(
				"hhmm"), 0)
			Publisher().publicar(topic, cadena, password)
			cadena = '{"Tipo":"Config","Cadena":"WQ0%s%d"}' % (horario.getHoraApagado.toString(
				"hhmm"), 0)
			Publisher().publicar(topic, cadena, password)
			for i, (encendido, apagado) in enumerate(zip(encendidos, apagados)):
				self.horarios[i] = horario
				encendido.setTime(horario.getHoraEncendido)
				apagado.setTime(horario.getHoraApagado)

	def cargarHorarios(self):
		self.horarios = []
		for i in range(1, 8):
			horario = Horario(self.bomba.getIdGrupo, i, "00:00:00", "00:00:00")
			self.horarios.append(horario)
		horariosConsultados = self.online.consultarHorarios(self.bomba.getIdGrupo)
		for horarioConsultado in horariosConsultados:
			self.horarios[horarioConsultado.getDia - 1].setHoraApagado(horarioConsultado.getHoraApagadoString)
			self.horarios[horarioConsultado.getDia - 1].setHoraEncendido(horarioConsultado.getHoraEncendidoString)
		encendidos = (
			self.widget.encendidoLunes, self.widget.encendidoMartes, self.widget.encendidoMiercoles, self.widget.encendidoJueves,
			self.widget.encendidoViernes, self.widget.encendidoSabado, self.widget.encendidoDomingo)
		apagados = (
			self.widget.apagadoLunes, self.widget.apagadoMartes, self.widget.apagadoMiercoles, self.widget.apagadoJueves, self.widget.apagadoViernes,
			self.widget.apagadoSabado, self.widget.apagadoDomingo)
		for horario in self.horarios:
			encendidos[horario.getDia - 1].setTime(horario.getHoraEncendido)
			apagados[horario.getDia - 1].setTime(horario.getHoraApagado)
