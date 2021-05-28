#!/bin/bash
#
# run this in top level install directory
#

MODELDIR=`pwd`/Tests/Models
#
# Let python known where the modules are found:
PYTHONPATH=`pwd`/Src:`pwd`/lib/python:`pwd`/lib64/python; export PYTHONPATH
echo PYTHONPATH is $PYTHONPATH
#
# Run the Server tests
rm crondb.dat
echo 'killing old server processes (killall python)'
killall python
killall Python   # for the Mac.....
echo Starting server...
echo python Src/Personis.py --models $MODELDIR &
nohup python Src/Personis.py --models $MODELDIR &
sleep 5
echo ....started
