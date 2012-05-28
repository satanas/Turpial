#!/bin/bash

# Author: Andrea Stagi (4ndreaSt4gi)
# Description: launches Turpial in Ubuntu with Unity support
# License: GPL v3

python ./turpial/ui/unity/daemon.py start
turpial
python ./turpial/ui/unity/daemon.py stop
