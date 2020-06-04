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
    inode_map = dict()

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

                    blockNumber = int(row[1])

                    if blockNumber not in block_map:
                        block = block_map[blockNumber] = Block()
                    else:
                        block = block_map[blockNumber]

                    block.entryType = BFREE
                    block.onFreeList = True

                elif label == IFREE:

                    inodeNumber = int(row[1])
                    if inodeNumber not in inode_map:
                        inode = inode_map[inodeNumber] = Inode()
                    else:
                        inode = inode_map[inodeNumber]

                    inode.onFreeList = True

                elif label == INODE:

                    inodeNumber = int(row[1])
                    if inodeNumber not in inode_map:
                        inode = inode_map[inodeNumber] = Inode()
                    else:
                        inode = inode_map[inodeNumber]

                    inode.inodeType = row[2]
                    inode.linkCount = row[6]
                    inode.fileSize  = row[10]
                    inode.metadata['i_blocks'] = row[12:28]

                    for dataBlockNum in inode.metadata['i_blocks']:
                        blockNumber = int(dataBlockNum)
                        if blockNumber not in block_map:
                            block = block_map[blockNumber] = Block()
                        else:
                            block = block_map[blockNumber]

                        block.entryType = "FROM INODE"


                elif label == DIRENT:
                    directory_entries.append(DirectoryEntry(row))

                elif label == INDIRECT:

                    blockNumber = int(row[5])
                    if blockNumber not in block_map:
                        block = block_map[blockNumber] = Block()
                    else:
                        block = block_map[blockNumber]

                    block.entryType = INDIRECT
                    block.indLevel = int(row[2])
                    block.offset = int(row[3])

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

    for (inodeNumber, inode) in inode_map.items():
        if inode.inodeType != 's' or inode.fileSize > 60:
            if not inode.onFreeList:
                pass
    


    for (blockNumber, block) in block_map.items():
        if block.onFreeList and block.entryType != BFREE:
            print("ALLOCATED BLOCK {} ON FREELIST".format(blockNumber))

    inodesPerBlock = int(super_summary.block_size/super_summary.inode_size)
    totalInodeBlocks = int(super_summary.n_inodes/inodesPerBlock)
    for i in range(int(group_summary.first_inode_block_number) + totalInodeBlocks, int(group_summary.group_block_count)):
        if i not in block_map:
            print("UNREFERENCED BLOCK {}".format(i))
            

    for (inodeNumber, inode) in inode_map.items():
        if inode.onFreeList and inode.inodeType != '':
            print("ALLOCATED INODE {} ON FREELIST".format(inodeNumber))

    for i in range(11, int(group_summary.group_inode_count) + 1):
        if i not in inode_map:
            print("UNALLOCATED INODE {} NOT ON FREELIST".format(i))
            

    # Build map using block number as index and a list of inodes that reference
    # that block as items

    if debug:
        print("Beginning block map initialization.")
        print("Number of blocks: {}".format(super_summary.n_blocks))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage=LAB3USAGE, description=LAB3DESC)
    parser.add_argument("filename", help=LAB3FILEHELP)
    parser.add_argument("--debug", "-d", action='store_const', const=True, default=False)
    args = parser.parse_args()
    debug = args.debug
    main(args.filename)
