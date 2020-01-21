# -*- coding: UTF8 -*-

from .html_widget_item import HtmlWidgetItem

class FechaWidgetItem(HtmlWidgetItem):

	def __init__(self,dateAndTime):
		(texto,css) = self.__build(dateAndTime)
		HtmlWidgetItem.__init__(self,texto,css)
		self.__dateAndTime = dateAndTime

	def __build(self,dateAndTime):
		if dateAndTime.strftime("%d-%b")[-1] == '.':
			mes = dateAndTime.strftime("%d-%b")[0:-1]
		else:
			mes = dateAndTime.strftime("%d-%b")
		texto = "<div class='time'>%shrs</div><br>%s-%s" % (dateAndTime.strftime("%H:%M"),mes,dateAndTime.strftime("%Y"))
		css = ".time{text-align:right; font-size: 9pt; font-weight: bold;} .number{text-align:right; font-size: 5.5pt; color: #cdcdcd;}"
		return (texto,css)

	def dateAndTime(self):
		return self.__dateAndTime
