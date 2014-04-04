"""
/***************************************************************************
 ShellDB
                                 A QGIS plugin
 Pass selected QGIS data to a shall script
                             -------------------
        begin                : 2012-01-31
        copyright            : (C) 2012 by Spatial Focus Inc
        email                : cshapiro@spatialfocus.com
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
def name():
    return "ShellDB"
def description():
    return "Pass selected QGIS data to a shell script"
def version():
    return "Version 0.2"
def icon():
    return "configIcon.png"
def qgisMinimumVersion():
    return "1.7"
def classFactory(iface):
    # load ShellDB class from file ShellDB
    from shelldb import ShellDB
    return ShellDB(iface)
