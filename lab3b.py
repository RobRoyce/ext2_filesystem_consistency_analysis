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

LAB3USAGE = "lab3b filename"
LAB3DESC = "Parses EXT2 dump files (.csv) and checks for consistency and integrity."
LAB3FILEHELP = "The file to be analyzed."

# Exit Codes #
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
        print("--------------------------------------------------")
        print("Filename set to {}...".format(filename))
        print("Debug set to {}...".format(debug))
        print("--------------------------------------------------\n")

    super_summary = None
    group_summary = None
    free_block_entries = list()
    free_inode_entries = list()
    inode_summaries = list()
    directory_entries = list()
    indirect_references = list()
    block_map = dict()
    reserved_blocks = [0, 1]

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


    # print out confirmation
    if debug:
        print("--------------------------------------------------")
        print("Superblock Summary: \n{}".format(super_summary))
        print("--------------------------------------------------\n")

        print("--------------------------------------------------")
        print("Inode Summary: \n")
        for summary in inode_summaries:
            print(summary)
        print("--------------------------------------------------\n")


    if super_summary.n_blocks <= 0 or super_summary.n_blocks >= (KiB << 20):
        # TODO: handle insanely large block counts
        pass


    # Initialize block and inode maps
    block_map = BlockMap(size=super_summary.n_blocks)
    inode_map = InodeMap(size=super_summary.n_inodes)
    block_map.set_free(free_block_entries)
    inode_map.set_free(free_inode_entries)



    for inode in inode_summaries:
        inode_map.insert(inode)
        offset = 0
        for blk_n in inode.direct_refs:
            if inode.type != 's':
                if inode.number < 0 or inode.number > super_summary.n_inodes:
                    print_invalid_block(blk_n, inode.number, offset)
                elif inode.number in reserved_blocks:
                    print_reserved()
                else:
                    b = Block(blk_n, t=Btype.DIRECT)
                    block_map.insert(b, inode.number)
                offset += 1

        for blk_n in inode.indirect_refs:
            pass
        for blk_n in inode.dbl_indirect_refs:
            pass
        for blk_n in inode.tpl_indirect_refs:
            pass


    print(inode_map)
    print(block_map)


    # Block Consistency Audits
    # Requirements:
    # Check for valid block pointers in all inodes and indirect blocks
    # for inode in inodes: check for consistency
    # for ind_block in indirect_blocks: check for consistency


    # if debug:
    #     print("--------------------------------------------------")
    #     print("BlockMap size: {}".format(block_map.size))
    #     print("BlockMap count: {}".format(block_map.count))
    #     print("InodeMap size: {}".format(inode_map.size))
    #     print("InodeMap count: {}".format(inode_map.count))
    #     print("--------------------------------------------------")



def print_invalid_block(block_number, inode_number, offset):
    print("INVALID BLOCK {} IN INODE {} AT OFFSET {}".format(block_number, inode_number, offset))

def print_reserved(level, block_number, inode_number, offset):
    if level is Btype.DIRECT:
        level = ""
    elif level is Btype.INDIRECT:
        level = "INDIRECT"
    elif level is Btype.DOUBLE:
        level = "DOUBLE INDIRECT"
    elif level is Btype.TRIPLE:
        level = "TRIPLE INDIRECT"
    else:
        #TODO: error out
        pass

    print("RESERVED {} BLOCK {} IN INODE {} AT OFFSET {}".format(level, block_number, inode_number, offset))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage=LAB3USAGE, description=LAB3DESC)
    parser.add_argument("filename", help=LAB3FILEHELP)
    parser.add_argument("--debug", "-d", action='store_const', const=True, default=False)
    args = parser.parse_args()

    debug = args.debug
    main(args.filename)
