from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QStyle, QStyleOption, QWidget

class CustomQWidget(QWidget):

    signalDibujado = pyqtSignal()

    def __init__(self,parent=None):
        #QWidget.__init__(self)
        super().__init__(parent)

    def paintEvent(self,event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget,opt,painter,self)
        self.signalDibujado.emit()
        return super().paintEvent(event)