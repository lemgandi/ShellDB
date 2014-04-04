"""
/***************************************************************************
 ShellDBDialog
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

import os
import platform

from PyQt4 import QtCore, QtGui
from ui_shelldb import Ui_ShellDB
from qgis.core import *
from qgis.gui import *

import utils


class ShellDBDialog(QtGui.QDialog):
    def __init__(self,iface):
        QtGui.QDialog.__init__(self)
        self.iface = iface
        self.Utilities=utils.utils(iface)
        self.homedir=os.environ['HOME']
        # Set up the user interface from Designer.
        self.ui = Ui_ShellDB()
        self.ui.setupUi(self)
        self.initFields()
        # The StateNames dict is a list of keys for the ui_state dictionary.
        # They are also keys for saving/retrieving our state from QgsProject.
        # This kind of sucks but I don't see any way of getting this info 
        # from the project itself.
        self.StateNames={'CmdLine':'FileName','LogFile':'FileName',
        'HideProcessedPts':'int','CurrentLayer':'QString',
         'EditCommands':'int','BatchLevelCmd':'FileName'}

    def escape_as_necessary(self,in_str):
        """QGIS or QT4 dialogs return filenames with / dirseps, regardless
        of what OS we are on.  Also since these are command lines, I must 
        escape spaces and other non-command characters.  """
        retVal=in_str
        current_sys=platform.system()
        if current_sys == 'Windows':
            retVal=retVal.replace('/','\\')
        if True == ' ' in retVal:
            retVal = '"' + retVal + '"'
        return retVal
            
    def getStateNames(self):
        """Get state names for reading keys from QgsProject"""
        return self.StateNames

    def set_state(self,ui_state):
        """Load values into fields."""
        self.ui_state=ui_state
        self.load_state(self.ui_state)

    def load_state(self,ui_state):
        """Load current cmdline et cetera into ui."""
        if ui_state.has_key('CmdLine'):
            self.ui.Command_Line_textinput.setText(ui_state['CmdLine'])
        if ui_state.has_key('LogFile'):
            self.ui.LogFileNameLine.setText(ui_state['LogFile'])
        if ui_state.has_key('BatchLevelCmd'):
            self.ui.BatchLevelScriptLine.setText(ui_state['BatchLevelCmd'])
        if ui_state.has_key('HideProcessedPts'):
            self.ui.HideProcessedPointsCheckbox.setChecked(ui_state['HideProcessedPts'])
        if ui_state.has_key('EditCommands'):
            self.ui.EditCommandCheckbox.setChecked(ui_state['EditCommands'])
        if ui_state.has_key('CurrentLayer'):
               theList=self.ui.map_layers_listbox.model().stringList()
               if ui_state['CurrentLayer'] in theList:
                   
                   index_num=self.ui.map_layers_listbox.model().stringList().index(ui_state['CurrentLayer'])
               else:
                   index_num = -1
               if (index_num != -1):
                   the_index=self.ui.map_layers_listbox.model().index(index_num) 
                   self.ui.map_layers_listbox.setCurrentIndex(the_index)
                   self.fill_fieldnames(the_index)

    def get_ui_state(self):
        """Access method for the dialog screen."""
        return self.ui_state

    def initFields(self):
        "Put data into the dialog fields which need it."
        layerList=[]
        # We will work only with vector layers.
        for kk in self.iface.mapCanvas().layers():
            if kk.type() == kk.VectorLayer:
                layerList.append(kk.id())
        layerListModel = QtGui.QStringListModel(layerList)
        self.ui.map_layers_listbox.setModel(layerListModel)
        # Connect a QT C++ signal has to have the **exact** prototype of
        # the signal you are trying to connect.
        QtCore.QObject.connect(self.ui.map_layers_listbox,
        QtCore.SIGNAL("clicked(const QModelIndex &)"),self.fill_fieldnames)
        QtCore.QObject.connect(self.ui.find_script_button,QtCore.SIGNAL("clicked()"),self.find_shellscript)
        QtCore.QObject.connect(self.ui.find_batch_cmd_button,QtCore.SIGNAL("clicked()"),self.find_batchlevelscript)
        QtCore.QObject.connect(self.ui.find_log_button,QtCore.SIGNAL("clicked()"),self.find_logfile)
        QtCore.QObject.connect(self.ui.data_fields_listbox,QtCore.SIGNAL("clicked(const QModelIndex &)"),self.fieldnames_to_command_line)
            
    def fill_fieldnames(self,itemClicked):
        "Place field names into field name list when a layer is selected."
        layer_name=itemClicked.model().stringList()[itemClicked.row()]
        the_layer=self.Utilities.find_layer_by_string(layer_name)
        layerList=[]
        for kk in the_layer.pendingFields():
            layerList.append(kk.name())
            fieldListModel=QtGui.QStringListModel(layerList)        
            self.ui.data_fields_listbox.setModel(fieldListModel)
            
    def fieldnames_to_command_line(self,itemClicked):
        "Fill selected fieldnames in on command line"
        field_name=itemClicked.model().stringList()[itemClicked.row()]
        append_str='@@'+field_name+'@@'
        current_cmd_line=self.ui.Command_Line_textinput.text()
        current_cmd_line = current_cmd_line + ' ' + append_str
        self.ui.Command_Line_textinput.clear()
        self.ui.Command_Line_textinput.insert(current_cmd_line)

    def find_shellscript(self):
       "Find the shell script we mean to run, fill it into command line box"
       # self.ui.Command_Line_textinput.insert("shellname");

       shell_name=QtGui.QFileDialog.getOpenFileName(
       self.ui.find_script_button,"Shell Script Name",self.homedir)
       self.ui.Command_Line_textinput.clear()
       self.ui.Command_Line_textinput.insert(self.escape_as_necessary(shell_name))
    def find_batchlevelscript(self):
        """Find the batch level script if necessary"""
        shell_name=QtGui.QFileDialog.getOpenFileName(
            self.ui.find_batch_cmd_button,"Find batch level script",self.homedir)
        self.ui.BatchLevelScriptLine.clear()
        self.ui.BatchLevelScriptLine.insert(self.escape_as_necessary(shell_name))

    def find_logfile(self):
        logfile_name=QtGui.QFileDialog.getSaveFileName(
        self.ui.find_log_button,"Log File Name",self.homedir,options=QtGui.QFileDialog.DontConfirmOverwrite)
        self.ui.LogFileNameLine.clear()
        self.ui.LogFileNameLine.insert(self.escape_as_necessary(logfile_name))

    def accept(self):
        """Accept input from ShellDBDialog"""
        self.ui_state['CmdLine']=self.ui.Command_Line_textinput.text()
        self.ui_state['LogFile']=self.ui.LogFileNameLine.text()
        self.ui_state['HideProcessedPts']=self.ui.HideProcessedPointsCheckbox.isChecked()
        currentLayerItem=self.ui.map_layers_listbox.currentIndex()
        self.ui_state['CurrentLayer']=currentLayerItem.model().stringList()[currentLayerItem.row()]
        self.ui_state['EditCommands']=self.ui.EditCommandCheckbox.isChecked()
        self.ui_state['BatchLevelCmd']=self.ui.BatchLevelScriptLine.text()
        self.done(0)

    def reject(self):
        """Reject input from ShellDBDialog"""
        self.done(1)

