#!/usr/bin/env bash

# NAME: Robert Royce, Tyler Hackett
# EMAIL: robroyce1@ucla.edu, tjhackett@ucla.edu
# ID: 705357270,405180956

# Check for project submission headers (name, email, id)
NAME1="Rob Royce"
NAME2="Tyler Hackett"
EMAIL1="robroyce1@ucla.edu"
EMAIL2="tjhackett@ucla.edu"
ID1=705357270
ID2=405180956

FILENAME=$1

printf "Checking $FILENAME for submission headers..."
h="first N lines"
N=10
if [ -f $FILENAME ]; then
    h=$(head -$N $FILENAME | grep -E "(Rob|robroyce1|705357270|Tyler|tjhackett|405180956)")
    if [ -z "$h" ]; then
        echo "FAIL"
    else
        echo "PASS"
    fi
    echo ""
fi
