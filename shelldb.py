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
import inspect

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from shelldbdialog import ShellDBDialog

import utils
import CommandRunner
import platform

class ShellDB:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.name='ShellDB'
        self.iface = iface        
        self.Utilities = utils.utils(iface)
        the_dialog=ShellDBDialog(self.iface)
        self.state_names=the_dialog.getStateNames()
        self.CmdDoer=CommandRunner.CommandRunner(self.iface)
        self.qgsproject=QgsProject.instance()


    def initGui(self):
        # Create action that will start plugin configuration
        self.configAction = QAction(QIcon(":/ShellDB/configIcon.png"), \
            "Configure", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.configAction, SIGNAL("triggered()"), \
        self.configure)
        self.runAction = QAction(QIcon(":/ShellDB/runIcon.png"), \
        "Run", self.iface.mainWindow())
        QObject.connect(self.runAction,SIGNAL("triggered()"), \
        self.run)
        # Configure myself from saved values if they are present in 
        # a project loaded from disk.
        QObject.connect(self.qgsproject,SIGNAL("readProject(const QDomDocument &)"),self.configure_from_saved_values)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.configAction)
        self.iface.addPluginToMenu("&Shell script plugin", \
        self.configAction)
        self.iface.addPluginToMenu("&Shell script plugin", \
        self.runAction)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&Shell Script Plugin",self.configAction)
        self.iface.removeToolBarIcon(self.configAction)
        self.iface.removeToolBarIcon(self.runAction)

    def handle_cmd(self,project,cmdname,inout):
	"""Handle a filename, possibly with quotes or part of a command line."""       
	if(cmdname[0] == '"'):
	  cmdname=cmdname[1:]
	  quotePt=cmdname.find('"')
	  if(inout == 'WRITE'):
	     cmdfile=project.writePath(cmdname[0:quotePt])
	  else:
             cmdfile=project.readPath(cmdname[0:quotePt])
	  if (platform.system() == 'Windows'):
	     cmdfile=cmdfile.replace('/','\\')
	  if(len(cmdname[quotePt:-1]) > 0):
	     theFN='"'+cmdfile+cmdname[quotePt:]
          else:
             theFN='"'+cmdfile+'"'
	else: 
	  if(inout == 'WRITE'):
	     theFN=project.writePath(cmdname)
          else:
             theFN=project.readPath(cmdname)
        return theFN
 

    def save_ui_state(self,ui_state,stateNames):
        """Save our configuration to the project."""
        dest=QgsProject.instance()
        for kk in ui_state.keys():
            if('FileName' == stateNames[kk] and (len(ui_state[kk]) > 0) ):
                dest.writeEntry(self.name,kk,self.handle_cmd(dest,ui_state[kk],'WRITE'))
            else:
                dest.writeEntry(self.name,kk,ui_state[kk])

    def read_ui_state(self,ui_keys_dict):
        """Read our configuration from the project"""
        the_ui_state={}
        for kk in ui_keys_dict.keys():
            if ui_keys_dict[kk] == 'QString':
                my_t=self.qgsproject.readEntry(self.name,kk)
                if my_t[1] == True:
                    the_ui_state[kk]=my_t[0]
            elif ui_keys_dict[kk] == 'FileName':
                my_t=self.qgsproject.readEntry(self.name,kk)
                if (my_t[1] == True) and (len(my_t[0]) > 0):
                    the_ui_state[kk] = self.handle_cmd(self.qgsproject,my_t[0],'READ')
            elif ui_keys_dict[kk] == 'int':
                my_t=self.qgsproject.readNumEntry(self.name,kk)
                if my_t[1] == True:
                    the_ui_state[kk] = my_t[0]
        return the_ui_state

    def configured(self):
        """Are we ready?"""
        retVal = True # Be optimistic.
        if 0 == len(self.ui_state):
            retVal = False;
        if (retVal == True):
            if (not self.ui_state.has_key("CmdLine")) or (not self.ui_state.has_key("CurrentLayer")):
                retVal = False
        return retVal

    # Configure myself from values saved in project.
    def configure_from_saved_values(self):
        self.ui_state = self.read_ui_state(self.state_names)

    # run method that performs all the real work
    def run(self):
        retVal = False
        if not self.configured():
            QMessageBox.warning(None,"Not Configured",
"""I am not configured yet. 
Load a project and use the configure button to fix this.""")
        else:
            self.CmdDoer.configure(self.ui_state)
            retVal = self.CmdDoer.run()
        if retVal == False:
            QMessageBox.warning(None,"Commandline Failure","One or more commandlines have failed")
        return retVal
        
    # Configure method -- show dialog, gather config data
    def configure(self):
#        self.Utilities.write_str_to_logfile("My File: %s" % (inspect.getsourcefile(utils)))
        self.dlg = ShellDBDialog(self.iface)
        state_names=self.dlg.getStateNames()
        self.ui_state=self.read_ui_state(state_names)
        # create and show the dialog
        self.dlg.set_state(self.ui_state)
        # show the dialog
        self.dlg.show()
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 0:
            self.save_ui_state(self.ui_state,state_names)
            
