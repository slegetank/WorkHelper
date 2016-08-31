#coding=utf-8

import sys, os, getopt, shutil
import re
reload(sys)
sys.setdefaultencoding('utf-8')

from socket import *
import struct
import threading
import time

deviceArray = []
MCAST_IP = '239.255.255.250'
MCAST_PORT = 1900
msearchSocket = None
searchThread = None

# methods
DeviceUpdateMethod = None

def refreshDevices():
    global deviceArray
    global msearchSocket
    global searchThread
    deviceArray = []

    msearchSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    msearchSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    msearchSocket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    msearchSocket.setsockopt(IPPROTO_IP, IP_MULTICAST_LOOP, 0)
    msearchSocket.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 2)
    mreq = struct.pack('4sl', inet_aton(MCAST_IP), MCAST_PORT)
    msearchSocket.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
    msearchSocket.bind(('', 0))

    sendMSearch()
    threading.Timer(3, sendMSearch)
    searchThread = threading.Thread(target=ssdpThreadMethod)
    searchThread.setDaemon(True)
    searchThread.start()

def sendMSearch():
    msearchSocket.sendto('M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 3\r\nST: ssdp:wiimudevice\r\nUSER-AGENT: mac/1.0 UPnP/1.1 upnpx/1.0\r\n\r\n', (MCAST_IP, MCAST_PORT))

def ssdpThreadMethod():
    while True:
        if not searchThread.isAlive():
            break

        response = msearchSocket.recv(1024)
        dealWithSSDPResponse(response)

def dealWithSSDPResponse(response):
    ip = re.search(r'(?<=LOCATION: http://).*?(?=:)', response)
    if not ip:
        return

    ip = ip.group()

    if not ip in deviceArray:
        deviceArray.append(ip)

        if DeviceUpdateMethod:
            DeviceUpdateMethod(ip)

if __name__ == '__main__':
    refreshDevices()
