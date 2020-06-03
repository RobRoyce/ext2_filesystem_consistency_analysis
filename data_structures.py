import sys

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

class Block:
    def __init__(self):
        pass

class Inode:
    def __init__(self):
        pass

class SuperBlock:
    def __init__(self):
        pass
