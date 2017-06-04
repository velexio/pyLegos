#!/bin/bash
PROJ_DIR=/Users/gchristiansen/projects/pyLegos; 
DYLD_LIBRARY_PATH=/Users/gchristiansen/rtengines/oracle/current/:$DYLD_LIBRARY_PATH; export DYLD_LIBRARY_PATH

PYTHONPATH=${PROJ_DIR}/src/framework; export PYTHONPATH
pdoc --html --html-dir ${PROJ_DIR}/docs --only-pypath --overwrite --all-submodules pylegos
pdoc --html --html-dir ${PROJ_DIR}/docs --only-pypath --overwrite --all-submodules pylegos.web
pdoc --html --html-dir ${PROJ_DIR}/docs  --only-pypath --overwrite --all-submodules pylegos.database

