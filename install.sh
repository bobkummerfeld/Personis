#!/bin/bash
#
# run this in top level install directory
#
test -d Personis || { echo 'Please run in top-level install directory'; exit 1; }

major=`python -c "import sys
print sys.version_info[0]"`
minor=`python -c "import sys
print sys.version_info[1]"`

if [ $major -eq 2 ]; then
    if [ $major -lt 2 ] || [ $minor -lt 7 ]; then
        echo "Python version too old."
        echo "Installed: $major.$minor"
        echo "Required: >= 2.7"
        exit
    fi  
else
    echo "Python version must be 2.X"
    exit
fi

cd Personis
export PYTHONPATH=`pwd`/Src:`pwd`/lib/python:`pwd`/lib64/python

# first make sure python-dev is installed
echo "python-dev and libgmp3-dev need to be installed in the Python2.7 library"
echo "this can be done on linux with 'sudo apt-get install python-dev libgmp3-dev'"
echo "on Macos if you installed Python with brew they should be already there"
echo -n "ok?"; read x
# sudo apt-get install python-dev
# sudo apt-get install libgmp3-dev

PLIB=`pwd`

echo installing simplejson
tar zxf simplejson-2.1.1.tar.gz
cd simplejson-2.1.1
python setup.py install --home=$PLIB
cd ..

echo installing pyCrypto
tar zxf pycrypto-2.6.tar.gz
cd pycrypto-2.6
python setup.py install --home=$PLIB
cd ..

echo install requests
tar zxvf requests-2.10.0.tar.gz
cd requests-2.10.0
python setup.py install --home=$PLIB
cd ..


echo done.
echo
echo '==============================================================================='
echo "Don't forget to set your PYTHONPATH to:"
echo $PYTHONPATH
echo "before attempting to use Personis."
echo
echo "Please read the Introduction and Tutorial in Personis/Doc/Personis.pdf"
echo '==============================================================================='
