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

import subprocess
import shlex
import os
import os.path
import platform

# Import the PyQt and QGIS libraries
from PyQt4 import QtCore
from PyQt4 import QtGui
import resources
from qgis.core import *

# Import local objects
import utils
import templategrinder
import rundialog

class CommandRunner:

    def __init__(self,iface):
        self.iface=iface
        self.Utilities=utils.utils(iface)
        self.CmdGrinder=templategrinder.templateGrinder()

    def configure(self,state):
        """State configuration happens here, not in __init__. This is so that
        we can change parameters and reconfigure on the fly."""
        self.state = state

    def getFieldNamesDict(self,currentLayer):
        """Return a dictionary of fieldnames.  This keeps us from
           the dreaded 'id' bug."""
        fldsList=currentLayer.pendingFields().toList()
        retValDict={}
        for kk in range(0,len(fldsList)):
            retValDict[kk] = (fldsList[kk].name())
        return retValDict
        
    def check_state(self,stateName):
        """Check my state for a value. I might need to add code to
        return null/false/etc if the stateName key does not exist 
        in the state dictionary."""
        retVal = None
        if stateName in self.state:
            retVal = self.state[stateName]
        return retVal

        
    def makeCmdLine(self,fieldnames,item):
       """Given a command line template, a fieldnames array, and 
       a selected item, make a command line."""
       tmpl_dict={}
       for kk in fieldnames:
           tmpl_dict[fieldnames[kk]]=str(item[kk])
       self.CmdGrinder.set_dict(tmpl_dict)
       retVal=self.CmdGrinder.grind()
       return retVal


    def do_command_winders_other(self,cmdline,logfile):
        """Get around various bugs in the Python 2.6 Popen call on windows."""
        the_path=os.path.dirname(cmdline)
        if (the_path == ''):
            the_path=os.environ['HOME']
	else:
	    if(the_path[0] == '"'):
	       the_path=the_path[1:]

        current_sys = platform.system()
        retcode=None
        if current_sys == 'Windows':
            # I cannot convert cmdline to a string on the stack in windows. I 
            # must have a separate named variable. I have no idea why.
            myCmd=str(cmdline)
            the_path=str(the_path)
	    # self.Utilities.write_str_to_logfile("the_path:["+the_path+"]")
            mySub=subprocess.Popen(myCmd,bufsize=4096,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,cwd=the_path)
            outstr,errstr=mySub.communicate()
            logfile.write(outstr)
            logfile.write(errstr)
            retcode=mySub.returncode
        else:
            mySub=subprocess.Popen(shlex.split(str(cmdline)),bufsize=4096,stdout=logfile,stderr=subprocess.STDOUT,universal_newlines=True, cwd=the_path)
            mySub.communicate()
            retcode=mySub.returncode
        return retcode

    def show_commands(self,cmdline_array):
        retVal = None
        my_runDialog=rundialog.RunDialog(self.iface,cmdline_array)
        my_runDialog.show()
        result=my_runDialog.exec_()
        # 0 if ok was pressed ( old C coder here)
        if 0 == result:
            retVal=my_runDialog.get_edited_commands()
        return retVal
        
    def shell_out(self,cmdlines,featurelist):
        """Okay, actually run our commands."""
        log_file=None
        retVal=True
        OS_Error=False
        if "" != self.check_state('LogFile'):
            try:
                log_file=open(str(self.state['LogFile']),str("a"))
            except IOError as ioTrouble:
                QtGui.QMessageBox.warning(None,"Logfile Trouble",
                "Cannot open log file: %s" % (ioTrouble.__str__()))
                log_file=None
        for kk in range(0,len(cmdlines)):
            # shlex.split does not appear to work on winders.
            # arglist=shlex.split(str(cmdlines[kk])) 
            # self.Utilities.write_array_to_logfile("Arglist",arglist)
            try:
                retcode=self.do_command_winders_other(cmdlines[kk],log_file)
            except OSError as osTrouble:
                QtGui.QMessageBox.warning(None,"OS Error",
                "An operating system error occurred:%s[%s]%s" % 
                (os.linesep,osTrouble.__str__(),os.linesep))
                retVal=False
                OS_Error=True
                break                                    
            except Exception as foo:
                if None != log_file:
                    log_file.write("Something bad happened on [%s]: [%s] %s" % 
                    (cmdlines[kk],foo,os.linesep))
                    retVal=False
                    OS_Error=True
                    break
            else:
                if retcode != 0:
                    retVal=False
                    # Do not delete features which have nonzero error levels.
                    if self.check_state("HideProcessedPts") != 0:
                        self.current_layer.deselect(featurelist[kk].id())
                    if None != log_file:
                        log_file.write("Return code:%d on [%s]%s" % (retcode,cmdlines[kk],os.linesep))

        if (self.check_state("HideProcessedPts") != 0) and (OS_Error == False):            
            editStarted = self.current_layer.startEditing()
            if editStarted == True:
                self.current_layer.deleteSelectedFeatures()
                self.current_layer.commitChanges()
                self.iface.mapCanvas().refresh()
            else:
                QtGui.QMessageBox.warning(None,"Read-only Layer","This layer is read-only. I have run your commands, but I cannot delete the processed features.")

        return retVal
            
    def run(self):
        """Run commands according to state."""
        status=True   # Be optimistic.
        retVal=True   # Do not kvetch if we have already shown an error.

        self.current_layer=self.Utilities.find_layer_by_string(self.check_state('CurrentLayer'))
        if None == self.current_layer:
            QtGui.QMessageBox.warning(None,"Missing Layer","""I cannot find map layer [%s]. This usually means it has been removed. After you re-add it, choose it again in my Configure panel to fix this.""" % (self.check_state('CurrentLayer')))
            status=False

        if True == status:
            if 0 == self.current_layer.selectedFeatureCount():
                QtGui.QMessageBox.warning(None,"No features Selected","""Please select one or more features which you wish to pass to the shell.""")
                status=False

        if True == status:
            field_names_array=self.getFieldNamesDict(self.current_layer)
            selected_feature_list=self.current_layer.selectedFeatures()
            cmdline_array=[]
            myBCmd=self.check_state('BatchLevelCmd')
            if((myBCmd <> None) and (len(myBCmd) > 0)):
                cmdline_array.append(myBCmd)
            self.CmdGrinder.set_str(self.check_state("CmdLine"))
            for kk in selected_feature_list:
                cmdline_array.append(self.makeCmdLine(field_names_array,kk))

            if 1 == self.check_state("EditCommands"):
                edited_array=self.show_commands(cmdline_array)
                if None == edited_array:
                    status=False
                else:
                    cmdline_array=edited_array

            if True == status:
#                self.Utilities.write_array_to_logfile("Edited cmdline array",cmdline_array)
                retVal=self.shell_out(cmdline_array,selected_feature_list)
                
            
            
        return retVal

                                                      
        
