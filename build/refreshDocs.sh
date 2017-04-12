#!/bin/bash
PROJ_DIR=/Users/gchristiansen/projects/pyLegos; 
DYLD_LIBRARY_PATH=/Users/gchristiansen/rtengines/oracle/current:$DYLD_LIBRARY_PATH; export DYLD_LIBRARY_PATH

PYTHONPATH=${PROJ_DIR}; export PYTHONPATH
pdoc --html --html-dir ${PROJ_DIR}/docs --overwrite --all-submodules velexio.pylegos
pdoc --html --html-dir ${PROJ_DIR}/docs/velexio/pylegos/core --overwrite velexio/pylegos/core/termlegos.py
pdoc --html --html-dir ${PROJ_DIR}/docs/velexio/pylegos/core --overwrite velexio/pylegos/core/threadlegos.py
pdoc --html --html-dir ${PROJ_DIR}/docs/velexio/pylegos/database --overwrite velexio/pylegos/database/oracle.py

