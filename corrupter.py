#!/usr/bin/env python3

# Filesystem Summary Corrupter

# NAME: Robert Royce, Tyler Hackett
# EMAIL: robroyce1@ucla.edu, tjhackett@ucla.edu
# ID: 705357270,405180956


import argparse
import csv
import errno
import os
import sys
import random

LAB3USAGE = "corrupter filename"
LAB3DESC = "Corrupts a filesystem summary CSV."
LAB3FILEHELP = "The file to be corrupted."

def main(filename):

    fileout = "{}.corrupt".format(filename)
    corruptChance = 0.20

    with open(filename, newline='') as f:

        with open(fileout, mode='w', newline='') as cf:

            for row in csv.reader(f):

                if(random.random() < corruptChance):

                    corruptIdx = random.randrange(1,len(row))
                    val = row[corruptIdx]

                    if val.isnumeric():
                        val = int(val)
                        row[corruptIdx] = str(val + random.randrange(-val, val+1))

                cf.write(",".join(row))
                cf.write("\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage=LAB3USAGE, description=LAB3DESC)
    parser.add_argument("filename", help=LAB3FILEHELP)
    parser.add_argument("--debug", "-d", action='store_const', const=True, default=False)
    args = parser.parse_args()
    debug = args.debug
    main(args.filename)
    
