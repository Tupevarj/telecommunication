#!/bin/sh
TRAINING="$1"
cd /home/tupevarj/Projects/ns-allinone-3.26/ns-3.26
xterm -e ./waf --run="CSONDemo --simTime=0.4 --training=$TRAINING" &
