import time
import traceback
from random import randint
 
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QProgressBar, QPushButton
 
from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar

class AbstractWorker(QtCore.QObject):
    """Abstract worker, ihnerit from this and implement the work method"""
 
    # available signals to be used in the concrete worker
    finished = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(Exception, basestring)
    progress = QtCore.pyqtSignal(float)
    toggle_show_progress = QtCore.pyqtSignal(bool)
    set_message = QtCore.pyqtSignal(str)
    toggle_show_cancel = QtCore.pyqtSignal(bool)
    
    # private signal, don't use in concrete workers this is automatically
    # emitted if the result is not None
    successfully_finished = QtCore.pyqtSignal(object)
 
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.killed = False
 
    def run(self):
        try:
            result = self.work()
            self.finished.emit(result)
        except UserAbortedNotification:
            self.finished.emit(None)
        except Exception as e:
            # forward the exception upstream
            self.error.emit(e, traceback.format_exc())
            self.finished.emit(None)
 
    def work(self):
        """ Reimplement this putting your calculation here
            available are:
                self.progress.emit(0-100)
                self.killed
            :returns a python object - use None if killed is true
        """
 
        raise NotImplementedError
 
    def kill(self):
        self.is_killed = True
        self.set_message.emit('Aborting...')
        self.toggle_show_progress.emit(False)
 
 
class UserAbortedNotification(Exception):
    pass
 
 
def start_worker(worker, iface, message, with_progress=True):
    # configure the QgsMessageBar
    #message_bar_item = iface.messageBar().createMessage(message)
    progress_bar = QProgressBar()
    progress_bar.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    if not with_progress:
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(0)
    cancel_button = QPushButton()
    cancel_button.setText('Cancel')
    cancel_button.clicked.connect(worker.kill)
    #message_bar_item.layout().addWidget(progress_bar)
    #message_bar_item.layout().addWidget(cancel_button)
    #iface.messageBar().pushWidget(message_bar_item, iface.messageBar().INFO)
 
    # start the worker in a new thread
    # let Qt take ownership of the QThread
    thread = QThread(iface.mainWindow())
    worker.moveToThread(thread)
    
    worker.set_message.connect(lambda message: set_worker_message(
        message, message_bar_item))
 
    worker.toggle_show_progress.connect(lambda show: toggle_worker_progress(
        show, progress_bar))
        
    worker.toggle_show_cancel.connect(lambda show: toggle_worker_cancel(
        show, cancel_button))
        
    worker.finished.connect(lambda result: worker_finished(
        result, thread, worker, iface))
        
    worker.error.connect(lambda e, exception_str: worker_error(
        e, exception_str, iface))
        
    worker.progress.connect(progress_bar.setValue)
    
    thread.started.connect(worker.run)
    
    thread.start()
    return thread#, message_bar_item
 
 
def worker_finished(result, thread, worker, iface):
        # remove widget from message bar
        #iface.messageBar().popWidget(message_bar_item)
        if result is not None:
            # report the result
            iface.messageBar().pushMessage('The result is: %s.' % result)
            worker.successfully_finished.emit(result)
            
        # clean up the worker and thread
        worker.deleteLater()
        thread.quit()
        thread.wait()
        thread.deleteLater()        
        
 
def worker_error(e, exception_string, iface):
    # notify the user that something went wrong
    iface.messageBar().pushMessage(
        'Something went wrong! See the message log for more information.',
        level=QgsMessageBar.CRITICAL,
        duration=3)
    QgsMessageLog.logMessage(
        'Worker thread raised an exception: %s' % exception_string,
        'SVIR worker',
        level=QgsMessageLog.CRITICAL)
 
 
def set_worker_message(message, message_bar_item):
    message_bar_item.setText(message)
 
 
def toggle_worker_progress(show_progress, progress_bar):
    progress_bar.setMinimum(0)
    if show_progress:
        progress_bar.setMaximum(100)
    else:
        # show an undefined progress
        progress_bar.setMaximum(0)
 
        
def toggle_worker_cancel(show_cancel, cancel_button):
    cancel_button.setVisible(show_cancel)