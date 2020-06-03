import sys
from enum import Enum
from pprint import pprint


class SuperBlockSummary:
    def __init__(self, report):
        self.n_blocks = int(report[1])
        self.n_indoes = int(report[2])
        self.block_size = int(report[3])
        self.inode_size = int(report[4])
        self.blocks_per_group = int(report[5])
        self.inodes_per_group = int(report[6])
        self.first_non_reserved_inode = int(report[7])

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
        self.block_number = report[1]

class FreeInodeEntry:
    def __init__(self, report):
        self.inode_number = report[1]

class InodeSummary:
    def __init__(self, report):
        self.number = int(report[1])
        self.type = report[2]
        self.mode = report[3]
        self.owner = report[4]
        self.group = report[5]
        self.link_count = report[6]
        self.last_inode_change_time = report[7]
        self.last_modification_time = report[8]
        self.last_access_time = report[9]
        self.file_size = report[10]
        self.n_512_blocks = report[11]

        self.direct_refs = list()
        self.indirect_refs = list()
        self.dbl_indirect_refs = list()
        self.tpl_indirect_refs = list()

        if self.type == 'f' or self.type == 'd':
            try:
                self.direct_refs.append(int(report[12]))
                self.direct_refs.append(int(report[13]))
                self.direct_refs.append(int(report[14]))
                self.direct_refs.append(int(report[15]))
                self.direct_refs.append(int(report[16]))
                self.direct_refs.append(int(report[17]))
                self.direct_refs.append(int(report[18]))
                self.direct_refs.append(int(report[19]))
                self.direct_refs.append(int(report[20]))
                self.direct_refs.append(int(report[21]))
                self.direct_refs.append(int(report[22]))
                self.direct_refs.append(int(report[23]))

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

class Block:
    def __init__(self, n, t=Btype.FREE):
        self.number = n
        self.ref_count = 0
        self.inode_refs = []
        self.type = t

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
            self.block_map[i] = None

        for block in self.block_list:
            # TODO: verify assumption that we'll never get 2 blocks with same number but different contents
            self.block_map[block.number] = block


    def insert(self, block):
        n = block.number
        try:
            tmp = self.block_map[n] # make sure it doesn't exist yet
        except KeyError as e:
            # does not exist, insert
            pass

    def set_free(self, free_block_entries):
        for block_num in free_block_entries:
            b = Block(block_num, Btype.FREE)
            self.block_map[block_num] = b

    def check_blocks(self):
        pass

    def __str__(self):
        s = ""
        for i in range(self.size):
            s += "{}: {}\n".format(i, self.block_map[i])
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

    def insert(self, inode):
        if self.count == self.size:
            return False
        elif self.inode_map[inode.number] == None:
            self.inode_map[inode.number] = inode
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

class Inode:
    def __init__(self):
        self.number = 0


class SuperBlock:
    def __init__(self):
        pass
