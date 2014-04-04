"""
/***************************************************************************
 ShellDB
                                 A QGIS plugin
 Pass selected QGIS data to a shell script
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
"""
from qgis.core import *


class utils:

    def __init__(self,iface):
        self.iface=iface
        self.logfilename = "/tmp/shelldb_debug.txt"
        self.logfile=None
        
    def find_layer_by_string(self,layer_name):
        """Return a layer given its id. Might be unneccessary if I 
        understood the plugin API a little better."""
        retVal=None
        for kk in self.iface.mapCanvas().layers():
            if kk.id() == layer_name:
                retVal = kk
                break;
        return retVal

    def openlog(self):
        """Open logfile."""
        retVal=True
        self.logfile=open(self.logfilename,"a")
        return retVal

    def closelog(self):
        """Close lotfile"""
        self.logfile.close()


    def write_dict_to_logfile(self,dict_name,dict):
        """Log contents of dictionary to logfile."""
        self.openlog()
        self.logfile.write("-------------------\n")
        self.logfile.write("Dictionary: [%s]:\n" % (dict_name))
        for kk in dict.keys():
            self.logfile.write("\t[%s]:[%s]\n" % (kk,dict[kk]))
        self.closelog()


    def write_array_to_logfile(self,arrayname,array):
        """Log contents of an array"""
        self.openlog()
        self.logfile.write("Array: [%s]:\n" % (arrayname))
        array_counter=0
        for kk in range(0,len(array)):
            self.logfile.write("\t%d: [%s]\n" % (kk,array[kk]))
        self.closelog()
            

    def write_str_to_logfile(self,str):
        """Log a string to the logfile"""
        self.openlog()
        self.logfile.write("***%s***\n" % (str))
        self.closelog()

