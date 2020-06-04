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

                    block = getBlock(block_map, int(row[1]))

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

                    iblockData = [(i, row[12 + i]) for i in range(0,15)]

                    for iBlockIdx, dataBlockNum in iblockData:
                        blockNumber = int(dataBlockNum)

                        if blockNumber == 0: continue

                        if blockNumber not in block_map:
                            block = getBlock(block_map, blockNumber)
                        else:
                            block = Block()

                        block.entryType = "FROM INODE"
                        
                        if(iBlockIdx < 12): block.indLevel = 0
                        elif(iBlockIdx == 12): block.indLevel = 1
                        elif(iBlockIdx == 13): block.indLevel = 2
                        elif(iBlockIdx == 14): block.indLevel = 3

                        inode.blockRefs[blockNumber] = block

                        masterBlock = getBlock(block_map, blockNumber)
                        masterBlock.inodeRefs[inodeNumber] = inode

                elif label == DIRENT:
                    directory_entries.append(DirectoryEntry(row))

                elif label == INDIRECT:

                    block = getBlock(block_map, int(row[5]))

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

    # Useful for converting block.indLevel values to human-readable strings
    indLevelDict = {0: '', 1: 'INDIRECT ', 2: 'DOUBLE INDIRECT ', 3: 'TRIPLE INDIRECT '}

    # Detect allocated blocks on freelist and duplicate blocks
    for (blockNumber, block) in block_map.items():
        if block.onFreeList and block.entryType != BFREE:
            print("ALLOCATED BLOCK {} ON FREELIST".format(blockNumber))
        elif len(block.inodeRefs) > 1:
            for inodeNumber, inode in block.inodeRefs.items():
                dupBlock = inode.blockRefs[blockNumber]
                print("DUPLICATE {}BLOCK {} IN INODE {} AT OFFSET {}".format(indLevelDict[dupBlock.indLevel], blockNumber, inodeNumber, 0))

    # Detect unreferenced blocks
    inodesPerBlock = int(super_summary.block_size/super_summary.inode_size)
    totalInodeBlocks = int(super_summary.n_inodes/inodesPerBlock)
    totalReservedBlocks = int(group_summary.first_inode_block_number) + totalInodeBlocks
    for i in range(totalReservedBlocks, int(group_summary.group_block_count)):
        if i not in block_map:
            print("UNREFERENCED BLOCK {}".format(i))
            

    # Detect allocated inodes on freelist and invalid block numbers
    for inodeNumber, inode in inode_map.items():
        if inode.onFreeList and inode.inodeType != '':
            print("ALLOCATED INODE {} ON FREELIST".format(inodeNumber))

        for blockNumber, block in inode.blockRefs.items():
            if blockNumber < 0 or blockNumber > super_summary.n_blocks:
                print("INVALID {}BLOCK {} IN INODE {} AT OFFSET {}".format(indLevelDict[block.indLevel], blockNumber, inodeNumber, 0))
            elif blockNumber < totalReservedBlocks and blockNumber > 0:
                print("RESERVED {}BLOCK {} IN INODE {} AT OFFSET {}".format(indLevelDict[block.indLevel], blockNumber, inodeNumber, 0))

    # Detect unallocated inodes not on freelist
    for i in range(11, int(group_summary.group_inode_count) + 1):
        if i not in inode_map:
            print("UNALLOCATED INODE {} NOT ON FREELIST".format(i))

    if debug:
        print("Beginning block map initialization.")
        print("Number of blocks: {}".format(super_summary.n_blocks))

def getInode(map, number):
    if number not in map:
        inode = map[number] = Inode()
    else:
        inode = map[number]

    return inode

def getBlock(map, number):
    if number not in map:
        block = map[number] = Block()
    else:
        block = map[number]

    return block


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage=LAB3USAGE, description=LAB3DESC)
    parser.add_argument("filename", help=LAB3FILEHELP)
    parser.add_argument("--debug", "-d", action='store_const', const=True, default=False)
    args = parser.parse_args()
    debug = args.debug
    main(args.filename)
