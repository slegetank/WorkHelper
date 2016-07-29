#coding=utf-8

import sys, os, json, getopt, shutil
reload(sys)
sys.setdefaultencoding('utf-8')
import random

import requests
import re

if __name__ == '__main__':
    rootpass = None

    opts, args = getopt.getopt(sys.argv[1:], 'i:', '')
    for option, value in opts:
        if option == '-i':
            rootpass = value

    if rootpass:
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

        # 修改zsh文件，添加go命令访问google
        if not os.path.exists(os.path.expanduser('~/.zshrc')):
            print 'Found no .zshrc, exit'
            exit(0)

        # 拷贝至根目录
        print 'Copy to ~...'
        scriptPath = os.path.expanduser('~/QuickGoogle.py')
        if os.path.exists(scriptPath):
            os.remove(scriptPath)

        shutil.copyfile(os.path.realpath(__file__), scriptPath)

        print 'Modify .zshrc...'
        zshrc = open(os.path.expanduser('~/.zshrc'), 'r+')
        try:
            content = zshrc.read()
            if not re.search(r'alias go', content, re.S):
                zshrc.write('alias go=\"python ~/QuickGoogle.py\"')
        finally:
            zshrc.close()
    else:
        response = requests.get('http://www.itechzero.com/google-mirror-sites-collect.html')
        if response.status_code != 200:
            print 'Access Error %s' % response.status_code
        else:
            recommendUrls = re.findall(r'(?<=]</span><a href=\").*?(?=\")', response.text, re.S)
            url = recommendUrls[random.randint(0, len(recommendUrls)-1)]
            os.system('open %s' % url)
