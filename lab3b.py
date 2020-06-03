#!/usr/bin/env python3

# NAME: Robert Royce, Tyler Hackett
# EMAIL: robroyce1@ucla.edu, tjhackett@ucla.edu
# ID: 705357270,405180956


import argparse
import csv
import errno
import os
import sys
from data_structures import *
from pprint import pprint

LAB3USAGE = "Lab3b filename"
LAB3DESC = "Parses EXT2 dump files and checks for consistency and integrity."
LAB3FILEHELP = "The file to be analyzed."
EXSUCCESS = 0
EXBADEXEC = 1
EXINCONSISTENT = 2
debug = False

VALID_PREFFIX = ['SUPERBLOCK', 'GROUP', 'BFREE', 'IFREE', 'INODE', 'DIRENT', 'INDIRECT']
SUPERBLOCK = 'SUPERBLOCK'
GROUP = 'GROUP'
BFREE = 'BFREE'
IFREE = 'IFREE'
INODE = 'INODE'
DIRENT = 'DIRENT'
INDIRECT = 'INDIRECT'

KiB = 1024

def main(filename):
    if(debug):
        print("Filename set to {}...".format(filename))
        print("Debug set to {}...".format(debug))

    super_summary = None
    group_summary = None
    free_block_entries = list()
    free_inode_entries = list()
    inode_summaries = list()
    directory_entries = list()
    indirect_references = list()
    block_map = dict()

    # read and parse the CSV file into constituent objects (based on TYPE field)
    contents = None
    try:
        with open(filename, newline='') as f:
            for row in csv.reader(f):
                label = row[0]

                if label == SUPERBLOCK:
                    super_summary = SuperBlockSummary(row)

                elif label == GROUP:
                    group_summary = GroupSummary(row)

                elif label == BFREE:
                    free_block_entries.append(FreeBlockEntry(row))

                elif label == IFREE:
                    free_inode_entries.append(FreeInodeEntry(row))

                elif label == INODE:
                    inode_summaries.append(InodeSummary(row))

                elif label == DIRENT:
                    directory_entries.append(DirectoryEntry(row))

                elif label == INDIRECT:
                    indirect_references.append(IndirectBlockReference(row))

                else: #TODO error!
                    pass

    except IOError as x:
        if x.errno == errno.ENOENT: # does not exist
            print("lab3b: {} does not exist.".format(filename))
        elif x.errno == errno.EACCESS:
            print("lab3b: {} cannot be read.".format(filename))
        else:
            print("lab3b: unable to read {}.".format(filename))
        sys.exit(EXBADEXEC)


    if super_summary.n_blocks <= 0 or super_summary.n_blocks >= (KiB << 20):
        # TODO: handle insanely large block counts
        pass

    block_map = BlockMap(size=super_summary.n_blocks)
    inode_map = InodeMap(size=super_summary.n_indoes)
    block_map.set_free(free_block_entries)

    if debug:
        print("BlockMap size: {}".format(block_map.size))
        print("BlockMap count: {}".format(block_map.count))
        print("InodeMap size: {}".format(inode_map.size))
        print("InodeMap count: {}".format(inode_map.count))
        print(block_map)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage=LAB3USAGE, description=LAB3DESC)
    parser.add_argument("filename", help=LAB3FILEHELP)
    parser.add_argument("--debug", "-d", action='store_const', const=True, default=False)
    args = parser.parse_args()
    debug = args.debug
    main(args.filename)
