#coding=utf-8

import sys, os, json, getopt, shutil
reload(sys)
sys.setdefaultencoding('utf-8')
import random

import requests
import re
import SetupHelper

if __name__ == '__main__':
    rootpass = None

    opts, args = getopt.getopt(sys.argv[1:], 's:', '')
    for option, value in opts:
        if option == '-s':
            rootpass = value
            SetupHelper.setup(os.path.realpath(__file__),
                              'alias go=\"python %s/%s\"' % (SetupHelper.scriptFolder, os.path.basename(__file__)),
                              'Use \'go\' to access search page.')

            # 修改hosts文件，加快stackoverflow访问
            copyFilePath = os.path.expanduser('~/Desktop/hosts')
            shutil.copy('/etc/hosts', copyFilePath)
            copyFile = open(copyFilePath, 'r+')
            try:
                content = copyFile.read()
                if not re.search(r'ajax.googleapis.com', content, re.S):
                    print 'Modify hosts...'
                    copyFile.write('127.0.0.1 ajax.googleapis.com')
                    os.system('echo %s | sudo -S mv %s /etc/hosts' % (rootpass, copyFilePath))
            finally:
                copyFile.close() 

            sys.exit(0)

    os.system('open https://www.tlss.space')
        #response = requests.get('http://www.itechzero.com/google-mirror-sites-collect.html')
        #if response.status_code != 200:
        #    print 'Access Error %s' % response.status_code
        #else:
        #    recommendUrls = re.findall(r'(?<=]</span><a href=\").*?(?=\")', response.text, re.S)
        #    url = recommendUrls[random.randint(0, len(recommendUrls)-1)]
        #    os.system('open %s' % url)
