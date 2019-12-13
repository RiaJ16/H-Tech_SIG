from PyQt5.QtWidgets import QListWidgetItem


class IndexedQListWidgetItem(QListWidgetItem):

    def __init__(self,text,index,parent=None):
        QListWidgetItem.__init__(self,text)
        self._index = int(index)
        self._uiShown = False

    def setIndex(self,index):
        self._index = index

    @property
    def getIndex(self):
        return self._index

    def setUiShown(self,flag):
        self._uiShown = flag

    @property
    def isUiShown(self):
        return self._uiShown
