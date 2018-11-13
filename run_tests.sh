#! /bin/bash
# Runs the testing framework:
#   - nose
#   - coverage
#   - mypy

cd testing_framework
python3 -m nose -v --with-coverage --cover-erase --cover-package .. ..
echo '----------------------------------------------------------------------'
python3 -m mypy -V ..
python3 -m mypy ..
