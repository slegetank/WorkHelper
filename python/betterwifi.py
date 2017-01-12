#coding=utf-8

import xml.etree.ElementTree
from collections import OrderedDict

import sys, os, biplist
reload(sys)
sys.setdefaultencoding('utf-8')
from optparse import OptionParser

import codecs
import re
import SetupHelper

def generateWiFiHistory():
    wifihistory = []
    configPlist = biplist.readPlist("/Library/Preferences/SystemConfiguration/com.apple.airport.preferences.plist")
    for item in configPlist["KnownNetworks"].values():
        if not item.get("LastConnected"):
            continue

        wifihistory.append({"ssid": item["SSIDString"], "date": item["LastConnected"]})

    wifihistory = sorted(wifihistory, key=lambda x:x["date"], reverse=True)[:10]

    retlist = []
    for item in wifihistory:
        retlist.append(item["ssid"])

    return retlist

def generateAvailableList():
    availabledic = OrderedDict()
    ssidlist = os.popen("/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s -x").read()

    e = xml.etree.ElementTree.fromstring(ssidlist)
    if len(e[0]) == 0:
        return

    templist = []
    for wifiinfo in e[0]:
        wifidic = {}
        for i in range(len(wifiinfo)):
            child = wifiinfo[i]
            if child.text == 'SSID_STR':
                wifidic["ssid"] = wifiinfo[i+1].text
            elif child.text == 'RSSI':
                wifidic["rssi"] = wifiinfo[i+1].text

        templist.append(wifidic)

    templist = sorted(templist, key=lambda x:x["rssi"], reverse=False)
    for item in templist:
        availabledic[item["ssid"]] = {"rssi": item["rssi"]}

    return availabledic

if __name__ == '__main__':
    currentSSID = os.popen("/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | awk \'/ SSID/ {print substr($0, index($0, $2))}\'").read().rstrip()

    historylist = generateWiFiHistory()
    avadic = generateAvailableList()

    for key in avadic.keys():
        if not key in historylist:
            del avadic[key]

    for i in range(len(avadic.keys())):
        key = avadic.keys()[i]
        note = ""
        if currentSSID != key:
            if i == 0:
                note = "[Enter] "
                avadic[key]["key"] = ""
            else:
                note = "[%d] " % i
                avadic[key]["key"] = str(i)

        note += key

        rssi = avadic[key]["rssi"].rjust(50-len(note))
        note += rssi

        print note

    choice = raw_input('Choose: ')
    for key in avadic.keys():
        if avadic[key].get("key") == choice:
            print "Connnect to %s ..." % key
            os.system("networksetup -setairportnetwork en0 %s" % key)
