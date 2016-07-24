#coding=utf-8

import sys, os, json, getopt
reload(sys)
sys.setdefaultencoding('utf-8')
import random

import requests
import re

response = requests.get('http://www.itechzero.com/google-mirror-sites-collect.html')
if response.status_code != 200:
    print 'Access Error %s' % response.status_code
else:
    recommendUrls = re.findall(r'(?<=]</span><a href=\").*?(?=\")', response.text, re.S)
    url = recommendUrls[random.randint(0, len(recommendUrls)-1)]
    os.system('open %s' % url)

