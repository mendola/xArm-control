#! /bin/bash
# Runs the testing framework:
#   - nose
#   - coverage
#   - mypy

cd testing_framework
python3 -m nose -v --with-coverage --cover-erase --cover-package .. ..
python3 -m mypy -V ..
