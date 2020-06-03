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
    block_map = dict() # key: block number, value: list of tuple (block_no, type)
    inode_map = dict() # key: inode number, value: list of tuple (inode_no, type)

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

                    inodeNumber = row[1]
                    if inodeNumber not in inode_map:
                        inode_map[inodeNumber] = list()

                    inodeType = 'UNALLOCATED' if (row[2] == 0) else 'ALLOCATED' 
                    inode_map[inodeNumber].append((inodeNumber, inodeType))

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


    ifree_set = set([ifree.inode_number for ifree in free_inode_entries])

    for (_, inodeList) in inode_map.items():
        for (inodeNumber, inodeType) in inodeList:
            print(inodeNumber, inodeType)
            if inodeNumber in ifree_set and inodeType == 'ALLOCATED':
                print("ALLOCATED INODE {} ON FREELIST".format(inodeNumber))
            elif inodeNumber not in ifree_set and inodeType == 'UNALLOCATED':
                print("UNALLOCATED INODE {} NOT ON FREELIST".format(inodeNumber))

    # Build map using block number as index and a list of inodes that reference
    # that block as items

    if debug:
        print("Beginning block map initialization.")
        print("Number of blocks: {}".format(super_summary.n_blocks))

    # for i in range(0, super_summary.n_blocks):
    #     block_map[i] = list()

    # for inode in inode_summaries:
    #     for ref in inode.direct_refs:
    #         block_map[ref].append(inode.number)
    #     for ref in inode.indirect_refs:
    #         block_map[ref].append(inode.number)
    #     for ref in inode.dbl_indirect_refs:
    #         block_map[ref].append(inode.number)
    #     for ref in inode.tpl_indirect_refs:
    #         block_map[ref].append(inode.number)

    # if debug:
    #     print("Displaying blocks and the inodes in which they are referenced...")
    #     pprint(block_map)
    #     for block, inode in block_map.items():
    #         print("Block {} is referenced {} times...".format(block, len(block_map[block])))

    # tmp = dict() # block[i] = (ref_count, [list_of_inodes])
    # for block, inodes in block_map.items():
    #     tmp[block] = (len(block_map[block]), block_map[block])

    # pprint(tmp)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage=LAB3USAGE, description=LAB3DESC)
    parser.add_argument("filename", help=LAB3FILEHELP)
    parser.add_argument("--debug", "-d", action='store_const', const=True, default=False)
    args = parser.parse_args()
    debug = args.debug
    main(args.filename)
