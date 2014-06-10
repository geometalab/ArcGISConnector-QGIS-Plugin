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
from PyQt4.QtNetwork import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from connectordialog import ConnectorDialog
from inputdialog import InputDialog
import os.path
import distutils.dir_util

import base64
import urllib
import json
import requests
import traceback

try:
	_encoding = QApplication.UnicodeUTF8
	def _translate(context, text, disambig):
		return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
	def _translate(context, text, disambig):
		return QApplication.translate(context, text, disambig)

_connections = dict()

class Connection:
	
	def __init__(self, name, url, username, pw):
		global _connections
		self.name = name
		self.url=url
		self.username = username
		self.password = pw
		_connections[name] = self
	
	

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
		
		self.connFile = self.plugin_dir+"/conns.dat"
		with open(self.connFile, "a") as bla:
			bla.close()
		self.indialog = None
		
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
		
		self.dialog.connect(self.dialog.connectButton, SIGNAL("clicked()"), self.loadTreeView)
		self.dialog.connect(self.dialog.importLayers, SIGNAL("clicked()"), self.loadLayer)
		self.dialog.connect(self.dialog.cancelButton, SIGNAL("clicked()"), self.dialog.close)
		
		self.dialog.connect(self.dialog.newButton, SIGNAL("clicked()"), self.newInput)
		self.dialog.connect(self.dialog.deleteButton, SIGNAL("clicked()"), self.delConnection)
		self.dialog.connect(self.dialog.editButton, SIGNAL("clicked()"), self.editCurrent)
		

		#self.dialog.password.setEchoMode(QLineEdit.Password);
		self.loadConnections()
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
	
	def editCurrent(self):
		name = self.dialog.connections.currentText()
		self.newInput(name)
		
	
	def newInput(self, name = ""):
		global _connections
		if self.indialog:
			self.indialog.close()
		
		self.indialog = InputDialog()
		self.indialog.setModal(True)
		
		self.indialog.passwordBox.setEchoMode(QLineEdit.Password);
		
		if name:
			try:
				conn = _connections[name]
				
				self.indialog.nameBox.setText(conn.name)
				self.indialog.serviceURLBox.setText(conn.url)
				self.indialog.usernameBox.setText(conn.username)
				self.indialog.passwordBox.setText(conn.password)
			except Exception:
				pass
		
		self.indialog.connect(self.indialog.OKButton,SIGNAL("clicked()"), self.newConnectionFromIndialog)
		self.indialog.connect(self.indialog.cancelButton,SIGNAL("clicked()"), self.indialog.close)
		
		self.indialog.show()
		self.indialog.exec_()
	
	
	def newConnectionFromIndialog(self):
		
		name = self.indialog.nameBox.text()
		url = self.indialog.serviceURLBox.text()
		username = self.indialog.usernameBox.text()
		password = self.indialog.passwordBox.text()
		
		Connection(name, url, username, password)
		
		self.writeConnections()
		self.loadConnections()
		self.setConnectionTo(name)
		self.indialog.close()
	
	def setConnectionTo(self, name):
		global _connections
		try:
			conn = _connections[name]
			oldIndex = self.dialog.connections.currentIndex()
			count = self.dialog.connections.count()
			for i in range(count):
				self.dialog.connections.setCurrentIndex(i)
				if self.dialog.connections.currentText() == name:
					return
			self.dialog.connections.setCurrentIndex(oldIndex)
		except Exception:
			return
	
	def writeConnections(self):
		global _connections
		
		with open(self.connFile, "w") as data:
			for connName in _connections.keys():
				conn = _connections[connName]
				if not conn:
					continue
				name = conn.name
				url = conn.url
				username = conn.username
				password = conn.password
				data.write(name+";"+url+";"+username+";"+password+"\n")
	
	def delConnection(self):
		global _connections
		try:
			_connections[self.dialog.connections.currentText()] = None
			self.writeConnections()
			self.loadConnections()
		except Exception:
			pass
	
	def loadConnections(self):
		global _connections
		with open(self.connFile, "r") as data:
			_connections = dict()
			lines = data.readlines()
			for line in lines:
				line = line.replace("\n", "")
				if line == "":
					continue
				#print line
				entries = line.split(";")
				Connection(entries[0], entries[1], entries[2], entries[3])
		#print _connections
		self.dialog.connections.clear()
		for connNames in _connections.keys():
			conn = _connections[connNames]
			self.dialog.connections.addItem(conn.name)
	
	def setLoginData(self):
		global _connections
		try:
			conn = _connections[self.dialog.connections.currentText()]
			self.username = conn.username
			self.password = conn.password
		except Exception:
			self.username = ""
			self.password = ""
	
	def requestFor(self, url):

		request = requests.get(url, auth=(self.username, self.password))
		if "www-authenticate" in request.headers:
			self.lastAuthMethod = "Basic"
			if "NTLM, Negotiate" in request.headers["www-authenticate"]:
				self.lastAuthMethod = "NTLM"
				from requests_ntlm import HttpNtlmAuth
				request = requests.get(url, auth=HttpNtlmAuth(self.username, self.password))
		else:
			self.lastAuthMethod = None
			
		if not request.status_code == 200:
			self.warning(request.text)
			return False
		return request.text
	
	def populateFolder(self, base, jsonContent, parentItem):
		
		if jsonContent.has_key("folders"):
			for folder in jsonContent["folders"]:
				newBase = base+"/"+folder
				jsonText = self.requestFor(newBase+"?f=json")
				newJsonContent = json.loads(jsonText)
				
				baseItem = QTreeWidgetItem()
				baseItem.setText(0, folder)
				parentItem.addChild(baseItem)
				self.populateFolder(newBase, newJsonContent, baseItem)
		if jsonContent.has_key("services"):
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
		self.dialog.treeView.clear()
		self.dialog.treeView.addTopLevelItem(baseItem)
		
		self.populateFolder(base, jsonContent, baseItem)
	
	def loadTreeView(self):
		global _connections
		try:
			conn = _connections[self.dialog.connections.currentText()]
			serviceURL = conn.url
		except Exception:
			return
		
		if not serviceURL:
			return
		if serviceURL == "":
			return
		
		url = serviceURL
		urlJSON = url + "?f=json"
		
		self.setLoginData()
		
		try:
			jsonText = self.requestFor(urlJSON)#urllib2.urlopen(request).read()
			if not jsonText:
				return
		except Exception as e:
			return self.warning(_translate("Connector", "Url not found.", None) + " \nError: " + e.message)
		try:
			jsonContent = json.loads(jsonText)
		except:
			return self.warning(_translate("Connector", "Quering JSON must be allowed on the Server.", None))
		
		self.loadTreeViewFor(url, jsonContent)
	
	def isFeatureLayer(self, item):
		jsonContent = json.loads(self.requestFor(item.toolTip(0)+"?f=json"))
		
		for layer in jsonContent["layers"]:
			layerJSON = json.loads(self.requestFor(item.toolTip(0)+"/"+str(layer["id"])+"/"+"?f=json"))
			
			if layerJSON['type'] == "Feature Layer":
				return True
			
		return False
	
	def loadMapServerLayers(self, item):
		jsonContent = json.loads(self.requestFor(item.toolTip(0)+"?f=json"))
		
		#testURL = item.toolTip(0)+"?f=json"
		
		import XMLWriter
		
		reqURL = item.toolTip(0)+"/tile/${z}/${y}/${x}"
		
		source = QUrl(reqURL)
		source.setUserName(self.username)
		source.setPassword(self.password)
		
		XMLWriter.url = source.toString(options=QUrl.None)
		
		#print testURL
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
		#self.iface.addRasterLayer(testURL, item.toolTip(1), "gdal")
	
	def loadFeatureLayers(self, item):
		jsonContent = json.loads(self.requestFor(item.toolTip(0)+"?f=json"))
		if jsonContent.has_key("layers"):
			for layer in jsonContent["layers"]:
				identi = str(layer["id"])
				name = layer["name"]
				
				
				reqURL = item.toolTip(0)+"/"+str(identi)+"/query?where=objectid+%3D+objectid&outfields=*&f=json"
				
				source = QUrl(reqURL)
				source.setUserName(self.username)
				source.setPassword(self.password)
				
				url = source.toString(options=QUrl.None)
				
				self.iface.addVectorLayer(url, item.toolTip(1)+" / "+name, "ogr")
				
				#self.loadImageryFor(item.toolTip(0)+"/"+str(identi)+"/", name)
			
	
	def loadImageryFor(self, layerURL, layerName):
		'''
		Unfinished implementation
		'''
		reqURL = layerURL + "?f=json"
		jsonContent = json.loads(self.requestFor(reqURL))
		infos = None
		try:
			infos = jsonContent["drawingInfo"]["renderer"]["uniqueValueInfos"]
		except KeyError:
			return
		
		for info in infos:
			name = str(info["label"])
			imageURL = layerURL + "images/"+ str(info["symbol"]["url"])
			
			os.makedirs(self.plugin_dir+"/tmp/"+layerName)
			with open(self.plugin_dir+"/tmp/"+layerName+"/"+name+".png", "w") as imageFile:
				imageFile.write(self.requestFor(imageURL).decode("base64"))
			
		
		return
	
	def loadLayer(self):
		item = self.dialog.treeView.currentItem()
		if not item:
			return self.warning(_translate("Connector", "Nothing selected", None))
		if not item.toolTip(0) or item.toolTip(0)=="":
			return self.warning(_translate("Connector", "Select a Service", None))
		
		if item.toolTip(2) == "MapServer":
			self.loadMapServerLayers(item)
		else:
			self.loadFeatureLayers(item)
		
		
	
	def passMethod(self):
		if 1 == 1:
			return
		
		pass
