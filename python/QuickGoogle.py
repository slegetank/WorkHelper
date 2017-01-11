#coding=utf-8

import sys, os, shutil
reload(sys)
sys.setdefaultencoding('utf-8')
# import random
from optparse import OptionParser

# import requests
import re
import SetupHelper
from urllib import urlencode

if __name__ == '__main__':
    cmdLine = sys.argv
    rootpass = None

    # deal with optional
    if '-k' in cmdLine:
        i = cmdLine.index('-k')
        if (i+1) == len(cmdLine):
            cmdLine.insert(i+1, "@")
        elif (i+2) < len(cmdLine):
            keyword = cmdLine[i+1]
            for key in cmdLine[i+2:]:
                keyword += " %s" % key

            cmdLine[i+1] = keyword

    parser = OptionParser()
    parser.add_option("-s", action="store_true", dest="setup")
    parser.add_option("-k", default="@", dest="keyword")
    (options, args) = parser.parse_args()

    if options.setup:
        rootpass = options.setup
        SetupHelper.setup(os.path.realpath(__file__),
                          'alias go=\"python %s/%s -k\"' % (SetupHelper.scriptFolder, os.path.basename(__file__)),
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
    elif options.keyword != "@":
        keyword = options.keyword
        data = {'q': keyword}

        os.system("open https://www.tlss.space/search?%s" % urlencode(data))
        sys.exit(0)

    os.system('open https://www.tlss.space')
        #response = requests.get('http://www.itechzero.com/google-mirror-sites-collect.html')
        #if response.status_code != 200:
        #    print 'Access Error %s' % response.status_code
        #else:
        #    recommendUrls = re.findall(r'(?<=]</span><a href=\").*?(?=\")', response.text, re.S)
        #    url = recommendUrls[random.randint(0, len(recommendUrls)-1)]
        #    os.system('open %s' % url)
