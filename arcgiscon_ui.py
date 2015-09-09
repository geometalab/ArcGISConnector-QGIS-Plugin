# -*- coding: utf-8 -*-
"""
/***************************************************************************
ArcGIS REST API Connector
A QGIS plugin
                              -------------------
        begin                : 2015-05-27
        git sha              : $Format:%H$
        copyright            : (C) 2015 by geometalab
        email                : geometalab@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import time

from PyQt4 import QtGui, uic, QtCore

FORM_CLASS_NEW, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'arcgiscon_dialog_new.ui'))



class ArcGisConDialogNew(QtGui.QDialog, FORM_CLASS_NEW):
    def __init__(self, parent=None):        
        super(ArcGisConDialogNew, self).__init__(parent)        
        self.setupUi(self)        
    
#     def startWorker(self):            
#         worker = TestWorker()
#         thread = QtCore.QThread(self)
#         worker.moveToThread(thread)
#         worker.finished.connect(self.workerFinished)        
#         thread.started.connect(worker.process)               
#         self.thread = thread
#         self.worker = worker
#         thread.start()
        
#             # create a new worker instance
#             worker = TestWorker()
#         
#             # configure the QgsMessageBar
#             messageBar = self.iface.messageBar().createMessage('Doing something time consuming...', )
#             progressBar = QtGui.QProgressBar()
#             progressBar.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
#             cancelButton = QtGui.QPushButton()
#             cancelButton.setText('Cancel')
#             cancelButton.clicked.connect(worker.kill)
#             messageBar.layout().addWidget(progressBar)
#             messageBar.layout().addWidget(cancelButton)
#             self.iface.messageBar().pushWidget(messageBar, self.iface.messageBar().INFO)
#             self.messageBar = messageBar
#         
#             # start the worker in a new thread
#             thread = QtCore.QThread(self)            
#             worker.moveToThread(thread)
#             worker.finished.connect(self.workerFinished)
#             worker.error.connect(self.workerError)
#             worker.progress.connect(progressBar.setValue)
#             thread.started.connect(worker.run)                        
#             thread.start()
#             self.thread = thread
#             self.worker = worker
#             
#     def workerFinished(self):
#         QtGui.QMessageBox.information(None, "DEBUG:", "finished")        
#                         
#     def workerError(self, e, message):
#         QtGui.QMessageBox.information(None, "DEBUG:", "error")