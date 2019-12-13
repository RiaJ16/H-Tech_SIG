

class DescargadorFotos:

	def actualizarFoto(self, filename):
		foto = QPixmap(filename)
		if foto.isNull():
			url = filename.split('/')
			url = url[len(url)-1]
			t1 = threading.Thread(target=self.online.descargarFoto,args=(url,filename))
			t1.start()
			#self.online.descargarFoto(url,filename)
			foto = QPixmap(filename)
		newHeight = 80
		try:
			newWidth = foto.width()*newHeight/foto.height()
		except:
			newWidth = 0
		if newWidth > 154:
			newWidth = 154
			newHeight = foto.height()*newWidth/foto.width()
		#self.labelFoto.setPixmap(foto.scaled(newWidth,newHeight))
		self.botonFoto.setIcon(QIcon(foto.scaled(newWidth,newHeight)))
		self.botonFoto.setIconSize(QSize(newWidth,newHeight))
		self.adjustSize()
		self.adjustSize()
		newWidth = foto.width()
		newHeight = foto.height()
		screenSize = ctypes.windll.user32.GetSystemMetrics(0)*3/4, ctypes.windll.user32.GetSystemMetrics(1)*3/4
		if newWidth > screenSize[0]:
			newWidth = screenSize[0]
			newHeight = newHeight * newWidth / foto.width()
		unmodifiedNewHeight = newHeight
		if newHeight > screenSize[1]:
			newHeight = screenSize[1]
			newWidth = newWidth * newHeight / unmodifiedNewHeight
		html = "<p><img src=\'%s' width='%f' height='%f'></p>" % (filename,newWidth,newHeight)
		#self.labelFoto.setToolTip(html)
		#self.botonFoto.setToolTip(html)
		self.fotoFlotante.setFixedSize(newWidth, newHeight)
		self.fotoFlotante.setText(html)