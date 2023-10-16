#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo "Script dir: $SCRIPT_DIR"


cd ${SCRIPT_DIR}/..


python emulator.py -p 5002 -redfish-path ./Resources/CXLAgent/ &

sleep 10

python -m unittest discover -s tests
