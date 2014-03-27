# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Connector
								 A QGIS plugin
 ArcGIS REST API Connector
							  -------------------
		begin				: 2014-03-25
		copyright			: (C) 2014 by tschmitz HSR
		email				: tschmitz at hsr dot ch
 ***************************************************************************/

/***************************************************************************
 *																		 *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or	 *
 *   (at your option) any later version.								   *
 *																		 *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from connectordialog import ConnectorDialog
import os.path
import distutils.dir_util

import urllib2, base64
import json
import traceback

try:
	_encoding = QApplication.UnicodeUTF8
	def _translate(context, text, disambig):
		return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
	def _translate(context, text, disambig):
		return QApplication.translate(context, text, disambig)

class Connector:

	def warning(self, text):
		return QMessageBox.warning(self.dialog, _translate("Connector", "Warning", None), text, buttons=QMessageBox.Ok, defaultButton=QMessageBox.NoButton)
	def info(self, text):
		return QMessageBox.information(self.dialog, _translate("Connector", "Info", None), text, buttons=QMessageBox.Ok, defaultButton=QMessageBox.NoButton)
	def questionYesNo(self, text):
		return QMessageBox.question(self.dialog, _translate("Connector", "Question", None), text, buttons = QMessageBox.Yes|QMessageBox.No);
	
	def inputBox(self, title, text):
		outputText, ok = QInputDialog.getText(self.dialog, _translate("Connector", title, None), _translate("Connector", text, None))
		if ok:
			return outputText

	def __init__(self, iface):
		# Save reference to the QGIS interface
		self.iface = iface
		# initialize plugin directory
		self.plugin_dir = os.path.dirname(__file__)
		# initialize locale
		self.qgis_bin_dir = os.getcwd()
		try:
			distutils.dir_util.remove_tree(self.plugin_dir+"/tmp")
		except:
			print traceback.format_exc()
		try:
			os.makedirs(self.plugin_dir+"/tmp")
		except:
			print traceback.format_exc()
		
		locale = QSettings().value("locale/userLocale")[0:2]
		localePath = os.path.join(self.plugin_dir, 'i18n', 'connector_{}.qm'.format(locale))

		if os.path.exists(localePath):
			self.translator = QTranslator()
			self.translator.load(localePath)

			if qVersion() > '4.3.3':
				QCoreApplication.installTranslator(self.translator)

		# Create the dialog (after translation) and keep reference
		self.dialog = ConnectorDialog()

	def initGui(self):
		# Create action that will start plugin configuration
		self.action = QAction(
			QIcon(":/plugins/connector/icon.png"),
			u"ArcGIS REST API Connector", self.iface.mainWindow())
		# connect the action to the run method
		self.action.triggered.connect(self.run)
		
		self.dialog.connect(self.dialog.loadServices, SIGNAL("clicked()"), self.loadTreeView)
		self.dialog.connect(self.dialog.importLayers, SIGNAL("clicked()"), self.loadLayer)
		self.dialog.connect(self.dialog.cancelButton, SIGNAL("clicked()"), self.dialog.close)

		self.dialog.password.setEchoMode(QLineEdit.Password);
		

		# Add toolbar button and menu item
		self.iface.addToolBarIcon(self.action)
		self.iface.addPluginToMenu(u"&ArcGIS REST API Connector", self.action)

	def unload(self):
		# Remove the plugin menu item and icon
		self.iface.removePluginMenu(u"&ArcGIS REST API Connector", self.action)
		self.iface.removeToolBarIcon(self.action)

	# run method that performs all the real work
	def run(self):
		# show the dialog
		self.dialog.show()
		# Run the dialog event loop
		self.dialog.exec_()
	
	def getRequestFor(self, url):
		request = urllib2.Request(url)
		base64string = base64.encodestring('%s:%s' % (self.dialog.username.text(), self.dialog.password.text())).replace('\n', '')
		request.add_header("Authorization", "Basic %s" % base64string)
		return request
	
	def populateFolder(self, base, jsonContent, parentItem):
		
		for folder in jsonContent["folders"]:
			newBase = base+"/"+folder
			jsonText = urllib2.urlopen(self.getRequestFor(newBase+"?f=json")).read()
			newJsonContent = json.loads(jsonText)
			
			baseItem = QTreeWidgetItem()
			baseItem.setText(0, folder)
			parentItem.addChild(baseItem)
			self.populateFolder(newBase, newJsonContent, baseItem)
		
		for service in jsonContent["services"]:
			name = service["name"].split("/")[-1]
			baseItem = QTreeWidgetItem()
			baseItem.setToolTip(0, base+"/"+name+"/"+service["type"])
			baseItem.setToolTip(1, name)
			baseItem.setToolTip(2, service["type"])
			baseItem.setText(0, name+" ("+service["type"]+")")
			parentItem.addChild(baseItem)
			
	
	def loadTreeViewFor(self, base, jsonContent):
		baseItem = QTreeWidgetItem()
		baseItem.setText(0, base)
		self.dialog.treeView.addTopLevelItem(baseItem)
		
		self.populateFolder(base, jsonContent, baseItem)
	
	def loadTreeView(self):
		serviceURL = self.dialog.serviceURL.text()
		if not serviceURL:
			return
		if serviceURL == "":
			return
		
		url = self.dialog.protocol.currentText()+self.dialog.serviceURL.text()
		urlJSON = url + "?f=json"
		request = self.getRequestFor(urlJSON)
		
		try:
			jsonText = urllib2.urlopen(request).read()
		except:
			return self.warning(_translate("Connector", "Url not found.", None))
		try:
			jsonContent = json.loads(jsonText)
		except:
			return self.warning(_translate("Connector", "Quering JSON must be allowed on the Server.", None))
		
		self.loadTreeViewFor(url, jsonContent)
	
	def isFeatureLayer(self, item):
		serviceRequest = self.getRequestFor(item.toolTip(0)+"?f=json")
		jsonContent = json.loads(urllib2.urlopen(serviceRequest).read())
		
		for layer in jsonContent["layers"]:
			layerRequest = self.getRequestFor(item.toolTip(0)+"/"+str(layer["id"])+"/"+"?f=json")
			layerJSON = json.loads(urllib2.urlopen(layerRequest).read())
			
			if layerJSON['type'] == "Feature Layer":
				return True
			
		return False
	
	def loadMapServerLayers(self, item):
		serviceRequest = self.getRequestFor(item.toolTip(0)+"?f=json")
		jsonContent = json.loads(urllib2.urlopen(serviceRequest).read())
		
		import XMLWriter
		XMLWriter.url = item.toolTip(0)+"/tile/${z}/${y}/${x}"
		try:
			XMLWriter.latestwkid = jsonContent["tileInfo"]["spatialReference"]["latestWkid"]
		except:
			try:
				XMLWriter.latestwkid = jsonContent["spatialReference"]["latestWkid"]
			except:
				try:
					XMLWriter.latestwkid = jsonContent["spatialReference"]["wkid"]
				except:
					XMLWriter.latestwkid = self.inputBox("Input SRID", "Input SRID")
		try:
			XMLWriter.originX = jsonContent["tileInfo"]["origin"]["x"]
		except:
			if self.isFeatureLayer(item):
				self.loadFeatureLayers(item)
				return
			XMLWriter.originX = self.inputBox("Input the X-Extend", "Input the X-Extend")
		try:
			XMLWriter.originY = jsonContent["tileInfo"]["origin"]["y"]
		except:
			XMLWriter.originY = self.inputBox("Input the Y-Extend", "Input the Y-Extend")
		try:
			XMLWriter.blockX = jsonContent["tileInfo"]["cols"]
		except:
			XMLWriter.blockX = self.inputBox("Image width in pixels", "Image width in pixels")
		try:
			XMLWriter.blockY = jsonContent["tileInfo"]["rows"]
		except:
			XMLWriter.blockY = self.inputBox("Image height in pixels", "Image height in pixels")
		try:
			for layers in jsonContent["tileInfo"]["lods"]:
				anz = layers["level"]
			XMLWriter.anzZooms = anz
		except:
			XMLWriter.anzZooms = self.inputBox("Number of Zoom levels", "Number of Zoom levels")
		with open(self.plugin_dir+"/tmp/"+item.toolTip(1)+".xml", "w") as tmpFile:
			tmpFile.write(XMLWriter.writeFile())
		
		self.iface.addRasterLayer(self.plugin_dir+"/tmp/"+item.toolTip(1)+".xml", item.toolTip(1))
	
	def loadFeatureLayers(self, item):
		serviceRequest = self.getRequestFor(item.toolTip(0)+"?f=json")
		jsonContent = json.loads(urllib2.urlopen(serviceRequest).read())
		
		for layer in jsonContent["layers"]:
			identi = str(layer["id"])
			name = layer["name"]
			
			inputFile = self.plugin_dir+"/tmp/"+item.toolTip(1)+"-QGIS-"+identi+".json"
			outputFile= self.plugin_dir+"/tmp/"+item.toolTip(1)+"-"+identi+".json"
			
			reqURL = item.toolTip(0)+"/"+str(identi)+"/query?where=objectid+%3D+objectid&outfields=*&f=json"
			with open(inputFile, "w") as tmpfile:
				tmpfile.write(urllib2.urlopen(self.getRequestFor(reqURL)).read())
			
			cmands = "ogr2ogr -f GeoJSON "+outputFile+" "+inputFile+" OGRGeoJSON -gt 1000"
			os.popen(cmands.encode("utf-8")).read()
			
			self.iface.addVectorLayer(outputFile, item.toolTip(1)+"-"+name, "ogr")
			
	
	def loadLayer(self):
		item = self.dialog.treeView.currentItem()
		if not item:
			return self.warning("Nothing selected")
		if not item.toolTip(0) or item.toolTip(0)=="":
			return self.warning("Select a Service")
		
		if item.toolTip(2) == "MapServer":
			self.loadMapServerLayers(item)
		else:
			self.loadFeatureLayers(item)
		
		
	
	def passMethod(self):
		if 1 == 1:
			return
		
		pass
