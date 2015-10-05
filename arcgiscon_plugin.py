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
from PyQt4.QtCore import QTranslator, qVersion, QCoreApplication, QSettings
from PyQt4.QtGui import QAction, QIcon, QApplication

from qgis.core import QgsMapLayer, QgsMapLayerRegistry, QgsProject
import resources_rc

from arcgiscon_service import NotificationHandler, EsriUpdateService,\
    FileSystemService
from arcgiscon_controller import ArcGisConNewController, ArcGisConRefreshController
from arcgiscon_model import EsriVectorLayer
from uuid import uuid4
import os.path

# import sys;
# sys.path.append(r'/Applications/liclipse/plugins/org.python.pydev_3.9.2.201502042042/pysrc')
# import pydevd

class ArcGisConnector:
#     pydevd.settrace()       
    _iface = None    
    _newLayerAction = None
    _newLayerActionText = None    
    _arcGisRefreshLayerAction = None
    _arcGisRefreshLayerWithNewExtentAction = None    
    _pluginDir = None
    _esriVectorLayers = None
    _updateService = None
    _qSettings = None
    
    def __init__(self, iface):            
        self._iface = iface        
        self._pluginDir = os.path.dirname(__file__)
        self._qSettings = QSettings()
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self._pluginDir,'i18n','arcgiscon_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        NotificationHandler.configureIface(iface)
        self._esriVectorLayers = {}
        self._iface.projectRead.connect(self._onProjectLoad)        
        self._updateService = EsriUpdateService.createService(iface)
        self._updateService.finished.connect(self._updateServiceFinished)      
        self._newController = ArcGisConNewController(iface)
        self._refreshController = ArcGisConRefreshController(iface)                         
        QgsMapLayerRegistry.instance().layerRemoved.connect(self._onLayerRemoved)
        QgsProject.instance().writeProject.connect(self._onProjectInitialWrite)
        QgsProject.instance().projectSaved.connect(self._onProjectSaved)
        self._connectToRefreshAction()
                      
    def initGui(self):
        newLayerActionIcon = QIcon(':/plugins/arcgiscon/arcgis.png')
        self._newLayerActionText = QCoreApplication.translate('arcgiscon', 'arcgiscon')
        self._newLayerAction = QAction(newLayerActionIcon, self._newLayerActionText, self._iface.mainWindow())
        self._newLayerAction.triggered.connect(lambda: self._newController.createNewConnection(self._updateService, self._esriVectorLayers, [self._arcGisRefreshLayerAction,self._arcGisRefreshLayerWithNewExtentAction]))
        try:
            self._iface.layerToolBar().addAction(self._newLayerAction)
        except:
            self._iface.addToolBarIcon(self._newLayerAction)   
        self._iface.addPluginToVectorMenu(self._newLayerActionText, self._newLayerAction)
        self._arcGisRefreshLayerAction = QAction( QCoreApplication.translate('ArcGisConnector', 'refresh from source'), self._iface.legendInterface() )
        self._arcGisRefreshLayerWithNewExtentAction = QAction( QCoreApplication.translate('ArcGisConnector', 'refresh from source with current extent'), self._iface.legendInterface() )
        self._iface.legendInterface().addLegendLayerAction(self._arcGisRefreshLayerAction, QCoreApplication.translate('ArcGisConnector', 'ArcGIS'), u"id1", QgsMapLayer.VectorLayer, False )
        self._iface.legendInterface().addLegendLayerAction(self._arcGisRefreshLayerWithNewExtentAction, QCoreApplication.translate('ArcGisConnector', 'ArcGIS'), u"id1", QgsMapLayer.VectorLayer, False )
        self._arcGisRefreshLayerAction.triggered.connect(self._refreshEsriLayer)
        self._arcGisRefreshLayerWithNewExtentAction.triggered.connect(lambda: self._refreshEsriLayer(True))
            
    def _connectToRefreshAction(self):
        for action in self._iface.mapNavToolToolBar().actions():
            if action.objectName() == "mActionDraw":
                action.triggered.connect(self._refreshAllEsriLayers)
                
    def _refreshAllEsriLayers(self): 
        for layer in self._esriVectorLayers.values():
            self._refreshController.updateLayer(self._updateService, layer)
    
    def _refreshEsriLayer(self, withCurrentExtent=False):
        qgsLayers = self._iface.legendInterface().selectedLayers()
        for layer in qgsLayers:
            if layer.id() in self._esriVectorLayers:  
                if withCurrentExtent:      
                    self._refreshController.updateLayerWithNewExtent(self._updateService, self._esriVectorLayers[layer.id()])
                else:
                    self._refreshController.updateLayer(self._updateService, self._esriVectorLayers[layer.id()])
                
    def _onProjectLoad(self): 
        projectId = str(QgsProject.instance().readEntry("arcgiscon","projectid","-1")[0])
        if  projectId != "-1":                                
            self._reconnectEsriLayers()
            FileSystemService().removeDanglingFilesFromProjectDir([layer.connection.createSourceFileName() for layer in self._esriVectorLayers.values()], projectId)
            self._updateService.updateProjectId(projectId)            
        
    def _onProjectInitialWrite(self):
        projectId = str(QgsProject.instance().readEntry("arcgiscon","projectid","-1")[0])
        if projectId == "-1" and self._esriVectorLayers:
            projectId = uuid4().hex
            for esriLayer in self._esriVectorLayers.values():                
                newSrcPath = FileSystemService().moveFileFromTmpToProjectDir(esriLayer.connection.createSourceFileName(), projectId)
                if newSrcPath is not None:
                    esriLayer.qgsVectorLayer.setDataSource(newSrcPath, esriLayer.qgsVectorLayer.name(),"ogr")            
            QgsProject.instance().writeEntry("arcgiscon","projectid",projectId)
            self._updateService.updateProjectId(projectId)                    
    
    def _onProjectSaved(self):
        projectId = str(QgsProject.instance().readEntry("arcgiscon","projectid","-1")[0])
        if projectId != "-1":
            FileSystemService().removeDanglingFilesFromProjectDir([layer.connection.createSourceFileName() for layer in self._esriVectorLayers.values()], projectId)
                        
    def _reconnectEsriLayers(self):
        layers = QgsMapLayerRegistry.instance().mapLayers()                
        for qgsLayer in layers.itervalues():            
            if qgsLayer.customProperty('arcgiscon_connection_url', ''):                
                try:
                    esriLayer = EsriVectorLayer.restoreFromQgsLayer(qgsLayer)
                    self._esriVectorLayers[qgsLayer.id()] = esriLayer
                    self._iface.legendInterface().addLegendLayerActionForLayer(self._arcGisRefreshLayerAction, qgsLayer)
                    self._iface.legendInterface().addLegendLayerActionForLayer(self._arcGisRefreshLayerWithNewExtentAction, qgsLayer)
                except: 
                    raise
                                                  
    def _updateServiceFinished(self):            
        self._updateService.tearDown()
        #move back to main GUI thread
        self._updateService.moveToThread(QApplication.instance().thread())
                  
    def _onLayerRemoved(self, layerId):
        if layerId in self._esriVectorLayers:
            del self._esriVectorLayers[layerId]
         
    def unload(self):
        FileSystemService().clearAllFilesFromTmpFolder()
        self._iface.removePluginMenu(
            QCoreApplication.translate('arcgiscon', 'arcgiscon'),
            self._newLayerAction)
        self._iface.removePluginVectorMenu(self._newLayerActionText, self._newLayerAction)
        self._iface.removeToolBarIcon(self._newLayerAction)        
        self._iface.legendInterface().removeLegendLayerAction(self._arcGisRefreshLayerAction)
        

