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
import json


class EsriVectorQueryFactoy:
    
    @staticmethod
    def createMetaInformationQuery():
        return EsriQuery(params={"f":"json"})                                 
    
    @staticmethod
    def createTotalFeatureCountQuery(extent=None, customFilter=None):  
        query = EsriVectorQueryFactoy.createBaseQuery(extent, customFilter)
        query.update({"returnCountOnly":"true"})                               
        return EsriQuery("/query",query)
    
    @staticmethod
    def createFeaturesQuery(extent=None, customFilter=None):
        query = EsriVectorQueryFactoy.createBaseQuery(extent, customFilter)                
        return EsriQuery("/query",query)
    
    @staticmethod
    def createPagedFeaturesQuery(page, maxRecords, extent=None, customFilter=None):
        offset = page * maxRecords
        query = EsriVectorQueryFactoy.createBaseQuery(extent, customFilter)
        query.update({"resultOffset":offset,"resultRecordCount":maxRecords})        
        return EsriQuery("/query",query) 
    
    @staticmethod
    def createExtentParam(extent):
        return {
                "geometryType":"esriGeometryEnvelope",
                "geometry":extent
                }
        
    @staticmethod    
    def createBaseQuery(extent=None, customFilter = None):        
        allObjects =  {"where":"objectid=objectid"}
        allFields = {"outfields":"*"}
        jsonFormat = {"f":"json"}                           
        query = {}            
        customFilterKeys = []
        if not customFilter is None:
            customFilterKeys = [k.lower() for k in customFilter.keys()]
        if customFilter is None or not "where" in customFilterKeys:
            query.update(allObjects)
        if customFilter is None or not "outfields" in customFilterKeys:
            query.update(allFields)
        if customFilter is None or not "f" in customFilterKeys:
            query.update(jsonFormat)
        if customFilter is not None:
            query.update(customFilter)
        if extent is not None and (customFilter is None or "geometry" not in customFilter):
            query.update(EsriVectorQueryFactoy.createExtentParam(extent))
        return query
                
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

class EsriConnectionJSONValidatorException(Exception):
    NotArcGisRest, WrongLayerType, NoLayer, NoPagination = range(4)  
    
    errorNr = None
    
    def __init__(self, message, errorNr):
        super(EsriConnectionJSONValidatorException, self).__init__(message)
        self.errorNr = errorNr


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
            raise EsriConnectionJSONValidatorException("No ArcGIS Resource found.", EsriConnectionJSONValidatorException.NotArcGisRest)
        metaInfo = EsriLayerMetaInformation.createFromMetaJson(responseJson)
        if metaInfo.layerType is None:
            raise EsriConnectionJSONValidatorException("The URL points not to a layer.", EsriConnectionJSONValidatorException.NoLayer)
        if metaInfo.layerType != "Feature Layer":
            raise EsriConnectionJSONValidatorException("Layer must be of type Feature Layer. {} provided.".format(metaInfo.layerType), EsriConnectionJSONValidatorException.WrongLayerType)
        
            
class EsriLayerMetaInformation:
    maxRecordCount = 0
    supportsPagination = False
    layerType = None
    
    @staticmethod
    def createFromMetaJson(metaJson):
        ':rtype EsriLayerMetaInformation'
        metaInfo = EsriLayerMetaInformation()
        if u'maxRecordCount' in metaJson:
            metaInfo.maxRecordCount = int(metaJson[u'maxRecordCount'])
        if "advancedQueryCapabilities" in metaJson and "supportsPagination" in metaJson["advancedQueryCapabilities"] and metaJson["advancedQueryCapabilities"]["supportsPagination"]:
            metaInfo.supportsPagination = metaJson["advancedQueryCapabilities"]["supportsPagination"]
        if "type" in metaJson:
            metaInfo.layerType = metaJson["type"]
        return metaInfo
        
        
class Connection:    
    basicUrl = None    
    name = None    
    authMethod = None
    username = None
    password = None
    bbBox = None
    customFiler = None
    
    def __init__(self, basicUrl, name, username=None, password=None, authMethod=ConnectionAuthType.NoAuth):
        self.basicUrl = basicUrl
        self.name = name
        self.username = username
        self.password = password
        self.authMethod = authMethod
        
    @staticmethod
    def createAndConfigureConnection(basicUrl, name, username=None, password=None, authMethod=ConnectionAuthType.NoAuth, validator=EsriConnectionJSONValidatorLayer()):
        connection = Connection(basicUrl, name, username, password, authMethod)
        connection.configure(validator)
        return connection
       
    def configure(self, validator):
        try:
            query = EsriVectorQueryFactoy.createMetaInformationQuery()                                     
            response = self.connect(query)
            if response.status_code != 200: 
                if "www-authenticate" in response.headers:
                    if "NTLM, Negotiate" in response.headers["www-authenticate"]:
                        self.authMethod = ConnectionAuthType.NTLM
                    else:
                        self.authMethod = ConnectionAuthType.BasicAuthetication          
        except (requests.exceptions.RequestException, ValueError):
            #fail silently
            pass   
                             
    def validate(self, validator):
        try:
            query = EsriVectorQueryFactoy.createMetaInformationQuery()
            response = self.connect(query)
            response.raise_for_status()
            validator.validate(response)              
            if self.name == "":
                self._updateLayerNameFromServerResponse(response)              
        except Exception:
            raise
    
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
    
    def needsAuth(self):
        return self.authMethod != ConnectionAuthType.NoAuth
    
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
    
    def getJson(self, query):
        return self.connect(query).json()
    
                    
    def createSourceFileName(self):        
        vectorSrcName = hashlib.sha224(self.getConnectionIdentifier()).hexdigest()
        return vectorSrcName + ".json"
    
    def getConnectionIdentifier(self):
        identifier = self.basicUrl
        if self.bbBox is not None:
            identifier+=self.bbBox
        if self.customFiler is not None:
            identifier+=json.dumps(self.customFiler)
        return identifier
                                            
    def _updateLayerNameFromServerResponse(self, response):
        try:
            responseJson = response.json()
            if "name" in responseJson:
                self.name = responseJson["name"]
        except ValueError:
            raise

      
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
        customFilter = str(qgsLayer.customProperty("arcgiscon_connection_customfilter"))
        if customFilter != "":
            esriLayer.connection.customFiler = json.loads(customFilter)
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
        customFilter = json.dumps(self.connection.customFiler) if self.connection.customFiler is not None else ""
        self.qgsVectorLayer.setCustomProperty("arcgiscon_connection_customfilter", customFilter)         
                      
