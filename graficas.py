# -*- coding: utf-8 -*-

import sys, locale, datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import numpy as np

class Graficas:

	def __init__(self,tipoSensor):
		locale.setlocale(locale.LC_ALL,'esm') #podría dar problemas con Linux
		self.tipoSensor = tipoSensor

	def graficar(self,x,y,dt,periodo,maximo):
		#plt.fill_between()
		fig, ax = plt.subplots(1)
		#ax.plot(x,y, color='#1F77B4')
		ax.fill_between(x,0,y,color='#1F77B4')
		colores = ['#1F77B4','#FF7F0E','#2CA02C','#D62728','#9467BD','#8C564B','#E377C2','#7F7F7F','#BCBD22','#17BECF']
		i=0
		for a, b in zip(x,y):
			#ax.plot([a,a],[0,b],color=colores[i])
			ax.plot([a],[b],color=colores[i],marker='.')
			i+= 1
			if i>9:
				i=0
		ax.axis('tight')
		ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%b %H:%M'))
		fig.autofmt_xdate()
		plt.grid(True)
		plt.xlabel("Fecha y hora")
		if self.tipoSensor == 1:
			plt.ylabel(u"Presión (mca)")
			#plt.title(u"Gráfica de presión")
		elif self.tipoSensor == 2:
			plt.ylabel("Flujo (litros/s)")
			plt.title(u"Gráfica de flujo")
		elif self.tipoSensor == (3 or 4):
			plt.ylabel(u"Nivel (m)")
			#plt.title(u"Gráfica de nivel")
		plt.yticks(np.round(np.arange(0, maximo+(maximo/10), maximo/10),decimals=2))
		ax.set_xlim(dt[0],dt[1])
		if periodo == 0:
			ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
			daterange = np.array([dt[0] + datetime.timedelta(minutes=i*3) for i in range(16)])
		elif periodo == 1:
			ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
			daterange = np.array([dt[0] + datetime.timedelta(hours=i*2) for i in range(13)])
			plt.xticks(daterange)
		elif periodo == 2:
			ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%b'))
			daterange = np.array([dt[0] + datetime.timedelta(days=i*2) for i in range(16)])
			plt.xticks(daterange)
		ax.fmt_xdata = mdates.DateFormatter('%d/%B/%Y %H:%Mhrs.')
		#formatter = mdates.AutoDateFormatter(mpl.ticker.LinearLocator())
		#formatter.scaled[1/(24.*60.)] = '%M:%S'
		#ax.xaxis.set_major_formatter(formatter)
		fig.show()