#!/bin/bash
COMMIT_MESSAGE=$1
if [ $# -ne 1 ]
then
  echo "Usage: ./build-source.sh <commit message>"
  exit 1
fi

echo Building...
git add velexio/pylegos/**/*.py
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
git add dist/vx_pylegos-source.tar.gz
./refreshDocs.sh
git add docs/*
git commit -m '$COMMIT_MESSAGE'
git push origin develop
echo Finished and pushed to origin


