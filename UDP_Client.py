import binascii
import socket
import struct
import sys
import hashlib
import signal
import select

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
print("==============================================")

dataList = [b'NCC-1701', b'NCC-1664', b'NCC-1017']
sequenceNum = 0 # Initialize sequence number to 0 
UDP_Packet_Data = struct.Struct('I I 8s 32s')
UDP_Data = struct.Struct('I I 8s')
timeout = 0.009

# Checks if a returning packet has a valid checkSum
def isValidCheckSum(returnPacket):
	#Create the checkSum for comparison
	values = (returnPacket[0],returnPacket[1],returnPacket[2])
	packed_data = UDP_Data.pack(*values)
	chksum =  bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")

	# Compare checkSums to test for corrupt data
	if returnPacket[3] == chksum:
		print('CLIENT: checkSums Match, Packet OK')
		return True
	else:
		print('CLIENT: checkSums Do Not Match, Packet Corrupt')
		return False

# Checks if a returning packet has a valid sequence number 
def isValidSequenceNum(returnPacket):
	values = (returnPacket[0],returnPacket[1],returnPacket[2])

	# Check if sequence number is correct and is an ACK packet
	if returnPacket[0] and returnPacket[1] == sequenceNum:
		return True
	return False

# Create and send packet for each element of data
while dataList:
	packetData = dataList.pop(0)

	# Create the chksum value
	values = (0, sequenceNum, packetData)
	packed_data = UDP_Data.pack(*values)
	chksum =  bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")

	# Build the UDP Packet
	packet = (0,sequenceNum,packetData,chksum)
	UDP_Packet = UDP_Packet_Data.pack(*packet)

	while True:
		# Send the UDP Packet
		print ("CLIENT: Sent Packet: ", packet)
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		sock.sendto(UDP_Packet, (UDP_IP, UDP_PORT))

		# Waits for response
		while True:
			print ("Waiting for packet now...")
			ready = select.select([sock], [],[], timeout)
			# If response received before timeout
			if ready[0]:
				data, addr = sock.recvfrom(1024)
				break
			# Otherwise, resend the packet
			else:
				print ("CLIENT: Timer Expired. Resending...")
				sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
				sock.sendto(UDP_Packet, (UDP_IP, UDP_PORT))

		returnPacket = UDP_Packet_Data.unpack(data)
		print ("CLIENT: Received Packet: ", returnPacket)

		# Check if packet has valid checkSum and seqeunce 
		if isValidCheckSum(returnPacket) and isValidSequenceNum(returnPacket):
			break

	sequenceNum = (sequenceNum+1)%2
	print("==============================================")