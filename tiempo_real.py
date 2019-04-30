# -*- coding: UTF8 -*-

import datetime
import os
import time

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from .abstract_worker import *

class TiempoReal(AbstractWorker,QObject):

	signalActualizar= pyqtSignal()

	def __init__(self):
		AbstractWorker.__init__(self)
		QObject.__init__(self)
		self.stopped = False
		self.apuntador = 0

	def work(self):
		self.signalActualizar.emit()
		while (not self.stopped):
			if self.comprobarHora(): #OPTIMIZAR CON HILOS
				self.signalActualizar.emit()
			time.sleep(10)

	def stop(self):
		self.stopped = True

	def comprobarHora(self):
		minuto = datetime.datetime.now().minute
		if (minuto % 1) == 0:
			return True
		else:
			return False