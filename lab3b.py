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

# Command Line Messages
LAB3USAGE = "Lab3b filename"
LAB3DESC = "Parses EXT2 dump files and checks for consistency and integrity."
LAB3FILEHELP = "The file to be analyzed."

# Exit Codes
EXSUCCESS = 0
EXBADEXEC = 1
EXINCONSISTENT = 2

# File read error messages
ERR_DNE = "lab3b: {} does not exist."
ERR_CNR = "lab3b: {} cannot be read."
ERR_UTR = "lab3b: unable to read {}."

# Report Formats
REP_ABOF = "ALLOCATED BLOCK {} ON FREELIST"
REP_AIOF = "ALLOCATED INODE {} ON FREELIST"
REP_DBIIAO = "DUPLICATE {}BLOCK {} IN INODE {} AT OFFSET {}"
REP_DINII = "DIRECTORY INODE {} NAME {} INVALID INODE {}"
REP_DINLTISB = "DIRECTORY INODE {} NAME {} LINK TO INODE {} SHOULD BE {}"
REP_DINUI = "DIRECTORY INODE {} NAME {} UNALLOCATED INODE {}"
REP_IBIAO = "INVALID {}BLOCK {} IN INODE {} AT OFFSET {}"
REP_IHLBLI = "INODE {} HAS {} LINKS BUT LINKCOUNT IS {}"
REP_RBIAO = "RESERVED {}BLOCK {} IN INODE {} AT OFFSET {}"
REP_UINOF = "UNALLOCATED INODE {} NOT ON FREELIST"
REP_URB = "UNREFERENCED BLOCK {}"

# Field Name Constants
SUPERBLOCK = 'SUPERBLOCK'
GROUP = 'GROUP'
BFREE = 'BFREE'
IFREE = 'IFREE'
INODE = 'INODE'
DIRENT = 'DIRENT'
INDIRECT = 'INDIRECT'

# Useful for converting block.indLevel values to human-readable strings
indLevelDict = {
    0: '',
    1: 'INDIRECT ',
    2: 'DOUBLE INDIRECT ',
    3: 'TRIPLE INDIRECT '
}

debug = False


def main(filename):
    super_summary = None
    group_summary = None
    free_block_entries = list()
    free_inode_entries = list()
    inode_summaries = list()
    directory_entries = list()
    indirect_references = list()
    allocOnFreeList = list()
    mismatch = list()
    inodeLinks = dict()


    # block_map: a dictionary mapping all referenced block numbers to a Block object.
    # If a block is referenced in multiple entries (i.e. a duplicate), then the 
    # block_map entry for the corresponding block number returns the Block 
    # associated with the first such INODE entry.
    block_map = dict()
    inode_map = dict()


    # -------------------------------------------------- The following try
    # block constructs various structures that are later used to generate
    # reports. Note that we use the except block to produce custom error
    # messages
    contents = None
    try:
        with open(filename, mode='r', newline='') as f:
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
                    inode = getInode(inode_map, int(row[1]))
                    inode.onFreeList = True
                    free_inode_entries.append(int(row[1]))

                elif label == INODE:
                    inode_summaries.append(InodeSummary(row))
                    inodeNumber = int(row[1])
                    inode = getInode(inode_map, inodeNumber)
                    inode.inodeType = row[2]
                    inode.linkCount = int(row[6])
                    inode.fileSize  = int(row[10])

                    if inode.inodeType != 's' or inode.fileSize > 60:
                        iblockData = [(i, row[12 + i]) for i in range(0,15)]

                        for iBlockIdx, dataBlockNum in iblockData:
                            blockNumber = int(dataBlockNum)

                            if blockNumber == 0: continue
                            if blockNumber not in block_map:
                                block = getBlock(block_map, blockNumber)
                            else:
                                block = Block()

                            block.entryType = "FROM INODE"

                            if(iBlockIdx < 12):
                                block.indLevel = 0
                                block.offset = iBlockIdx
                            elif(iBlockIdx == 12):
                                block.indLevel = 1
                                block.offset = 12
                            elif(iBlockIdx == 13):
                                block.indLevel = 2
                                block.offset = 268
                            elif(iBlockIdx == 14):
                                block.indLevel = 3
                                block.offset = 65804

                            inode.blockRefs[blockNumber] = block
                            masterBlock = getBlock(block_map, blockNumber)
                            masterBlock.inodeRefs[inodeNumber] = inode
                            masterBlock.entryType = block.entryType

                elif label == DIRENT:
                    directory_entries.append(DirectoryEntry(row))

                elif label == INDIRECT:
                    blockNumber = int(row[5])

                    if blockNumber not in block_map:
                        block = getBlock(block_map, blockNumber)
                    else:
                        block = Block()

                    block.entryType = INDIRECT
                    block.indLevel = int(row[2])
                    block.offset = int(row[3])

                    inodeNumber = int(row[1])
                    owner = getInode(inode_map, inodeNumber)

                    owner.blockRefs[blockNumber] = block
                    masterBlock = getBlock(block_map, blockNumber)
                    masterBlock.inodeRefs[inodeNumber] = owner
                    masterBlock.entryType = block.entryType

                else: #TODO error!
                    pass

    except IOError as x:
        if x.errno == errno.ENOENT: # does not exist
            sys.stderr.write(ERR_DNE.format(filename))
        elif x.errno == errno.EACCESS: # no read permission
            sys.stderr.write(ERR_CNR.format(filename))
        else: # other error
            sys.stderr.write(ERR_UTR.format(filename))
        sys.exit(EXBADEXEC)


    # --------------------------------------------------
    # Detect allocated blocks on freelist and duplicate blocks
    for (blockNumber, block) in block_map.items():

        # ALLOCATED BLOCK X ON FREELIST
        # --------------------------------------------------
        if block.onFreeList and block.entryType != BFREE:
            print(REP_ABOF.format(blockNumber))

        # DUPLICATE X BLOCK Y IN INODE Z AT OFFSET O
        # --------------------------------------------------
        elif len(block.inodeRefs) > 1:
            for inodeNumber, inode in block.inodeRefs.items():
                dupBlock = inode.blockRefs[blockNumber]

                print(REP_DBIIAO.format(
                    indLevelDict[dupBlock.indLevel],
                    blockNumber,
                    inodeNumber,
                    dupBlock.offset))


    # --------------------------------------------------
    # UNREFERENCED BLOCK X
    inodesPerBlock = int(super_summary.block_size/super_summary.inode_size)
    totalInodeBlocks = int(super_summary.n_inodes/inodesPerBlock)
    totalReservedBlocks = int(group_summary.first_inode_block_number) + totalInodeBlocks
    for i in range(totalReservedBlocks, int(group_summary.group_block_count)):
        if i not in block_map:
            print(REP_URB.format(i))


    # --------------------------------------------------
    # Detect allocated inodes on freelist and invalid block numbers
    for inodeNumber, inode in inode_map.items():

        # ALLOCATED INODE X ON FREELIST
        # --------------------------------------------------
        if inode.onFreeList and inode.inodeType != '':
            print(REP_AIOF.format(inodeNumber))
            allocOnFreeList.append(inodeNumber)

        # INVALID T BLOCK X IN INODE Y AT OFFSET Z
        # --------------------------------------------------
        for blockNumber, block in inode.blockRefs.items():
            if blockNumber < 0 or blockNumber > super_summary.n_blocks:
                print(REP_IBIAO.format(
                    indLevelDict[block.indLevel],
                    blockNumber,
                    inodeNumber,
                    block.offset))

        # RESERVED T BLOCK X IN INODE Y AT OFFSET Z
        # --------------------------------------------------
            elif blockNumber < totalReservedBlocks and blockNumber > 0:
                print(REP_RBIAO.format(
                    indLevelDict[block.indLevel],
                    blockNumber,
                    inodeNumber,
                    block.offset))


    # --------------------------------------------------
    # Detect unallocated inodes not on freelist
    for i in range(11, int(group_summary.group_inode_count) + 1):
        if i not in inode_map:
            print(REP_UINOF.format(i))


    # --------------------------------------------------
    # Detect inconsistencies between actual and reported inode link counts
    # Also checks for proper '.' and '..' references and counts
    for i in range(super_summary.n_inodes):
        inodeLinks[i] = 0
    for dirent in directory_entries:

        # DIRECTORY INODE X NAME S UNALLOCATED INODE N
        # Occurs when an inode appears in the free list but also appears in a DIRENT
        # --------------------------------------------------
        if dirent.inode_ref in free_inode_entries and dirent.inode_ref not in allocOnFreeList:
            print(REP_DINUI.format(
                dirent.parent_inode,
                dirent.name,
                dirent.inode_ref))
            continue

        # DIRECTORY INODE X NAME S LINK TO INODE Y SHOULD BE Z
        # Occurs when a DIRENT has name '.' or '..'
        # but the parent inode is not set properly
        # --------------------------------------------------
        if dirent.name == "'.'" or (dirent.name == "'..'" and dirent.parent_inode == 2):
            if dirent.inode_ref != dirent.parent_inode:
                print(REP_DINLTISB.format(
                    dirent.parent_inode,
                    dirent.name,
                    dirent.inode_ref,
                    dirent.parent_inode))

        # DIRECTORY INODE X NAME S INVALID INODE Y
        # Occurs when a DIRENT entry references an invalid inode
        # --------------------------------------------------
        try:
            inodeLinks[dirent.inode_ref] += 1
        except KeyError as e:
            print(REP_DINII.format(
                dirent.parent_inode,
                dirent.name,
                dirent.inode_ref))


    # INODE X HAS N LINKS BUT LINKCOUNT IS M
    # Occurs when actual link count does not equal reported link count
    # --------------------------------------------------
    for inode in inode_summaries:
        if inodeLinks[inode.number] != inode.link_count:
            print(REP_IHLBLI.format(
                inode.number,
                inodeLinks[inode.number],
                inode.link_count))


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

    # try/except needed to force custom exit code
    try:
        args = parser.parse_args()
    except SystemExit:
        exit(EXBADEXEC)

    debug = args.debug
    main(args.filename)
