#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo "Script dir: $SCRIPT_DIR"

#${SCRIPT_DIR}/../setup.sh -v -n

cd ${SCRIPT_DIR}/..

#source ./venv/bin/activate

python emulator.py -p 80 -redfish-path ./Resources/CXLAgent/ &

sleep 10

python -m unittest discover -s tests
