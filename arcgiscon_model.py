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

from qgis.core import QgsVectorLayer

import requests
import requests_ntlm
import hashlib

class EsriVectorQueryFactoy:
    
    _queryAll = {"where":"objectid=objectid","outfields":"*","f":"json"}
    
    @staticmethod
    def createMetaInformationQuery():
        return EsriQuery(params={"f":"json"})                                 
    
    @staticmethod
    def createTotalFeatureCountQuery(extent=None):  
        query = EsriVectorQueryFactoy._queryAll.copy()
        query.update({"returnCountOnly":"true"})   
        if extent is not None:
            query.update(EsriVectorQueryFactoy.createExtentParam(extent))                     
        return EsriQuery("/query",query)
    
    @staticmethod
    def createFeaturesQuery(page, maxRecords, extent=None):
        offset = page * maxRecords
        query = EsriVectorQueryFactoy._queryAll.copy()
        query.update({"resultOffset":offset,"resultRecordCount":maxRecords})
        if extent is not None:            
            query.update(EsriVectorQueryFactoy.createExtentParam(extent))
        return EsriQuery("/query",query) 
    
    @staticmethod
    def createExtentParam(extent):
        return {
                "geometryType":"esriGeometryEnvelope",
                "geometry":extent
                }
                
class EsriQuery:
    _urlAddon = None
    _params = None
    def __init__(self, urlAddon="", params={}):
        self._urlAddon = urlAddon
        self._params = params
    
    def getUrlAddon(self):
        return self._urlAddon
    
    def getParams(self):
        return self._params
    
       
    
class ConnectionAuthType:
    NoAuth, BasicAuthetication, NTLM = range(3)


class EsriConnectionJSONValidatorResponse:
    isValid = None
    exceptionMessage = None
    
    def __init__(self, isValid, exceptionMessage=None):
        self.isValid = isValid
        self.exceptionMessage = exceptionMessage
    
    @staticmethod
    def createValid():
        return EsriConnectionJSONValidatorResponse(True)
    
    @staticmethod
    def createNotValid(message):
        return EsriConnectionJSONValidatorResponse(False, message)
    

class EsriConnectionJSONValidator:
    
    def validate(self, responseJson):
        raise NotImplementedError( "Needs implementation" )
    
class EsriConnectionJSONValidatorLayer(EsriConnectionJSONValidator):
    
    def validate(self, response):
        try:
            responseJson = response.json()
        except ValueError:
            return EsriConnectionJSONValidatorResponse.createNotValid("No ArcGIS Resource found.")        
        if "type" in responseJson:
            if responseJson["type"] != "Feature Layer":
                return EsriConnectionJSONValidatorResponse.createNotValid("Layer must be of type Feature Layer. {} provided.".format(str(responseJson["type"])))
        else:
            return EsriConnectionJSONValidatorResponse.createNotValid("The URL points not to a layer.")                
        if not ("advancedQueryCapabilities" in responseJson and "supportsPagination" in responseJson["advancedQueryCapabilities"] and responseJson["advancedQueryCapabilities"]["supportsPagination"]):
                return EsriConnectionJSONValidatorResponse.createNotValid("Pagination not supported. ArcGIS Server must be at least of version 10.3. Current version: {}".format(str(responseJson["currentVersion"])))
        return EsriConnectionJSONValidatorResponse.createValid()
            
class Connection:    
    basicUrl = None    
    name = None    
    authMethod = None
    username = None
    password = None
    bbBox = None
    
    def __init__(self, basicUrl, name, username=None, password=None, authMethod=ConnectionAuthType.NoAuth):
        self.basicUrl = basicUrl
        self.name = name
        self.username = username
        self.password = password
        self.authMethod = authMethod
        
    @staticmethod
    def createAndConfigureConnection(basicUrl, name, username=None, password=None, authMethod=ConnectionAuthType.NoAuth):
        connection = Connection(basicUrl, name, username, password, authMethod)
        connection.configure()
        return connection
                        
    def validate(self, validator=None):
        try:
            query = EsriVectorQueryFactoy.createMetaInformationQuery()
            response = self.connect(query)
            response.raise_for_status()
            if validator is not None:
                response = validator.validate(response)
                if not response.isValid:
                    raise Exception(response.exceptionMessage)                
        except Exception:
            raise
        
    def updateBoundingBoxByExtent(self, extent):
        self.bbBox = extent
    
    def updateBoundingBoxByRectangle(self, qgsRectangle, spacialReferenceWkt):
        xmin=qgsRectangle.xMinimum()
        ymin=qgsRectangle.yMinimum()
        xmax=qgsRectangle.xMaximum()
        ymax=qgsRectangle.yMaximum()
        self.bbBox = "xmin: {}, ymin: {}, xmax: {}, ymax: {}, spatialReference: {}".format(xmin,ymin,xmax,ymax, spacialReferenceWkt)
        
    def clearBoundingBox(self):
        self.bbBox = None        
                   
    def configure(self):
        try:
            query = EsriVectorQueryFactoy.createMetaInformationQuery()                                     
            response = self.connect(query)
            if response.status_code != 200: 
                if "www-authenticate" in response.headers:
                    if "NTLM, Negotiate" in response.headers["www-authenticate"]:
                        self.authMethod = ConnectionAuthType.NTLM
                    else:
                        self.authMethod = ConnectionAuthType.BasicAuthetication            
        except requests.exceptions.RequestException:
            #fail silently
            pass
        
    def getJson(self, query):
        return self.connect(query).json()
                
    def createSourceFileName(self):        
        vectorSrcName = hashlib.sha224(self.getConnectionIdentifier()).hexdigest()
        return vectorSrcName + ".json"
    
    def getConnectionIdentifier(self):
        identifier = self.basicUrl
        if self.bbBox is not None:
            identifier+=self.bbBox
        return identifier
                
    def connect(self, query):       
        auth = None     
        try: 
            if self.authMethod !=ConnectionAuthType.NoAuth and self.username and self.password:
                auth = self.authMethod
                if self.authMethod == ConnectionAuthType.NTLM:                    
                    auth = requests_ntlm.HttpNtlmAuth(self.username, self.password)                                      
            request =  requests.get(self.basicUrl+query.getUrlAddon(), params=query.getParams(), auth=auth, timeout=10)
        except requests.ConnectionError:
            raise
        except requests.HTTPError:
            raise
        except requests.Timeout:
            raise
        except requests.TooManyRedirects:
            raise
                
        return request
    
    
class EsriVectorLayer:
    qgsVectorLayer = None        
    connection = None
    
    @staticmethod
    def create(connection, srcPath):
        esriLayer = EsriVectorLayer()
        esriLayer.connection = connection
        esriLayer.createQgsVectorLayer(srcPath)
        return esriLayer
    
    @staticmethod
    def restoreFromQgsLayer(qgsLayer):
        esriLayer = EsriVectorLayer()
        esriLayer.qgsVectorLayer = qgsLayer
        basicUrl = str(qgsLayer.customProperty("arcgiscon_connection_url"))
        name = qgsLayer.name()
        username = str(qgsLayer.customProperty("arcgiscon_connection_username")) 
        password = str(qgsLayer.customProperty("arcgiscon_connection_password"))
        authMethod = int(qgsLayer.customProperty("arcgiscon_connection_authmethod"))
        esriLayer.connection = Connection(basicUrl, name, username, password, authMethod)
        extent = str(qgsLayer.customProperty("arcgiscon_connection_extent"))
        if extent != "":
            esriLayer.connection.updateBoundingBoxByExtent(extent)
        return esriLayer
                                                
    def createQgsVectorLayer(self, srcPath):
        self.qgsVectorLayer = QgsVectorLayer(srcPath,self.connection.name,"ogr")
        self.updateProperties()
        return self.qgsVectorLayer  
    
    def updateProperties(self):
        self.qgsVectorLayer.setCustomProperty("arcgiscon_connection_url", self.connection.basicUrl)            
        self.qgsVectorLayer.setCustomProperty("arcgiscon_connection_authmethod", self.connection.authMethod)
        self.qgsVectorLayer.setCustomProperty("arcgiscon_connection_username", self.connection.username)
        self.qgsVectorLayer.setCustomProperty("arcgiscon_connection_password", self.connection.password)
        extent = self.connection.bbBox if self.connection.bbBox is not None else ""
        self.qgsVectorLayer.setCustomProperty("arcgiscon_connection_extent", extent)        
                      
