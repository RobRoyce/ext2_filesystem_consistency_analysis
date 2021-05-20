# EXT2 Filesystem Consistency Analysis

This project is based on an assignment for UCLA's undergraduate-level course -- Operating Systems Principles. The project objectives include:

- Reinforce the basic file system concepts of directory objects, file objects, and free space.
- Gain experience examining, interpreting and processing information in complex binary data structures.
- Reinforce the notions of consistency and integrity and apply them to a concrete and non-trivial problem.


# Details

In this project, we perform consistency analysis on EXT2 filesystem summaries. Specifically, we perform:

- Block Consistency Audits
- I-node Allocation Audits
- Directory Consistency Audits

## Block Consistency Audits
The process flowchart shows the method we developed for performing BCAs. A block is deemed consistent when:
* Its I-node number is not greater than the maximum number of blocks possible
* The block is not illegally allocated to a reserved block number
* Any references to the block are appropriate, and the block is correctly referenced in the free list or in an allocation table

<img width="640" alt="image" src="https://user-images.githubusercontent.com/19367848/119056417-851a2380-b97f-11eb-937a-8a7bacf45359.png">

# Data Structures
The following graph shows the audit-to-data-structure dependency relationships. As you can see, block groups analysis is outside the scope of this project.

<img width="640" alt="image" src="https://user-images.githubusercontent.com/19367848/119056454-92cfa900-b97f-11eb-846e-fae21f845dd6.png">
