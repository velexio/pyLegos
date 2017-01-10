#!/bin/bash
echo Building...
cd dist

cp -r ../velexio .

touch velexio/__init__.py
touch velexio/pylegos/__init__.py
touch velexio/pylegos/core/__init__.py
touch velexio/pylegos/database/__init__.py
find velexio/ -name "*.pyc" -delete

tar -czf vx_pylegos-source.tar.gz velexio 

rm -rf velexio
cd ..
echo Finished


