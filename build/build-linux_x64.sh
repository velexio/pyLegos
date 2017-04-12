#!/bin/bash
echo Building...
mkdir -p dist/velexio/pylegos/deplibs

nuitka --module velexio/pylegos/database/oracle.py --output-dir dist/velexio/pylegos/database --remove-output --recurse-all 
nuitka --module velexio/pylegos/core/framework.py --output-dir dist/velexio/pylegos/core --remove-output

cp -r deplibs/* dist/velexio/pylegos/deplibs/.
cd dist

touch velexio/__init__.py
touch velexio/pylegos/__init__.py
touch velexio/pylegos/core/__init__.py
touch velexio/pylegos/database/__init__.py

rm vx_pylegos-linux_x64.tar.gz
tar -czf vx_pylegos-linux_x64.tar.gz velexio 

rm -rf velexio
cd ..
echo Finished


