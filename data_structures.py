import sys
from enum import Enum
from pprint import pprint


class SuperBlockSummary:
    def __init__(self, report):
        self.n_blocks = int(report[1])
        self.n_inodes = int(report[2])
        self.block_size = int(report[3])
        self.inode_size = int(report[4])
        self.blocks_per_group = int(report[5])
        self.inodes_per_group = int(report[6])
        self.first_non_reserved_inode = int(report[7])

    def __str__(self):
        s = "Number of blocks: {}\n".format(self.n_blocks)
        s += "Number of inodes: {}\n".format(self.n_inodes)
        s += "Block size: {}\n".format(self.block_size)
        s += "Inode size: {}\n".format(self.inode_size)
        s += "Blocks per group: {}\n".format(self.blocks_per_group)
        s += "Inodes per group: {}\n".format(self.inodes_per_group)
        s += "First non-reserved inode number: {}".format(self.first_non_reserved_inode)
        return s

class GroupSummary:
    def __init__(self, report):
        self.group_number = report[1]
        self.group_block_count = report[2]
        self.group_inode_count = report[3]
        self.n_free_blocks = report[4]
        self.n_free_inodes = report[5]
        self.free_block_bitmap_block_number = report[6]
        self.free_inode_bitmap_block_number = report[7]
        self.first_inode_block_number = report[8]

class FreeBlockEntry:
    def __init__(self, report):
        self.block_number = int(report[1])

class FreeInodeEntry:
    def __init__(self, report):
        self.inode_number = int(report[1])

class InodeSummary:
    def __init__(self, report):
        self.number = int(report[1])
        self.type = report[2]
        self.mode = int(report[3])
        self.owner = int(report[4])
        self.group = int(report[5])
        self.link_count = int(report[6])
        self.last_inode_change_time = report[7]
        self.last_modification_time = report[8]
        self.last_access_time = report[9]
        self.file_size = int(report[10])
        self.n_512_blocks = int(report[11])

        self.direct_refs = list()
        self.indirect_refs = list()
        self.dbl_indirect_refs = list()
        self.tpl_indirect_refs = list()

        if self.type == 'f' or self.type == 'd':
            try:
                for i in range(12, 24):
                    self.direct_refs.append(int(report[i]))

                # TODO - verify these with DIRENT and INDIRECT entries at some point
                self.__populate_indir_refs(int(report[24]))
                self.__populate_dbl_indir_refs(int(report[25]))
                self.__populate_tpl_indir_refs(int(report[26]))
            except:
                # TODO: Error out, these should only be valid for 'f' and 'd'
                pass


    def __populate_indir_refs(self, row):
        # TODO
        self.indirect_refs.append(row)

    def __populate_dbl_indir_refs(self, row):
        # TODO
        self.dbl_indirect_refs.append(row)

    def __populate_tpl_indir_refs(self, row):
        # TODO
        self.tpl_indirect_refs.append(row)

    def __str__(self):
        s = "Inode number {}\n".format(self.number)
        s += "File type: {}\n".format(self.type)
        s += "Mode: {}\n".format(self.mode)
        s += "Owner: {}\n".format(self.owner)
        s += "Group: {}\n".format(self.group)
        s += "Link count: {}\n".format(self.link_count)
        s += "Date last changed: {}\n".format(self.last_inode_change_time)
        s += "Date last modified: {}\n".format(self.last_modification_time)
        s += "Date last access: {}\n".format(self.last_access_time)
        s += "File size: {}\n".format(self.file_size)
        s += "Number of 512 byte blocks: {}\n".format(self.n_512_blocks)
        s += "Direct references: {}\n".format(self.direct_refs)
        s += "Indirect references: {}\n".format(self.indirect_refs)
        s += "Double indirect references: {}\n".format(self.dbl_indirect_refs)
        s += "Triple indirect references: {}\n".format(self.tpl_indirect_refs)
        return s

class DirectoryEntry:
    def __init__(self, report):
        self.parent_inode_number = report[1]
        self.logical_byte_offset = report[2]
        self.inode_number_of_ref_file = report[3]
        self.entry_length = report[4]
        self.name_length = report[5]
        self.name = report[6]

class IndirectBlockReference:
    def __init__(self, report):
        self.inode_number_of_owner = report[1]
        self.level_of_indirection = report[2]
        self.logical_block_offset = report[3]
        self.block_nunmber_of_indirect = report[4]
        self.block_number_of_referenced_block = report[5]

class Btype(Enum):
    FREE = 0
    DIRECT = 1
    INDIRECT = 2
    DOUBLE = 3
    TRIPLE = 4
    UNKNOWN = 5

class Block:
    def __init__(self, n, t=Btype.UNKNOWN):
        self.number = n
        self.ref_count = 0
        self.inode_refs = []
        self.type = t

    def __str__(self):
        s = "Block {}\n".format(self.number)
        s += "Referene count: {}\n".format(self.ref_count)
        s += "Inode references: {}\n".format(self.inode_refs)
        s += "Type: {}".format(self.type)
        return s

class BlockMap:
    def __init__(self, **kwargs):
        self.block_map = dict()
        self.block_list = list()
        self.count = 0
        self.size = 0

        try:
            self.block_list = kwargs['blocks']
        except:
            self.block_list = []

        try:
            self.size = kwargs['size']
        except:
            self.size = 0


        for i in range(self.size):
            self.block_map[i] = Block(i)

        for block in self.block_list:
            # TODO: verify assumption that we'll never get 2 blocks with same number but different contents
            self.block_map[block.number] = block


    def insert(self, block, inode_number):
        n = block.number
        try:
            tmp = self.block_map[n] #if it already exists, increment reference count and append to inode_refs
            self.block_map[n].ref_count += 1
            self.block_map[n].inode_refs.append(inode_number)
            # TODO
        except KeyError as e:
            # does not exist, insert
            self.block_map[n] = block




    def set_free(self, free_block_entries):
        for entry in free_block_entries:
            self.block_map[entry.block_number].type = Btype.FREE

    def check_blocks(self):
        pass

    def __str__(self):
        s = ""
        for i in range(self.size):
            s += "{}:\n{}\n\n".format(i, self.block_map[i])
        return s

class InodeMap:
    def __init__(self, **kwargs):
        self.inode_map = dict()
        self.count = 0
        self.size = 0

        try:
            self.size = kwargs['size']
        except:
            self.size = 0

        for i in range(self.size):
            self.inode_map[i] = None

    def insert(self, inode_s):
        if self.count == self.size:
            # TODO: too many inodes, something went wrong
            pass
        elif self.inode_map[inode_s.number] == None:
            self.inode_map[inode_s.number] = inode_s
        else: # an entry already exists, what TODO?
            pass

    def get(self, k):
        try:
            return self.inode_map[k]
        except:
            return None

    def set_free(self, free_inode_entries):
        for inode_num in free_inode_entries:
            pass # TODO

    def __str__(self):
        s = ""
        for i in range(1, self.size):
            s += "{}:\n{}\n".format(i, self.inode_map[i])
        return s

class Inode:
    def __init__(self):
        self.number = 0


class SuperBlock:
    def __init__(self):
        pass
