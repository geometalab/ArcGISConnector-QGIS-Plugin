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
from qgis.core import QgsMapLayerRegistry
from PyQt4.QtCore import QObject, QCoreApplication
from arcgiscon_ui import ArcGisConDialogNew
from arcgiscon_model import Connection, EsriVectorLayer, EsriConnectionJSONValidatorLayer
from arcgiscon_service import NotificationHandler, EsriUpdateWorker
from Queue import Queue


class ArcGisConNewController(QObject):

	_newDialog = None
	_esriVectorLayers = None
	_iface = None
	_connection = None
	_legendActions = None
	
	_updateService = None
	
	def __init__(self, iface):
		QObject.__init__(self)
		self._iface = iface				
		self._newDialog = ArcGisConDialogNew()		
		self._newDialog.cancelButton.clicked.connect(self._newDialog.reject)
		self._newDialog.connectButton.clicked.connect(self._checkConnection)		
		self._updateWorkerPool = Queue()		
			
	def createNewConnection(self, updateService, esriVectorLayers, legendActions):
		self._esriVectorLayers = esriVectorLayers
		self._legendActions = legendActions
		self._updateService = updateService		
		self._resetInputValues()
		self._newDialog.show()		
		self._newDialog.exec_()
																		
	def _checkConnection(self):
		url = self._newDialog.layerUrlInput.text()
		name = self._newDialog.layerNameInput.text()
		username = self._newDialog.usernameInput.text()
		password = self._newDialog.passwordInput.text()
			
		connection = Connection.createAndConfigureConnection(url, name, username, password)
		try:
			connection.validate(EsriConnectionJSONValidatorLayer() )
			if self._newDialog.extentOnly.isChecked():
				mapCanvas = self._iface.mapCanvas()
				connection.updateBoundingBoxByRectangle(mapCanvas.extent(), mapCanvas.mapRenderer().destinationCrs().toWkt())				
			self._newDialog.connectionErrorLabel.setText("")
			self._requestLayerForConnection(connection)						
			self._newDialog.accept()
		except Exception as e:
			self._newDialog.connectionErrorLabel.setText(str(e.message))
			
	def _requestLayerForConnection(self, connection):
		updateWorker = EsriUpdateWorker.create(connection, lambda srcPath: self.onSuccess(srcPath, connection), self.onError)							
		self._updateService.update(updateWorker)		
		
	def onSuccess(self, srcPath, connection):		
		esriLayer = EsriVectorLayer.create(connection, srcPath)		
		for action in self._legendActions:
			self._iface.legendInterface().addLegendLayerActionForLayer(action, esriLayer.qgsVectorLayer)
		QgsMapLayerRegistry.instance().addMapLayer(esriLayer.qgsVectorLayer)
		self._esriVectorLayers[esriLayer.qgsVectorLayer.id()]=esriLayer
			
	def onError(self, errorMessage):
		NotificationHandler.pushError(QCoreApplication.translate('ArcGisConController', 'Worker thread:'), errorMessage)
		
	def _resetInputValues(self):
		self._newDialog.layerUrlInput.setText("")
		self._newDialog.layerNameInput.setText("")
		self._newDialog.usernameInput.setText("")
		self._newDialog.passwordInput.setText("")
		self._newDialog.connectionErrorLabel.setText("")
		self._newDialog.extentOnly.setChecked(False)
		
	def _resetConnectionErrorStatus(self):
		self._newDialog.connectionErrorLabel.setText("")
		
class ArcGisConRefreshController(QObject):
	_iface = None

	def __init__(self, iface):
		QObject.__init__(self)
		self._iface = iface

	def updateLayer(self, updateService, esriLayer):
		if not esriLayer.connection is None:
			worker = EsriUpdateWorker.create(esriLayer.connection, None, self.onError)			
			updateService.update(worker)
			
	def updateLayerWithNewExtent(self, updateService, esriLayer):
		if not esriLayer.connection is None:
			mapCanvas = self._iface.mapCanvas()
			esriLayer.connection.updateBoundingBoxByRectangle(mapCanvas.extent(), mapCanvas.mapRenderer().destinationCrs().toWkt())
			esriLayer.updateProperties()			
			worker = EsriUpdateWorker.create(esriLayer.connection, lambda newSrcPath: self.onUpdateLayerWithNewExtentSuccess(newSrcPath, esriLayer), self.onError)			
			updateService.update(worker)
			
	def onUpdateLayerWithNewExtentSuccess(self, newSrcPath, esriLayer):
		esriLayer.qgsVectorLayer.setDataSource(newSrcPath, esriLayer.qgsVectorLayer.name(),"ogr")
																	
	def onError(self, errorMessage):
		NotificationHandler.pushError(QCoreApplication.translate('ArcGisConController', 'Worker thread:'), errorMessage, 10)		
		
		