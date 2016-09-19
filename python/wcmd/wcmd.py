#coding=utf-8

import sys, os, json, getopt, re
reload(sys)
sys.setdefaultencoding('utf-8')

import threading
import requests
import biplist
import subprocess
import time
import SimpleHTTPServer
import SocketServer 
import thread
import socket

import SSDP

wcmdDeviceUpdateMethod = None
deviceArray = None

localHTTPServer = None

class wdevice(object):
    def __init__(self, ipaddress):
        self.ip = ipaddress
        self.isContra = False

    # public
    def cmd_getStatusEx(self):
        self.commonHttpMethod('getStatusEx')

    def cmd_getSlavelist(self):
        self.commonHttpMethod('multiroom:getSlaveList')

    def cmd_getSysLog(self):
        global sys_log_count

        os.system('clear')
        url = 'http://%s/httpapi.asp?command=getprivatesyslog' % self.ip
        response = requests.get(url)
        print url
        print '*******************************************'
        if response.text == 'unknown command':
            print response.text
            print '*******************************************'
        else:
            os.system('open http://%s/data/sys.log' % self.ip)

    def cmd_contra(self):
        global localHTTPServer

        if not localHTTPServer:
            os.chdir(os.path.dirname(__file__))
            class ReusableTCPServer(SocketServer.TCPServer): allow_reuse_address=True
            localHTTPServer = ReusableTCPServer(("0.0.0.0", 8000), SimpleHTTPServer.SimpleHTTPRequestHandler)
            thread.start_new_thread(localHTTPServer.serve_forever, ())

        if not self.isContra:
            self.isContra = True

            localIP = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
            url = 'http://%s/httpapi.asp?command=%s' % (self.ip, 'setPlayerCmd:play:http://%s:8000/music.mp3' % localIP)
            response = requests.get(url)
            if response.text == 'OK':
                requests.get('http://%s/httpapi.asp?command=setPlayerCmd:vol:80' % self.ip)

            os.system('clear')
            print 'Start play...'
        else:
            self.isContra = False
            requests.get('http://%s/httpapi.asp?command=setPlayerCmd:stop' % self.ip)
            os.system('clear')
            print 'Stop'

    def cmd_ping(self):
        ret = os.popen('pgrep ping %s tail' % self.ip).read().strip()
        if len(ret) == 0:
            subprocess.Popen(['ping', self.ip])
        else:
            processNum = ret.split(' ')[0]
            os.system('kill %s' % processNum)

    # private
    def commonHttpMethod(self, cmd):
        os.system('clear')
        url = 'http://%s/httpapi.asp?command=%s' % (self.ip, cmd)
        response = requests.get(url)
        print url
        print '*******************************************'
        print 'status: %d' % response.status_code
        print response.text
        print '*******************************************'


def deviceAdded(ip):
    global deviceArray

    if not deviceArray:
        deviceArray = []

    device = wdevice(ip)
    deviceArray.append(device)

    if wcmdDeviceUpdateMethod:
        wcmdDeviceUpdateMethod()

def init():
    SSDP.DeviceUpdateMethod = deviceAdded
    SSDP.refreshDevices()

def refresh():
    global deviceArray

    deviceArray = None
    SSDP.refreshDevices()
