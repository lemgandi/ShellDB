#!/bin/bash
SRCDIR=/home/cshapiro/projects/QGIS_Shell/ShellDB
if [ $(pwd) = ${SRCDIR} ]
then
   echo Don t run this here.
   exit 1
fi
make
rm Makefile
rm count_selected_features.txt
rm get_attribute_names.txt
rm notes.txt
