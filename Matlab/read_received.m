% Read packeted file
clc
clear
close all

% Function to calculate how many bit errors each packet contains
% INPUTS: 
%    - a received packet,
%    - a transmitted packet (from the file 'transmitted_payload.bin', that 
%    contains the binary file generated from the transmitted image
%    - the number of the packet
% OUTPUT: errors_package = 1 if the packet contains at least one bit error,
%         0 if contains non
% A message is printed on the command window to tell you how many errors
% the packet contains

function errors_package = calculate_ber(packet_rx,packet_tx,num_packet)
    ber_package = 0;
    errors_package = 0;
    for i = 1:length(packet_rx)
        if packet_rx(i) ~= packet_tx(i)
            ber_package = ber_package + 1;
        end
    end
    if ber_package ~= 0
        errors_package = 1;
    end
    fprintf("There are %d bit errors in package number %d\n",ber_package,num_packet)
end


% Function to correlate the preamble with the received file, until the
% preamble is found for the first tim
%INPUTS: - preamble
%        - receive file
%OUTPUT: index of the first character of the preamble the first time it
%appears in the file
function idx = find_preamble(preamble, receivedData)
    for i = 1:length(receivedData)-length(preamble)
        if receivedData(i:i+length(preamble)-1) == preamble
            idx = i;
            break
        else
            idx = 0;
        end
    end
end

% The following lines recreate the payload that is transmitted, to compare 
% the transmitted packets with the received packets

fileTx = 'capra.jpg';                             % Image file name
scale = 1;                                          % Image scaling factor
fData = imread(fileTx);                                                 % Read image data from file
origSize = size(fData);                                                 % Original input image size
scaledSize = max(floor(scale.*origSize(1:2)),1);                        % Calculate new image size
heightIx = min(round(((1:scaledSize(1))-0.5)./scale+0.5),origSize(1));
widthIx = min(round(((1:scaledSize(2))-0.5)./scale+0.5),origSize(2));
fData = fData(heightIx,widthIx,:);                                      % Resize image
imsize = size(fData);                                                   % Store new image size
binData = dec2bin(fData(:),8);                                          % Convert to 8 bit unsigned binary
trData = reshape((binData-'0').',1,[]).';                               % Create binary stream

msgLen = length(trData);  % Length of the payload

fid = fopen('transmitted_payload.bin', 'wt');
fwrite(fid, trData);
fclose(fid);

% Open and read the received file

fileID = fopen(".\received_files\received_new2_qpsk_2sps_1Msr_5Mbw.bin","r");
receivedData = fread(fileID);
fclose(fileID);

% Define preamble
barker = comm.BarkerCode("Length",13,SamplesPerFrame=13);
preamble = (1+barker())/2;  % Length 13, unipolar
preamble = [preamble', preamble']'; % The baker code is repeated twice
% COMMENT LINE 79 WHEN USING THE FILE received_bpsk_10sps_1Msr_5Mbw.bin

preambleLen = numel(preamble);
numLen = 16;  % each packet number takes two bytes
payloadLen = 10000;
packets = 740;
packetLen = preambleLen+numLen+payloadLen; % total packet bytes including preamble

processed_data = zeros(msgLen,1);
tot_message = msgLen+packets*(preambleLen+1)+packets*(numLen+1);

% Remove garbage before the file is actually transmitted
idx = find_preamble(preamble, receivedData);
receivedData = receivedData(idx:end);
k = 0;  % Count how many packets contain mistakes

% FOR LOOP: checks if the preamble is found, if it is, reads the following
% 16 bits to find the packet number, if its bigger than the total number of
% transmitted packets, the packet is discarded. Then it reads the following
% 10 000 payload bits and compares them to the correct ones

for i = 1:packets+1
      num = receivedData((preambleLen+1):(preambleLen+numLen));
      s = sprintf('%d', num);
      n = bin2dec(s);  
      if n > 742 || n ~= i
          continue
      end
      fprintf("Preamble and number package %d correct\n",n)
      if n == 1 && i == 1
          processed_data(1:10000) = receivedData((preambleLen+numLen+1):packetLen);
          err = calculate_ber(processed_data(1:10000),trData(1:10000),n);
      else
          if n == packets+1
            processed_data(((n-1)*10000)+1:end) = receivedData((preambleLen+numLen+1):9520+preambleLen+numLen);
            err = calculate_ber(processed_data(((n-1)*10000)+1:end),trData((n-1)*10000+1:end),n);
            break
          else
            processed_data(((n-1)*10000)+1:n*10000) = receivedData((preambleLen+numLen+1):packetLen);
            err = calculate_ber(processed_data(((n-1)*10000)+1:n*10000),trData((n-1)*10000+1:n*10000),n);
          end
      end
      receivedData = receivedData(packetLen+1:end);

      idx = find_preamble(preamble, receivedData);
      receivedData = receivedData(idx:end);

      if err ~= 0
          k = k +1;
      end
    
end

fprintf("There are %d packages containing errors\n",k)

% The received file is transformed back in an image
str = reshape(sprintf('%d',processed_data(1:length(processed_data))), 8, []).';
decdata = uint8(bin2dec(str));
receivedImage = reshape(decdata,imsize);

% The image is shown and saved in a file jpg in the same folder of the code
imshow(receivedImage);
imwrite(receivedImage,"received_capra.jpg")
