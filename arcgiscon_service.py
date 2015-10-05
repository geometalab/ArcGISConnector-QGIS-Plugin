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

from PyQt4 import QtCore, QtGui
from qgis.gui import QgsMessageBar
from arcgiscon_model import EsriVectorQueryFactoy, EsriLayerMetaInformation
from Queue import Queue

import multiprocessing
import math
import json
import os.path
import time
import sys
import shutil


def downloadSource(args):  
    ':type connection:Connection'
    ':type query:EsriQuery'
    connection, query, resultQueue = args
    resultJson = connection.getJson(query)
    if resultQueue is not None:      
        resultQueue.put(1)
    return resultJson  


class EsriUpdateWorker(QtCore.QObject):
    def __init__(self, connection):
        QtCore.QObject.__init__(self)
        self.connection = connection        
    
    @staticmethod
    def create(connection, onSuccess=None, onError=None):
        worker = EsriUpdateWorker(connection)
        if onSuccess is not None:
            worker.onSuccess.connect(onSuccess)
        if onError is not None:
            worker.onError.connect(onError)
        return worker
                
    onSuccess = QtCore.pyqtSignal(basestring)
    onError = QtCore.pyqtSignal(basestring)

class EsriUpdateServiceState:
    Down, Idle, Processing, TearingDown = range(4)


class EsriUpdateService(QtCore.QObject):    
    connectionPool = None    
    _thread = None
    _iface = None
    _isKilled = None  
    state = None
    
    _messageBar = None
    _progressBar = None
    
    _projectId = None
      
    #because http json response with features over 1000 is too large, 
    #we limit the max features per request to 1000
    _maxRecordCount = 1000   
         
    def __init__(self, iface):
        QtCore.QObject.__init__(self)        
        self._isKilled = False
        self._iface = iface
        self.state = EsriUpdateServiceState.Down
        self.connectionPool = Queue()
        
    @staticmethod
    def createService(iface):
        service = EsriUpdateService(iface)            
        return service
    
    def updateProjectId(self, projectId):
        self._projectId = projectId
    
    def update(self, worker):        
        while (self.state == EsriUpdateServiceState.TearingDown):
            time.sleep(0.1)
        self.connectionPool.put(worker)
        if self.isDown():
            self.start()
    
    def start(self):        
        self.state = EsriUpdateServiceState.Idle                
        self._isKilled = False
        self._createMessageBarWidget()
        thread = QtCore.QThread()        
        self.moveToThread(thread)
        thread.started.connect(self.runUpdateWorker)
        thread.start()
        self._thread = thread
        
    def isDown(self):
        return self.state == EsriUpdateServiceState.Down
                
    def kill(self):
        self._isKilled = True  
        
    def tearDown(self):        
        self.state = EsriUpdateServiceState.TearingDown
        self._removeMessageBarWidget()
        self._thread.quit() 
        self._thread.wait()
        self._thread = None                
        self.state = EsriUpdateServiceState.Down
        
                                                 
    def runUpdateWorker(self):                                 
        while (not self.connectionPool.empty() or self.state == EsriUpdateServiceState.Processing) and not self._isKilled:
            try:   
                if self.state == EsriUpdateServiceState.Idle:
                    self.state = EsriUpdateServiceState.Processing
                    currentJob = self.connectionPool.get()         
                    totalRecords = self._getTotalRecords(currentJob.connection)
                    if totalRecords > 0: 
                        query = EsriVectorQueryFactoy.createMetaInformationQuery()
                        metaJson = currentJob.connection.getJson(query)
                        metaInfo = EsriLayerMetaInformation.createFromMetaJson(metaJson)                        
                        maxRecordCount = metaInfo.maxRecordCount if 0 < metaInfo.maxRecordCount < self._maxRecordCount else self._maxRecordCount                                                                                                                                                       
                        pages = int(math.ceil(float(totalRecords) / float(maxRecordCount)))
                        self.progress.emit(10)
                        results = []
                        if pages == 1 or not metaInfo.supportsPagination:
                            #if server doesn't support pagination and there are more features than we can retrieve within one single server call, warn user.                             
                            if(totalRecords > float(maxRecordCount)):
                                currentJob.onError.emit(QtCore.QCoreApplication.translate('ArcGisConService', "Not all features could be retrieved. Please adjust extent or use a filter."))                                                   
                            query = EsriVectorQueryFactoy.createFeaturesQuery(currentJob.connection.bbBox, currentJob.connection.customFiler)
                            results = [downloadSource((currentJob.connection, query, None))]
                        else:
                            queries = []
                            for page in range(0,pages):            
                                queries.append(EsriVectorQueryFactoy.createPagedFeaturesQuery(page, maxRecordCount, currentJob.connection.bbBox, currentJob.connection.customFiler))                                                                        
                            results = self._downloadSources(queries, currentJob.connection)
                        self.progress.emit(90)                        
                        if results is not None and not self._isKilled:
                            filePath = self._processSources(results, currentJob.connection)
                            currentJob.onSuccess.emit(filePath)
                        self.progress.emit(100)    
                        self.state = EsriUpdateServiceState.Idle 
                        self._isKilled = False
                    else:  
                        currentJob.onError.emit(QtCore.QCoreApplication.translate('ArcGisConService', "Layer has no features (with the current extent). Nothing has been updated."))                                                          
                        self.state = EsriUpdateServiceState.Idle                                        
            except Exception as e:      
                currentJob.onError.emit(str(e))
                self.state = EsriUpdateServiceState.Idle
                self._isKilled = False                                                                                 
        self.finished.emit()
       
       

    def _downloadSources(self, queries, connection):        
        #workaround for windows qis bug (http://gis.stackexchange.com/questions/35279/multiprocessing-error-in-qgis-with-python-on-windows)
        if os.name == "nt":
            path = os.path.abspath(os.path.join(sys.exec_prefix, '../../bin/pythonw.exe'))
            multiprocessing.set_executable(path)
            sys.argv = [ None ]  
        workerPool = multiprocessing.Pool(multiprocessing.cpu_count())
        manager = multiprocessing.Manager()
        resultQueue = manager.Queue()
        args = [(connection, query, resultQueue) for query in queries]
        workingMap = workerPool.map_async(downloadSource,args)
        progressStepFactor = 80.0 / len(queries)                  
        while not self._isKilled:
            if(workingMap.ready()):                                
                break
            else:
                size = resultQueue.qsize()                                                              
                self.progress.emit(10+size*progressStepFactor)             
        if self._isKilled:
            workerPool.terminate()
        else:
            workerPool.close()
            workerPool.join()                 
        toReturn = None            
        if not self._isKilled:
            toReturn = workingMap.get()        
        return toReturn
    
    def _processSources(self, sources, connection):        
        combined = {}
        progressStepFactor = 10.0 / len(sources)
        if len(sources) > 0:            
            base = sources[0] 
            step = 1                                
            for nextResult in sources[1:]:                
                if self._isKilled:
                    break                             
                if u'features' in base and u'features' in nextResult:                     
                    base[u'features'].extend(nextResult[u'features'])
                self.progress.emit(90+step*progressStepFactor)
                step += 1                                
            combined = base
        
        if not self._isKilled:
            filePath = None
            if self._projectId is not None:
                filePath = FileSystemService().storeJsonInProjectFolder(combined, connection.createSourceFileName(), self._projectId)
            else:
                filePath = FileSystemService().storeJsonInTmpFolder(combined, connection.createSourceFileName())
            return filePath            
                   
    def _getMaxRecordCount(self, connection):
        maxRecordCount = self._maxRecordCount
        query = EsriVectorQueryFactoy.createMetaInformationQuery()
        metaJson = connection.getJson(query)   
        if u'maxRecordCount' in metaJson:
            count = int(metaJson[u'maxRecordCount'])                                    
            maxRecordCount = count if 0 < count < self._maxRecordCount else maxRecordCount        
        return maxRecordCount
        
    def _getTotalRecords(self, connection):                                
        totalRecords = 0
        query = EsriVectorQueryFactoy.createTotalFeatureCountQuery(connection.bbBox, connection.customFiler)            
        metaJson = connection.getJson(query)                    
        if u'count' in metaJson:                
            totalRecords = int(metaJson[u'count'])
        return totalRecords
    
    def _createMessageBarWidget(self):
        messageBar = self._iface.messageBar().createMessage(QtCore.QCoreApplication.translate('ArcGisConService', 'processing arcgis data...'),)
        progressBar = QtGui.QProgressBar()
        progressBar.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.progress.connect(self._adjustProgress)
        cancelButton = QtGui.QPushButton()
        cancelButton.setText(QtCore.QCoreApplication.translate('ArcGisConService', 'Cancel'))
        cancelButton.clicked.connect(self.kill)
        messageBar.layout().addWidget(progressBar)
        messageBar.layout().addWidget(cancelButton)
        self._iface.messageBar().pushWidget(messageBar, self._iface.messageBar().INFO)
        self._messageBar = messageBar
        self._progressBar = progressBar
              
    def _removeMessageBarWidget(self):
        self.progress.disconnect(self._adjustProgress)
        self._iface.messageBar().popWidget(self._messageBar)
        self._messageBar = None        
    
    def _adjustProgress(self, value):        
        self._progressBar.setValue(value)
            
    finished = QtCore.pyqtSignal()
    #progress is linked with progress bar and expects number 
    #between 0=0% and 100=100%
    progress = QtCore.pyqtSignal(float)
    
    
class FileSystemService:
    
    arcGisJsonSrc = os.path.join(os.path.dirname(__file__),"arcgisjsonsrc")    
    tmpFolderName = "tmp"
    
    def storeJsonInTmpFolder(self, jsonFile, jsonFileName):
        tmpPath = os.path.join(self.arcGisJsonSrc, self.tmpFolderName)
        self._createFolderIfNotExists(tmpPath)
        filePath = os.path.join(tmpPath, jsonFileName)
        self._storeJson(jsonFile, filePath)
        return filePath
    
    def storeJsonInProjectFolder(self, jsonFile, jsonFileName, projectId):
        projectDir = os.path.join(self.arcGisJsonSrc,projectId)
        self._createFolderIfNotExists(projectDir)
        filePath = os.path.join(projectDir, jsonFileName)
        self._storeJson(jsonFile, filePath)
        return filePath
      
    def removeDanglingFilesFromProjectDir(self, existingFileNames, projectId):        
        projectPath = os.path.join(self.arcGisJsonSrc, projectId)
        self._createFolderIfNotExists(projectPath)
        filePaths = [os.path.join(projectPath, fileName) for fileName in existingFileNames]
        for existingName in os.listdir(projectPath):
            existingPath = os.path.join(self.arcGisJsonSrc, projectId, existingName)
            if existingPath not in filePaths:
                if os.path.isfile(existingPath):
                    os.unlink(existingPath)  
    
    def moveFileFromTmpToProjectDir(self, fileName, projectId):               
        pathToReturn = None 
        srcPath = os.path.join(self.arcGisJsonSrc,self.tmpFolderName, fileName)
        if os.path.isfile(srcPath):
            tarPath = os.path.join(self.arcGisJsonSrc, projectId)
            if not os.path.isfile(tarPath):
                self._createFolderIfNotExists(tarPath)
                shutil.copy2(srcPath, tarPath)
            pathToReturn = os.path.join(tarPath,fileName)
        return pathToReturn
    
    def clearAllFilesFromTmpFolder(self):
        tmpPath = os.path.join(self.arcGisJsonSrc, self.tmpFolderName)
        if os.path.isdir(tmpPath):
            for fileName in os.listdir(tmpPath):
                filePath = os.path.join(tmpPath, fileName)
                if os.path.isfile(filePath):
                    os.unlink(filePath)                
    
    def _storeJson(self, jsonFile, filePath):                
        with open(filePath, 'w+') as outfile:
            json.dump(jsonFile, outfile)
        
    
    def _createFolderIfNotExists(self, folderPath):
        if not os.path.isdir(folderPath):
            os.makedirs(folderPath)
    
    

class NotificationHandler:
    
    _iface = None
    _duration = 4
    
    @classmethod
    def configureIface(cls, iface):        
        cls._iface = iface
    
    @classmethod    
    def pushError(cls, title, message, duration=None):
        cls._checkConfiguration()        
        cls._pushMessage(title, message, QgsMessageBar.CRITICAL, duration)
        
    @classmethod    
    def pushWarning(cls, title, message, duration=None):
        cls._checkConfiguration()
        cls._pushMessage(title, message, QgsMessageBar.WARNING, duration)
        
    @classmethod  
    def pushSuccess(cls, title, message, duration=None):
        cls._checkConfiguration()
        cls._pushMessage(title, message, QgsMessageBar.SUCCESS, duration)   
    
    @classmethod  
    def pushInfo(cls, title, message, duration=None):
        cls._checkConfiguration()
        cls._pushMessage(title, message, QgsMessageBar.INFO, duration)        
    
    @classmethod  
    def _pushMessage(cls, title, message, messageLevel, duration=None):
        duration = duration if duration is not None else cls._duration
        cls._iface.messageBar().pushMessage(title, message, level=messageLevel, duration=duration)
    
    @classmethod 
    def _checkConfiguration(cls):
        if not cls._iface:
            raise RuntimeError("iface is not configured")
        