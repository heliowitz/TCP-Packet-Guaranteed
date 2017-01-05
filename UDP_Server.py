import binascii
import socket
import struct
import sys
import hashlib

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
unpacker = struct.Struct('I I 8s 32s')
packer = struct.Struct('I I 8s')
sequenceNum = 0

# Checks if an incoming packet has a valid checkSum
def isValidCheckSum(incomingPacket):
    values = (incomingPacket[0],incomingPacket[1],incomingPacket[2])
    packed_data = packer.pack(*values)
    chksum = bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")
    if incomingPacket[3] == chksum:
        print('SERVER: checkSums Match, Packet OK')
        return True
    else:
        print('SERVER: checkSums Do Not Match, Packet Corrupt')
        return False

# Checks if an incoming packet has a valid sequence number 
def isValidSequence(incomingPacket):
    values = (incomingPacket[0],incomingPacket[1],incomingPacket[2])
    
    # Check if sequence number is correct and is an ACK packet
    if incomingPacket[1] == sequenceNum:
        return True
    return False

while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    incomingPacket = unpacker.unpack(data)
    print ("SERVER: Received Packet", incomingPacket)
    
    while True:
        # Create response packet indicating error
        values = (1, sequenceNum, b' ')
        packed_data = packer.pack(*values)
        chksum =  bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")

        # Build packet
        # Will send previous sequenceNum if not valid, will send current otherwise
        if isValidCheckSum(incomingPacket) and isValidSequence(incomingPacket):
            values = (1, sequenceNum, b' ')
            packed_data = packet.pack(*values)
            chksum = bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")
            packet = (1,sequenceNum,b' ',chksum)
        else:
            values = (1, (sequenceNum+1)%2, b' ')
            packed_data = packet.pack(*values)
            chksum = bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")
            packet = (1,(sequenceNum+1)%2,b' ',chksum)
        UDP_Packet = unpacker.pack(*packet)

        # Send the UDP Packet
        print ("SERVER: Sent Packet: ", packet)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        sock.sendto(UDP_Packet, addr)            
        break

    # Create response packet indicating success
    sequenceNum = (sequenceNum+1)%2
    print("==============================================")
