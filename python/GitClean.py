#coding=utf-8

import sys, os, json, getopt, shutil
reload(sys)
sys.setdefaultencoding('utf-8')
import random

import requests
import re
import SetupHelper

def checkIfCurrentDirectoryIsGit():
    if os.system('git rev-parse') == 0:
        return True
    else:
        return False

if __name__ == '__main__':
    # s - setup
    opts, args = getopt.getopt(sys.argv[1:], 's', '')
    for option, value in opts:
        if option == '-s':
            SetupHelper.setup(os.path.realpath(__file__),
                              'alias xclean=\"python %s/%s\"' % (SetupHelper.scriptFolder, os.path.basename(__file__)),
                              'Use \'xclean\' to clean your git repository throughly')
            sys.exit(0)

    if not checkIfCurrentDirectoryIsGit():
        print 'Not a git dir. Abort'
        sys.exit(-1)

    # read remote info
    remoteUrl = os.popen('git remote get-url --push origin').read().strip()
    print 'Local: %s' % os.popen('basename `git rev-parse --show-toplevel`').read().strip()
    print 'Remote: %s' % remoteUrl
    print 'Status: \n %s' % os.popen('git status -s').read().strip()
    choice = raw_input('Sure to clean it throughly? (y/*)')
    if choice == 'y':
        os.system('git reset --hard && git clean -df')
        print '\xF0\x9f\x8d\xba  Clean finish. Have fun.'
    else:
        print 'Nothing happend.'
