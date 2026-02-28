# Modulation Schemes for Free Space Optical Communication
This repository contains all GNU Radio flowgraphs, Matlab and python scripts that were used during the project. Additionally, the test data which was transmitted and received during the experiments, as well as a documentation are included.

## Table of contents
1. [GNU Radio flowgraphs](#1-gnu-radio-flowgraphs)
2. [Matlab scripts](#2-matlab-scripts)
3. [Utility scripts](#3-utility-scripts)
4. [Electrical connections](#4-Electrical connections)
5. [Troubleshooting](#5-troubleshooting)

## 1. GNU Radio flowgraphs
If you are new to GNU Radio, it is recommended to have a look at the official [tutorials](https://wiki.gnuradio.org/index.php/Tutorials) first. After that, the following descriptions will be easier to understand.  
While reading the following descriptions, it is adviced to open the corresponding flowgraph image to follow the explanations.  
For this project, GNU Radio 3.10.12 was used.

### 1.1 Phase Shift Keying

#### 1.1.1 Random source transmission
This section refers to the flowgraphs ``ber_bpsk.grc``, ``ber_qpsk.grc``, ``ber_8psk.grc`` and ``ber_16psk.grc``. The diagram images can be found here: [ber_bpsk.pdf](GNU_Radio/Images/ber_bpsk.pdf), [ber_qpsk.pdf](GNU_Radio/Images/ber_qpsk.pdf), [ber_8psk.pdf](GNU_Radio/Images/ber_8psk.pdf), [ber_16psk.pdf](GNU_Radio/Images/ber_16psk.pdf).

The flowgraphs transmit a random source, which are bytes with values between 0 and 255. A random sequence of 30,000 bytes is sent and repeated while the flowgraph is running.

The transmission data is then modulated with the generic ``Constellation Modulator`` block, which can take different ``Constellation Object`` blocks as input. The ``Constellation Modulator`` also applies a Root-raised cosine filter. Since differential encoding is used, the constellation type parameter of the ``Constellation Object`` must not be set to ``QPSK`` as that prevents differential encoding and will not work. Instead, ``DQPSK`` may be selected. However, it is recommended to not use the preset types and instead set it to ``Variable Constellation`` and define symbol mapping and constellation points manually.

After that, the modulated signal is sent to the Pluto SDR (configured as the transmitter) using the ``PlutoSDR Sink`` block via USB and received at the Pluto SDR (Configured as the receiver), which sends the signal back to the computer via USB using the ``PlutoSDR Source`` block. In this project, two SDRs were used (one as transmitter, one as receiver). Thus, the IP in the Pluto blocks must be set accordingly in the ``IIO context URI`` parameter.

A ``FFT Root Raised Cosine Filter`` block is needed to match the filter at the transmitter.

In the ``Symbol Sync`` block, the symbols are synchronized. Different algorithms in the ``Timing Error Detector`` can be tested, while in our project y[n]y'[n] Maximum likelihood turned out to be the best overall.

The ``Costas Loop`` block locks the phase, making the constellation points appear as expected in the ``QT GUI Constellation Sink`` block. The ``Order`` parameter must be set according to how many constellation points are used. The exception is 16-PSK, where the order is still 8 (8 is the maximum value).

The ``Constellation Decoder`` block then decodes the complex signal to bytes.

Since differential encoding is used at the transmitter, a ``Differential Decoder`` block is required at the receiver.

The ``Map`` block remaps the symbol bytes and the order of the list must be the same as in the ``Constellation Object``.

Until now, the signal contains log~2~(p) bits per byte, where p is the number of constellation points. Therefore, it must be unpacked such that each byte contains one bit.

Finally, the data is written to the file as configured in the ``File Sink`` block.

The ``Probe Rate`` block regularly prints the bit rate to the terminal.

#### 1.1.2 General File transmission
This section refers to the flowgraphs ``pluto_bpsk_tx/rx.grc``, ``pluto_qpsk_tx/rx.grc`` and ``pluto_8psk_tx/rx.grc``. The diagram images can be found here: [pluto_bpsk_tx.pdf](GNU_Radio/Images/pluto_bpsk_tx.pdf), [pluto_bpsk_rx.pdf](GNU_Radio/Images/pluto_bpsk_rx.pdf), [pluto_qpsk_tx.pdf](GNU_Radio/Images/pluto_qpsk_tx.pdf), [pluto_qpsk_rx.pdf](GNU_Radio/Images/pluto_qpsk_rx.pdf), [pluto_8psk_tx.pdf](GNU_Radio/Images/pluto_8psk_tx.pdf), [pluto_8psk_rx.pdf](GNU_Radio/Images/pluto_8psk_rx.pdf).

These flowgraphs transmit any file, implementing the packeting inside the flowgraph. In contrast to repeated source transmission, the receiver should be turned on before the transmitter. Thus, the flowgraphs are splitted into a transmitter and receiver.  
A GNU Radio [tutorial](https://wiki.gnuradio.org/index.php?title=File_transfer_using_Packet_and_BPSK&oldid=14511)[^old_version] was used as a starting point (author: Dubbage) and modified.

**Transmitter:**  
A HIER block ``File Source Packaged`` is used to read the file which should be transmitted and does the following (the diagram image can be found here: [hier_file_source_packaged.pdf](GNU_Radio/Images/hier_file_source_packaged.pdf)).

- It starts with an embedded python block ``EPB: File Source to Tagged Stream``, which first sends a preamble 64 times, then sends the file data in packets (each packet contains as many bytes as configured in the ``Pkt_len`` parameter of the ``File Source Packaged`` block). In front of each file data packet, the packet number is put. At the end, an end of file marker, the file name and a repeated post filler (64 times) is sent. A tag with the (new) packet length is also applied to make it a tagged stream (required by other blocks later). 
While the file data is encoded in Base64, everything else (including the packet number) is not encoded. The encoded file data packet is 4/3 as long as the decoded one, since Base64 encodes 3 Bytes into 4 Bytes.  
The **preamble** is ``&U...U]`` (50 times U), the **packet number frame** ``[000001]`` (always 6 digits, therefore a maximum of 999,999 packets are possible. This means a maximum file size of 999,999 times Pkt_len bytes. If larger files are desired, increase packet length or adjust packet number frame.), the **end of file marker** ``%UUU#EOF`` (followed by the file name), the **post filler** ``%UUU#EOF`` followed by 43 times the character ``U`` and ending with ``]``.
- After the embedded python block, a CRC32 code is also attached to each packet by the ``Stream CRC32`` block to detect errors at the receiver. The ``Mode`` parameter must be set to generate.
- Finally a header is also attached (including the access key ``11100001010110101110100010010011``) using the ``Protocol Formatter`` and ``Tagged Stream Mux`` blocks. The access key is used at the receiver for correlation.

As in random source transmission, the data is modulated by the ``Constellation Modulator`` block using a ``Constellation Object`` (which is configured depending on the number of constellation points). For more details, see the previous section.

The modulated signal is then sent to the Pluto SDR (configured as transmitter) using the ``PlutoSDR Sink`` via USB and sent to the Pluto SDR (configured as receiver).

**Receiver:**  
The received signal is sent to the computer via USB using the ``PlutoSDR Source`` block.

A ``FFT Root Raised Cosine Filter`` block is used to match the filter at the transmitter (which is inside of the ``Constellation Modulator`` block).

In the ``Symbol Sync`` block, the symbols are synchronized. Different algorithms in the ``Timing Error Detector`` can be tested, while in our project y[n]y'[n] Maximum likelihood turned out to be the best overall.

The ``Costas Loop`` block locks the phase, making the constellation points appear as expected in the ``QT GUI Constellation Sink`` block. The ``Order`` parameter must be set according to how many constellation points are used. The exception is 16-PSK, where the order is still 8 (8 is the maximum value).

The ``Constellation Decoder`` block then decodes the complex signal to bytes.

Since differential encoding is used at the transmitter, a ``Differential Decoder`` block is required at the receiver.

The ``Probe Rate`` block at this time does not print the bit rate, but the symbol rate (except for BPSK as it is the same there).

A HIER block ``File Sink Unpackaged mod_scheme`` is used to perform further actions before writing the data to a file. Since the mapping and unpacking depends on the constellation points, there is one block for each modulation scheme (the diagram images can be found here: [hier_file_sink_unpackaged_bpsk.pdf](GNU_Radio/Images/hier_file_sink_unpackaged_bpsk.pdf), [hier_file_sink_unpackaged_qpsk.pdf](GNU_Radio/Images/hier_file_sink_unpackaged_qpsk.pdf), [hier_file_sink_unpackaged_8psk.pdf](GNU_Radio/Images/hier_file_sink_unpackaged_8psk.pdf)).

- The ``Map`` block remaps the symbol bytes and the order of the list must be the same as in the ``Constellation Object`` (not needed in BPSK, since there is only 0 and 1).
- Until now, the signal contains log~2~(p) bits per byte, where p is the number of constellation points. Therefore, it must be unpacked such that each byte contains one bit (not needed in BPSK, since symbol is only 1 bit).
- The ``Correlate Access Code - Tag Stream`` block looks for the access code. If not found (with the ``Threshold`` parameter, the maximum number of wrong bits allowed can be changed), the packet will already be dropped at this point. The access code used is ``TODO``.
- The data is repacked from 1 relevant bit per byte (that is how the previous block outputs the data) to 8 relevant bits per byte (that is how the next block expects the data if ``Packed`` is true).
- The ``Stream CRC32`` is now set to ``Mode`` check. It drops packets when errors in the payload are detected.
- Finally, the data (without header and CRC32 checksum) is written to the configured file.

The ``File Sink Unpackaged mod_scheme`` block also outputs the input and output signal of the ``Correlate Access Code - Tag Stream`` block, comparing them in ``QT GUI Time Sink`` blocks. If, during transmission, there is an input signal but no output signal, the access code correlation failed and the packet is dropped. If there is no output signal visible during the entire transmission, it indicates something is wrong with the flowgraph.

#### 1.1.3 File transmission using pre-processed .bin files
This section refers to the flowgraphs ``raw_file_bpsk_tx/rx.grc`` and ``raw_file_qpsk_tx/rx.grc``. The diagram images can be found here: [raw_file_bpsk_tx.pdf](GNU_Radio/Images/raw_file_bpsk_tx.pdf), [raw_file_bpsk_rx.pdf](GNU_Radio/Images/raw_file_bpsk_rx.pdf), [raw_file_qpsk_tx.pdf](GNU_Radio/Images/raw_file_qpsk_tx.pdf), [raw_file_qpsk_rx.pdf](GNU_Radio/Images/raw_file_qpsk_rx.pdf).


### 1.2 Important notes using Pluto SDR
When testing flowgraphs and if the TX and RX SMA connectors of the SDRs are directly connected to each other with a cable, make sure to set the ``Attenuation TX1`` parameter of the ``PlutoSDR Sink`` block to **at least 20 dB** to prevent damaging the device. Only when using antennas or the laser, it can be set to 0 dB.

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

# 4. Electrical connections
All the design files are available in the folder "ElectricalDesign", which is subdivided into "Version 1" and "Version 2". The first is the one used during our tests. The second is the improved version with all the problems we encountered fixed, plus some other nice features like pin names, use of rule areas, fixed voltage reference for the amplifier, but with the possibility to switch back to the DAC if needed, and monitor of the amplifier voltage directly from VBUS of INA226, while shunt voltage keeps reading the photodiode resistor voltage. Moreover pull-up resistors were added.

# 5. Troubleshooting

## 5.1 General

**Q:** Impossible to find DAC or ADC or setup is not successfu (error from the code).
**A:** Check that that the 2 wires of I2C are connected properly SDA->SDA SCL->SCL, check to have a ground connection between the Arduino and the receiver, in case you are using an external power supply. If this is ok then if you are using an Arduino Uno R4 you need external pullup resistors (from 2.2k to 20k connected to 5V or 3.3V). If you are using an Arduino Mega check which I2C pair you are using, there are many! If free always choose the first couple, located at pin 20 and 21. 
The schematics annotated of the first version are available in  ``ElectricalDesign/Version1/Pinout Receiver.png``, for the second version the pins are annotated in the silkscreen.

## 5.2 GNU Radio flowgraphs
**Q:** The signal is bad, what could be wrong?
**A:** Check if the laser is on (also the current). Check the laser alignment towards the receiver. Check the attenuation of the ``PlutoSDR Sink`` block and set it to 0 dB (**not** if TX and RX directly connected to each other via SMA cable). Check that the IP addresses of the SDRs are configured correctly in the ``PlutoSDR Sink`` and ``PlutoSDR Source`` blocks.

**Q:** The SDR is not detected by GNU Radio (terminal shows an error when running the flowgraph), what should i do?
**A:** Check the IP addresses of the SDRs in the flowgraph, but also make sure they are correct by clicking on the SDR in file explorer and opening config.txt. The ip is listed at ``ipaddr`` under ``[NETWORK]`` (you can also change the address). Also make sure that ``usb_ethernet_mode`` under ``[SYSTEM]`` is set to rndis. If that still does not help, check the computer network (on Windows via ``ipconfig`` in the terminal). If no Ethernet adapter category is listed, the RNDIS driver might need to be reinstalled by opening the device manager → right click unknown device → update driver → browse my computer → let me pick from a list → network adapters → microsoft → remote NDIS compatible device.
