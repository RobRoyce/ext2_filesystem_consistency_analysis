import sys

class SuperBlockSummary:
    def __init__(self, report):
        self.__n_blocks = report[1]
        self.__n_indoes = report[2]
        self.__block_size = report[3]
        self.__inode_size = report[4]
        self.__blocks_per_group = report[5]
        self.__inodes_per_group = report[6]
        self.__first_non_reserved_inode = report[7]

class GroupSummary:
    def __init__(self, report):
        self.__group_number = report[1]
        self.__group_block_count = report[2]
        self.__group_inode_count = report[3]
        self.__n_free_blocks = report[4]
        self.__n_free_inodes = report[5]
        self.__free_block_bitmap_block_number = report[6]
        self.__free_inode_bitmap_block_number = report[7]
        self.__first_inode_block_number = report[8]

class FreeBlockEntry:
    def __init__(self, report):
        self.__block_number = report[1]

class FreeInodeEntry:
    def __init__(self, report):
        self.__inode_number = report[1]

class InodeSummary:
    def __init__(self, report):
        self.__inode_number = report[1]
        self.__file_type = report[2]
        self.__mode = report[3]
        self.__owner = report[4]
        self.__group = report[5]
        self.__link_count = report[6]
        self.__last_inode_change_time = report[7]
        self.__last_modification_time = report[8]
        self.__last_access_time = report[9]
        self.__file_size = report[10]
        self.__n_512_blocks = report[11]

        if self.__file_type == 'f' or self.__file_type == 'd':
            try:
                self.__block_addr1 = report[12]
                self.__block_addr2 = report[13]
                self.__block_addr2 = report[14]
                self.__block_addr3 = report[15]
                self.__block_addr4 = report[16]
                self.__block_addr5 = report[17]
                self.__block_addr6 = report[18]
                self.__block_addr7 = report[19]
                self.__block_addr8 = report[20]
                self.__block_addr9 = report[21]
                self.__block_addr10 = report[22]
                self.__block_addr11 = report[23]
                self.__block_addr12 = report[24]
            except:
                # TODO: Error out, these should all be valid for 'f' and 'd'
                pass

class DirectoryEntry:
    def __init__(self, report):
        self.__parent_inode_number = report[1]
        self.__logical_byte_offset = report[2]
        self.__inode_number_of_ref_file = report[3]
        self.__entry_length = report[4]
        self.__name_length = report[5]
        self.__name = report[6]

class IndirectBlockReference:
    def __init__(self, report):
        self.__inode_number_of_owner = report[1]
        self.__level_of_indirection = report[2]
        self.__logical_block_offset = report[3]
        self.__block_nunmber_of_indirect = report[4]
        self.__block_number_of_referenced_block = report[5]
