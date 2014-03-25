# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Connector
                                 A QGIS plugin
 ArcGIS REST API Connector
                             -------------------
        begin                : 2014-03-25
        copyright            : (C) 2014 by tschmitz HSR
        email                : tschmitz@hsr.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load Connector class from file Connector
    from connector import Connector
    return Connector(iface)
