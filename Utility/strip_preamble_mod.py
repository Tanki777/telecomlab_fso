#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Title: strip_preamble
# Author: Barry Duggan
# Modified by: Cemal Yilmaz

"""
Strip preamble and trailer packets from input file.
Detects packet number frames and decodes payload chunks, writing the decoded data to output file.
Optionally compares the content of the decoded output file with the original transmitted file for bit errors.
"""

import os.path
import sys
import base64
import numpy as np

_debug = 1          # set to zero to turn off diagnostics
state = 0
Pkt_len = 52
chunks_per_pkt = int(np.ceil(Pkt_len/3))

if (len(sys.argv) < 3):
    print ('Usage: python3 strip_preamble.py <input file> <output file>')
    print ('Number of arguments=', len(sys.argv))
    print ('Argument List:', str(sys.argv))
    exit (1)
# test if input file exists
fn = sys.argv[1]
if not(os.path.exists(fn)):
    print(fn, 'does not exist')
    exit (1)
# open input file
f_in = open (fn, 'rb')

# open output file
f_out = open (sys.argv[2], 'wb')

debug_iter = 0
detected_pkt_num_frames = set()
current_pkt_num = None
current_pkt_payload_chunk_num = 1
first_chunk_after_preamble = None

while True:

    # Preamble region
    if (state == 0):
        buff = f_in.read (Pkt_len)
        b_len = len(buff)

        # If first byte is % and last byte is ], detected preamble packet
        if ((buff[0] == 37) and (buff[51] == 93)):
            continue

        # Otherwise, enter payload region and move file pointer back by 1 packet
        else:
            if (_debug):
                print ("End of preamble")
            f_in.seek(-Pkt_len, os.SEEK_CUR)
            state = 1
            continue

    # Payload region
    elif (state == 1):
        buff = f_in.read(4)
        b_len = len(buff)

        if b_len == 0:
            print ('End of file')
            break

        if (buff[0] == 37):     # '%'
            if (buff == b'%UUU'):
                print ("End of text")
                buff = f_in.read(4)     # skip next four 'U's
                rcv_fn = []
                i = 0

                while (i < 44):
                    ch = f_in.read(1)
                    if (ch == b'%'):
                        break
                    rcv_fn.append((ord)(ch))
                    i += 1
                rf_len = len (rcv_fn)
                x = 0

                while (x < rf_len):
                    rcv_fn[x] = str((chr)(rcv_fn[x]))
                    x += 1
                ofn = "".join(rcv_fn)
                print ("Transmitted file name:",ofn)
                state = 2

                break
        
        # Check if next chunk indicates start of a packet
        elif buff[0] == "[".encode('utf-8')[0]:
            buff += f_in.read(4)  # read the rest of the packet number frame
            
            # Parse packet number from frame
            pkt_num_str = buff[1:7].decode('utf-8')

            # Handle case if packet number inside [] is not a valid integer
            try:
                pkt_num = int(pkt_num_str)
                current_pkt_num = pkt_num
                detected_pkt_num_frames.add(pkt_num)
            except ValueError:
                print(f"Invalid packet number format: {pkt_num_str}")
                current_pkt_num = None
                continue
        
        # current chunk in buffer are payload bytes --> decode
        else:
            # Skip chunk if current packet number was not detected successfully
            if current_pkt_num is None:
                continue
            
            else:
                # decode Base64
                data = base64.b64decode(buff)
                f_out.write (data)
                current_pkt_payload_chunk_num += 1

            if current_pkt_payload_chunk_num > chunks_per_pkt:
                print(f"Warning: detected more chunks in a packet than expected (pkt num: {current_pkt_num}, chunk num: {current_pkt_payload_chunk_num})")

            # If current chunk is last chunk of the packet, reset counter
            if current_pkt_payload_chunk_num == chunks_per_pkt:
                current_pkt_payload_chunk_num = 1
        
f_in.close()
f_out.close()

missing_number_cnt = 0
missing_numbers = []

# Packet numbers that should be there
if len(detected_pkt_num_frames) > 0:
    TX_PKT_CNT = 132479 # <-- edit this to the total numer of packets displayed in the flowgraph
    tx_pkt_numbers = [num for num in range(1, TX_PKT_CNT+1)]

    # check if all sent numbers are in the received data
    for number in tx_pkt_numbers:
        if number not in detected_pkt_num_frames:
            missing_number_cnt += 1
            missing_numbers.append(number)

    print("Missing number count:", missing_number_cnt)
    print(f"Packet drop rate: {missing_number_cnt/TX_PKT_CNT*100:.5f}%")
    print("Missing numbers:", missing_numbers)


# Reads transmitted and received files, comparing the content for bit errors packet by packet.
def compare_detected_packets():
    print("Comparing RX file with TX file...")

    file_tx = open("test_file_tx.txt", 'rb') # <-- edit this to the original transmitted file name
    file_rx = open(sys.argv[2], 'rb')
    packets_tx = {}
    packets_rx = {}
    pkt_num = 1
    total_bit_err = 0
    pkts_with_error = 0

    # Read transmitted file packets and store in dictionary
    while True:
        buff_tx = file_tx.read(Pkt_len)

        if not buff_tx:
            break

        packets_tx[pkt_num] = buff_tx
        pkt_num += 1

    print("Done reading TX file.")

    # Reset packet number
    pkt_num = 1

    # Read received file packets and store in dictionary
    while True:
        buff_rx = file_rx.read(Pkt_len)

        if not buff_rx:
            break
        
        # Skip packet numbers that are in missing numbers list
        if pkt_num in missing_numbers:
            pkt_num += 1
            while pkt_num in missing_numbers:
                pkt_num += 1
            packets_rx[pkt_num] = buff_rx
            pkt_num += 1
            continue
        packets_rx[pkt_num] = buff_rx
        pkt_num += 1

    print("Done reading RX file.")

    # Compare packet content bitwise for packet numbers NOT in missing numbers list
    for pkt_num in sorted(packets_tx.keys()):
        if pkt_num in missing_numbers:
            continue
        pkt_tx = packets_tx.get(pkt_num)
        pkt_rx = packets_rx.get(pkt_num)

        if pkt_tx is None:
            print(f"Packet {pkt_num} missing in transmitted file")
            continue

        if pkt_rx is None:
            print(f"Packet {pkt_num} missing in received file")
            continue

        bit_err = 0

        # Compare packet content bitwise
        for i in range(min(len(pkt_tx), len(pkt_rx))):
            if pkt_tx[i] != pkt_rx[i]:
                bit_err += 1

        if bit_err > 0:
            print(f"Packet {pkt_num}: Bit errors = {bit_err}")
            pkts_with_error += 1
        total_bit_err += bit_err


    file_tx.close()
    file_rx.close()

    print(f"Total bit errors: {total_bit_err}")
    print(f"Number of packets with errors: {pkts_with_error}")
    print(f"Missing packets: {missing_number_cnt}")
    print(f"Combined packet error and drop rate: {(pkts_with_error + missing_number_cnt)/(TX_PKT_CNT)*100:.5f}%")

compare_detected_packets() # <-- comment out to skip comparison