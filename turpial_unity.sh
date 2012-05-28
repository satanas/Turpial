#!/bin/bash

# Author: Andrea Stagi (4ndreaSt4gi)
# Description: launches Turpial in Ubuntu with Unity support
# License: GPL v3

./turpial/ui/unity/turpial-daemon.py start
turpial
./turpial/ui/unity/turpial-daemon.py stop
