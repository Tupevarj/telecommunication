#/bin/sh
STEP="$1"
./waf --run="REMgenerator --step=$STEP"
