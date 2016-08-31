#coding=utf-8

import sys, os, getopt, shutil
import re
reload(sys)
sys.setdefaultencoding('utf-8')

import wcmd
from Tkinter import *

deviceListBox = None
CurrentDevice = None

def deviceAdd():
    global CurrentDevice
    deviceListBox.delete(0, END)

    for device in wcmd.deviceArray:
        deviceListBox.insert(END, device.ip)

    CurrentDevice = wcmd.deviceArray[0]
    deviceListBox.select_set(0)

def listBoxSelected(event):
    global CurrentDevice
    if wcmd.deviceArray == None or len(wcmd.deviceArray) == 0:
        return

    CurrentDevice = wcmd.deviceArray[deviceListBox.curselection()[0]]
    print 'Current device: %s' % CurrentDevice.ip

def refreshDeviceList():
    deviceListBox.delete(0, END)
    wcmd.refresh()

# cmd button method
def cmdButtonMethod(cmd):
    if not CurrentDevice:
        print 'Please select a device.'
        return

    try:
        method = getattr(CurrentDevice, 'cmd_'+cmd)
        method()
    except Exception, e:
        print 'Found no %s' % cmd

def cmdButtonMethodBuilder(cmd):
    return lambda: cmdButtonMethod(cmd)

def main():
    global deviceListBox

    # UI
    rootWindow = Tk()
    rootWindow.title('Device Helper')
    rootWindow.resizable(width=False, height=False)
    deviceListBox = Listbox(rootWindow)
    deviceListBox.bind('<ButtonRelease-1>', listBoxSelected)
    deviceListBox.pack()

    Button(rootWindow, text='Refresh', command=refreshDeviceList).pack()

    for method in dir(wcmd.wdevice):
        if method.startswith('cmd_'):
            cmd = method[4:]
            Button(rootWindow, text=cmd, command=cmdButtonMethodBuilder(cmd)).pack()

    wcmd.wcmdDeviceUpdateMethod = deviceAdd
    wcmd.init()

    rootWindow.mainloop()
