#coding=utf-8

import sys, os, json, shutil
from optparse import OptionParser
reload(sys)
sys.setdefaultencoding('utf-8')
import random

import biplist
import re
import SetupHelper
import stat
import time

# 关键的目录有三个：
# 1. ~/Library/Application Support/com.apple.sharedfilelist
# 2. ~/Library/Containers/com.apple.ScreenSharing/Data/Library/Application Support/Screen Sharing/
# 3. ~/Library/Preferences/com.apple.finder.plist

historyList = None

def guessLastConnectedIP():
    global historyList
    lastConnectUrl = None

    # configPlist = biplist.readPlist(os.path.expanduser('~/Library/Preferences/com.apple.finder.plist'))
    # tempUrl = configPlist['FXConnectToLastURL']
    # if tempUrl and tempUrl.startswith("vnc"):
    #     lastConnectUrl = tempUrl

    # 按修改时间排序
    screenShareDir = os.path.expanduser("~/Library/Containers/com.apple.ScreenSharing/Data/Library/Application Support/Screen Sharing/")
    entries = (os.path.join(screenShareDir, fn) for fn in os.listdir(screenShareDir))
    entries = ((os.stat(path), path) for path in entries)
    entries = ((state[stat.ST_MTIME], path) for state, path in entries if path.endswith(".vncloc"))

    historyList = []
    for mdate, path in sorted(entries, reverse=True):
        with open(path, 'r') as configFile:
            content = configFile.read()
            vncurl = re.search(r"(?<=URL</key>\n\t<string>).*?(?=</string>)", content, re.S).group()
            # if lastConnectUrl and lastConnectUrl == vncurl:
            #     continue

            historyList.append({"url": vncurl, "name": os.path.splitext(os.path.basename(path))[0]})

    if not lastConnectUrl and len(historyList) != 0:
        lastConnectUrl = historyList[0]['url']
        del historyList[0]

    return lastConnectUrl

if __name__ == '__main__':
    cmdLine = sys.argv

    # deal with optional
    if '-i' in cmdLine:
        i = cmdLine.index('-i')
        if (i+1) == len(cmdLine):
            cmdLine.insert(i+1, "@")

    parser = OptionParser()
    parser.add_option("-s", action="store_true", dest="setup")
    parser.add_option("-i", default="@", dest="ip")
    (options, args) = parser.parse_args()

    if options.setup:
        SetupHelper.setup(os.path.realpath(__file__),
                          'alias vnc=\"python %s/%s -i\"' % (SetupHelper.scriptFolder, os.path.basename(__file__)),
                          'Use \'vnc\' to connect to vnc server')
        sys.exit(0)
    elif options.ip != "@":
        remoteIP = options.ip
        if not re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", remoteIP):
            print "IP invalid"
            sys.exit(-1)

        os.system("open \"vnc://%s\"" % remoteIP)
        sys.exit(0)

    lastConnectUrl = guessLastConnectedIP()
    if not lastConnectUrl:
        print 'You need to enter an ip'
        sys.exit(-1)

    print "Enter. %s" % lastConnectUrl
    for i in range(len(historyList)):
        dic = historyList[i]
        print "%d. %s" % (i, dic['url'])

    choice = raw_input('Choose: ')
    if choice == '':
        os.system("open %s" % lastConnectUrl)
        sys.exit(0)

    try:
        choice = int(choice)
    except ValueError:
        print("Input invalid.")

    if choice >= len(historyList):
        print("Input invalid.")
        sys.exit(-1)

    os.system("open %s" % historyList[choice]["url"])
