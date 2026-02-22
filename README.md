# Modulation Schemes for Free Space Optical Communication
This repository contains all GNU Radio flowgraphs, Matlab and python scripts that were used during the project. Additionally, the test data which was transmitted and received during the experiments, as well as a documentation are included.

## Table of contents
1. [GNU Radio flowgraphs](#1-gnu-radio-flowgraphs)
2. [Matlab scripts](#2-matlab-scripts)
3. [Utility scripts](#3-utility-scripts)

## 1. GNU Radio flowgraphs

## 2. Matlab scripts

## 3. Utility scripts
### 3.1 Post-processing for file transmission using GNU Radio flowgraph
If using one of the following flowgraphs ``pluto_bpsk_rx/tx.grc``, ``pluto_qpsk_rx/tx.grc`` or ``pluto_8psk_rx/tx.grc``, the received ``.tmp`` file must be post-processed to reconstruct the file data. For this, the script ``strip_preamble_mod.py`` can be used.  
The original script is authored by duggabe (see [here](https://wiki.gnuradio.org/index.php?title=File_transfer_using_Packet_and_BPSK&oldid=14511)) and was modified.[^old_version]

[^old_version]: Note that the GNU Radio tutorial was reworked and this link refers to the older version which was used in this project.

**Usage:**
````
python .\strip_preamble_mod.py in_file_name.tmp out_file_name.txt
````
The file extension of the output file must match that of the transmitted file.

**What it does:**
- Removes preamble.
- Looks for packet number frames.
- Decodes payload data (Base64) chunk-wise (each chunk is 4 Bytes) and writes it to the output file.
- Prints how many (and which) packet number frames were not detected.
- Compares content of detected packets with transmitted file and checks for bit errors.
- Prints packet error rate.

**Configuration:**  
Before using the script, it should be configured for the used transmission file and setting. The following should be checked and edited if necessary.
- Packet length (only if modified in the flowgraph).
- Preamble, end of file marker, post filler content (only if modified in the embedded python block in the flowgraph).
- Total number of packets for the transmitted file (is displayed in GNU Radio terminal after the transmission has ended).
- Whether the received file content should be compared with the transmitted file.
- Filename of the transmitted file (only if the received file content is compared with the transmitted file).

### 3.2 Missing number check for .txt files for file transmission using GNU Radio flowgraph
If using one of the flowgraphs listed in the previous section, the script ``txt_scanner.py`` can check which numbers are missing in the received file.

**Requirements:**
- The transmitted file contains ordered incrementing numbers (by 1), separated by commas (see ``test_file_tx.txt``).

**Usage:**

````
python .\txt_scanner.py
````

**What it does:**
- Prints how many (and which) numbers are missing in the received file.

**Configuration:**  
Before using the script, it should be configured as follows.
- Edit the name of the received file.
- Edit the list of numbers to be checked to match the transmitted file content.