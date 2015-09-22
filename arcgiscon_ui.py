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
        