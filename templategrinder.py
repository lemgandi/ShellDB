#!/usr/bin/python
#######################################################################
#
# Copyright (C) Charles Shapiro 2006 charles.shapiro@tomshiro.org
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2, or (at your option)
#   any later version.
#
# Template grinder. Given a template string and a dictionary of 
# substitute names + values,
# replaces each delimited macro in the string with the value.
# Macros are delimited with "@@name@@".
#
# Modified for this project:  null dictionary data converted to empty 
# string, dictionary keys converted from QString to string.
#
#######################################################################
import re
import os
import utils

class templateGrinder:
	def setup(self):
		self.template_list=[]
		self.template_dict={}
		self.Utilities=utils.utils(None)

	def template_from_fil(self,filename):
		"""Read template from a filename."""
		try:
			fil=file(filename,"r")
			self.set_str(fil.read())
			fil.close()
		except IOError:
			self.set_str("No Template")



	def __init__(self,template_dict=None,template_str=None,isFile=False):
		"""Create myself from a dictionary and string."""
		self.setup()
		if isFile:
			if template_str != None:
				self.template_from_fil(template_str)
		else:
			if template_str != None:
				self.set_str(template_str)
		if template_dict != None:
			self.set_dict(template_dict)

	def grind_str(self,tStr):
		self.set_str(tStr)
		retVal=self.grind()
		return retVal
			
	def set_str(self,tStr):
		"""Make input template into a list we can pop() from
		top to bottom."""
		self.template_list=tStr.split('\n')
		

	def set_dict(self,tDict):
		""" Set template dictionary member"""
		for k in tDict.keys():
			srchStr="@@" + k + "@@"
			# str() is necessary here because QT sneakily changes
			# quoted strings to QString, which re will kick out
			# with a type error.
			reSrch=re.compile(str(srchStr))
			if tDict[k] != None:
				self.template_dict[reSrch]=tDict[k]
			else:
				self.template_dict[reSrch]=""

	def process_line(self,line):
		""" Substitute all macros in a single line."""
		for srch in self.template_dict.keys():
			substitute=self.template_dict[srch]
			found=srch.search(line)			
			while found:
				theSpan=found.span()
				lineBottom=line[0:theSpan[0]]
				lineTop=line[theSpan[1]:len(line)]
				line=lineBottom + substitute + lineTop
				found=srch.search(line)
		line += os.linesep
		return line

	def grind(self):
		"""Apply template dictionary to template string to produce
		result string."""
		success=True
		result_str=""
		if len(self.template_list) == 0 or len(self.template_dict) == 0:
			success=False
		if success == True:
			myList=self.template_list
			for the_line in myList:
				result_str += self.process_line(the_line)
		# Oops.  If just one line, remove extra newline put in
		# by process_line.
		if len(myList) == 1:
			result_str=result_str[0:len(result_str)-1]
		return result_str

			
		
if __name__ == "__main__":
	import sys
	skelFN=sys.argv[1]
	macFN=sys.argv[2]

	thefil=file(macFN,'r')
	macList=thefil.readlines()
	macList=[memb.strip() for memb in macList]
       	thefil.close()
	macDict=dict([member.split(":") for member in macList])
	macDict["AREA"]=None

	my_grinder=templateGrinder(macDict,skelFN,True)
	print my_grinder.grind()
	
	
