#!/bin/bash
PROJ_DIR=/Users/gchristiansen/projects/pyLegos; 

PYTHONPATH=${PROJ_DIR}; export PYTHONPATH
pdoc --html --html-dir ${PROJ_DIR}/docs --overwrite --all-submodules velexio.pylegos


