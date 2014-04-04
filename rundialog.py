"""
/***************************************************************************
   RunDialog.py
                               
Show command lines ready to run
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

from PyQt4 import QtCore, QtGui
from ui_rundialog import Ui_RunCommandsDialog
from qgis.core import *
from qgis.gui import *

import utils

class RunDialog(QtGui.QDialog):
    
    def __init__(self,iface,CmdLineArray):
        QtGui.QDialog.__init__(self)
        self.iface=iface
        self.Utilities=utils.utils(iface)
        self.ui=Ui_RunCommandsDialog()
        self.InptCmdLineArray=CmdLineArray
        self.OutptCmdLineArray=[]
        self.ui.setupUi(self)
        self.initFields()

    def initFields(self):
        theTextStr=""
        for kk in self.InptCmdLineArray:
            theTextStr += kk
            theTextStr += '\n'

        self.ui.CommandLinesTextEdit.setLineWrapMode(
        self.ui.CommandLinesTextEdit.NoWrap)
        self.ui.CommandLinesTextEdit.setPlainText(theTextStr)
        QtCore.QObject.connect(self.ui.RunButton,QtCore.SIGNAL("clicked()"),self.goYes)
        QtCore.QObject.connect(self.ui.AbortButton,QtCore.SIGNAL("clicked()"),self.abort)

    def goYes(self):
       """Get edited commands out of textbox."""
       cmd_lines=self.ui.CommandLinesTextEdit.toPlainText()
       for kk in cmd_lines.split('\n'):
           self.OutptCmdLineArray.append(kk)
       self.OutptCmdLineArray.pop() # Remove spurious last newline
       self.done(0)

    def get_edited_commands(self):
        """Get command lines edited by user out of dialog."""
        return self.OutptCmdLineArray

    def abort(self):
       """No Go."""
       self.done(1)

