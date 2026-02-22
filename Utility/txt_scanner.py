# Author: Cemal Yilmaz

"""
Checks how many (and which) numbers are received in the received file.
Assumes the number range defined in this file and separated by commas.
"""

import sys

# load RX file
filename_rx = "\\test_file_rx_new.txt"

with open(sys.path[0] + filename_rx, 'r') as f_rx:
    content_rx = f_rx.read()

# parse received numbers as integers and ignore any non-numeric content
received_numbers = set()
for num in content_rx.split(','):
    try:
        received_numbers.add(int(num.strip()))
    except ValueError:
        pass

# store numbers that were sent originally (1 tp 1000000)
sent_numbers = [num for num in range(1,1000001)] # <-- edit this to the original range of sent numbers

# check if all sent numbers are in the received content
missing_number_cnt = 0
missing_numbers = []
for number in sent_numbers:
    if number not in received_numbers:
        missing_number_cnt += 1
        missing_numbers.append(number)

print("Missing number count:", missing_number_cnt)
print("Missing numbers:", missing_numbers)