from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QLabel

class BusyIcon(QLabel):

	def __init__(self, layout, inverted = False):
		QLabel.__init__(self)
		self.setAlignment(Qt.AlignRight)
		layout.addWidget(self)
		self.inverted = inverted

	def startAnimation(self):
		#movie = QMovie(":Varios/icons/valve60fps.mp4")
		movie = QMovie(":Varios/icons/loading.gif")
		if self.inverted:
			movie = QMovie(":Varios/icons/loading-i.gif")
		movie.setScaledSize(QSize(30,30))
		self.setMovie(movie)
		movie.start()

	def show(self):
		self.setVisible(True)

	def hide(self):
		self.setVisible(False)