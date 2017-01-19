#coding=utf-8

import sys, os, biplist, getopt
reload(sys)
sys.setdefaultencoding('utf-8')

import SetupHelper
from collections import OrderedDict

import datetime
import operator

cache_plist = os.path.join(SetupHelper.scriptFolder, "WebCache.plist")

def getCurrentTabs():
    tab_arr = []

    title_url_separator = "`~&"
    tab_separator = "&)#"

    # get current tabs
    safrai_tab_str = os.popen("osascript -e \'set url_list to {}\ntell application \"Safari\"\nset safariWindow to front window\nrepeat with w in safariWindow\nrepeat with t in (tabs of w)\nset TabInfo to (\"\" & (URL of t) & \"%s\" & (name of t) & \"%s\")\ncopy TabInfo to the end of url_list\nend repeat\nend repeat\nend tell\nreturn url_list\'" % (title_url_separator, tab_separator)).read()
    tabs = safrai_tab_str.split(tab_separator)

    for tab in tabs:
        items = tab.split(title_url_separator)
        if len(items) == 2:
            tab_arr.append({"url": items[0].lstrip(', '), "name": items[1]})

    return tab_arr

def cache(tag):
    tab_arr = getCurrentTabs()

    if not os.path.exists(cache_plist):
        web_cache_dic = {}
    else:
        web_cache_dic = biplist.readPlist(cache_plist)

    # timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H:%M:%S')
    # tag = tag if tag else timestamp

    web_cache_dic[tag] = {"timestamp": datetime.datetime.now() , "tabs": tab_arr}
    biplist.writePlist(web_cache_dic, cache_plist)

def clean():
    os.system("osascript -e \'tell application \"Safari\"\nclose every window\nmake new document at end of documents with properties {name:\"Hello World\"}\nend tell\'")

def pop(tag):
    web_cache_dic = biplist.readPlist(cache_plist)
    cachedTags = web_cache_dic.get(tag)
    if not cachedTags:
        return

    tabs = cachedTags["tabs"]
    for item in tabs:
        os.system("osascript -e \'tell application \"Safari\"\ntell front window\nset current tab to (make new tab with properties {URL:\"%s\"})\nend tell\nend tell\'" % item["url"])

    os.system("osascript -e \'tell application \"Safari\"\ntell front window\nclose tab 1\nend tell\nend tell\'")

    # remove cache
    web_cache_dic = biplist.readPlist(cache_plist)
    del web_cache_dic[tag]
    biplist.writePlist(web_cache_dic, cache_plist)

def guessTag():
    tabs = getCurrentTabs()
    if len(tabs) == 0:
        return None

    tlTag = None
    baiduTag = None

    for item in tabs:
        name = item["name"]
        if " - 图灵搜索" in name:
            tlTag = name
        elif "_百度搜索" in name:
            baiduTag = name

    retTag = tlTag if tlTag else baiduTag
    return retTag if retTag else tabs[0]["name"].split(" ")[0]

def printCurrentCache(withindex=False):
    web_cache_dic = OrderedDict(sorted(biplist.readPlist(cache_plist).items(), key=lambda t: t[1]["timestamp"], reverse=True))
    for i in range(len(web_cache_dic.keys())):
        key = web_cache_dic.keys()[i]
        item = web_cache_dic[key]

        print "%s%s [%s]" % ("%d. " % i if withindex else "", item["timestamp"].strftime("%Y-%m-%d %H:%M:%S"), key)

    return web_cache_dic.keys()

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], 'scp', '')
    for option, value in opts:
        # c: cache
        # p: pop
        if option == '-s':
            SetupHelper.setup(os.path.realpath(__file__),
                              'alias wcache=\"python %s/%s\"' % (SetupHelper.scriptFolder, os.path.basename(__file__)),
                              'Use \'wcache + xxx\' to cache your browser.')
            sys.exit(0)
        elif option == '-c':
            defaultTag = guessTag()
            if not defaultTag:
                print "No web found!"
                sys.exit(-1)

            printCurrentCache()
            tag = raw_input('Input a tag [default \"%s\"]: ' % defaultTag)
            if len(tag) == 0:
                tag = defaultTag

            cache(tag)
            printCurrentCache()

            choice = raw_input('Clean browser? [Enter]/*')
            if len(choice) == 0:
                clean()
        elif option == '-p':
            tags = printCurrentCache(True)
            choice = raw_input('Pop which cache? ')

            try:
                choice = int(choice)
            except ValueError:
                print("Input invalid.")
                sys.exit(-1)

            if choice >= len(tags) or choice < 0:
                print("Input invalid.")
                sys.exit(-1)

            tag = tags[choice]
            clean()
            pop(tag)
