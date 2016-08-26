#coding=utf-8

import sys, os, json, getopt, shutil
reload(sys)
sys.setdefaultencoding('utf-8')
import random

import requests
import re
import SetupHelper

def cleanDerivedData():
    derivedPath = os.path.expanduser('~/Library/Developer/Xcode/DerivedData/')
    os.system('rm -rf %s' % derivedPath)

    print '\xF0\x9f\x8d\xba  Clean derived data finish.'

def showHideFiles():
    showAllFiles = os.popen('defaults read com.apple.finder AppleShowAllFiles').read().strip()
    if showAllFiles == '1':
        showAllFiles = 'false'
    else:
        showAllFiles = 'true'

    os.system('defaults write com.apple.finder AppleShowAllFiles -bool %s' % showAllFiles)
    os.system('killall Finder')

    print '\xF0\x9f\x8d\xba  %s hidden files finished.' % ('Show' if (showAllFiles=='true') else 'Hide')

if __name__ == '__main__':
    # s - setup
    opts, args = getopt.getopt(sys.argv[1:], 's', '')
    for option, value in opts:
        if option == '-s':
            SetupHelper.setup(os.path.realpath(__file__),
                              'alias ltool=\"python %s/%s\"' % (SetupHelper.scriptFolder, os.path.basename(__file__)),
                              'use \'ltool\' to use these little tools.')
            sys.exit(0)

    print '****************************'
    print '1 clean DerivedData'
    print '2 show/hide hidden files'
    print '****************************'

    choice = raw_input('Choose:')
    if choice == '1':
        cleanDerivedData()
    elif choice == '2':
        showHideFiles()
