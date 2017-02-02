#!/bin/bash
COMMIT=$1
COMMIT_MESSAGE=$2
PUSH_ORIGIN=$3

function showUsage {
  echo "Usage: ./build-source.sh <commit y|n> [ <commit message> <push y|n> ]"
  exit 1
}
if [ $# -lt 1 ]
then
 showUsage
fi

if [ ${COMMIT} == 'y' ] && [ $# -ne 3 ]
then
 showUsage
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
if [ ${COMMIT} == 'y' ]
then
  git commit -m '${COMMIT_MESSAGE}'
  if [ ${PUSH_ORIGIN} == 'y' ]
  then
    git push origin develop
  fi
fi
echo Finished 


