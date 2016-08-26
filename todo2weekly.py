#coding=utf-8

import sys, os, json, getopt, re
reload(sys)
sys.setdefaultencoding('utf-8')

import requests
import biplist
import SetupHelper
from datetime import date
from dateutil.relativedelta import relativedelta, FR

global wiimu_account
global wiimu_pass

todo_page_id = '1245397'
configPlistPath = '%s/.wiimuconfig.plist' % os.path.expanduser('~')

def getGerritAccountPass():
    global wiimu_account
    global wiimu_pass

    if os.path.exists(configPlistPath):
        configPlist = biplist.readPlist(configPlistPath)
        wiimu_account = configPlist.get('wiimuaccount', '')
        wiimu_pass = configPlist.get('wiimupass', '')
    else:
        configPlist = {'wiimuaccount':'', 'wiimupass':''}
        biplist.writePlist(configPlist, configPlistPath)

    if len(wiimu_account) == 0 or len(wiimu_pass) == 0:
        print 'This is your first time use this.'
    while(len(wiimu_account) == 0 or len(wiimu_pass) == 0):
        tempAccount = raw_input('Please enter your Wiimu account:')
        tempPass = raw_input('Please enter your Wiimu pass:')

        response = requests.get('https://sh.linkplay.com:8081/artifactory/api/security/encryptedPassword', auth=(tempAccount, tempPass))
        if response.status_code == 200:
            wiimu_account = tempAccount
            wiimu_pass = tempPass

            configPlist = biplist.readPlist(configPlistPath)
            configPlist['wiimuaccount'] = wiimu_account
            configPlist['wiimupass'] = wiimu_pass
            biplist.writePlist(configPlist, configPlistPath)
            print 'Login success! Enjoy!'
        else:
            print 'Wrong account or password, please enter again'

def parseTodoData():
    retArr = []

    response = os.popen('curl -u \'%s:%s\' https://sh.linkplay.com:8090/rest/api/content/%s?expand=body.storage,version -s' % (wiimu_account, wiimu_pass, todo_page_id)).read().strip()
    try:
        response = json.loads(response)
        if response.get('version') == None:
            return

        #versionNum = int(response.get('version').get('number'))
        #versionNum += 1
        #title = response.get('title')
        content = response.get('body').get('storage').get('value')
        rows = re.findall(r'<tr>.*?</tr>', content, re.S)
        for row in rows:
            cols = re.findall(r'<td.*?</td>', row, re.S)
            if len(cols) != 0:
                priority = re.search(r'(?<=>).*?(?=</td>)', cols[0], re.S).group()

                # 4 - finished
                if int(priority) != 4:
                    continue

                title = re.search(r'(?<=>).*?(?=</td>)', cols[1], re.S).group().strip()
                desc = re.search(r'(?<=>).*?(?=</td>)', cols[3], re.S).group().strip()
                title = title.replace('&nbsp;', '')
                desc = desc.replace('&nbsp;', '')
                title = re.sub(r'<.*?>', '', title)
                desc = re.sub(r'<.*?>', '', desc)
                retArr.append({'title': title, 'desc': desc})

    except Exception, e:
        print e

    return retArr

def modifyWeeklyPage(finishedJobs, weeklyPageId):
    jobsContent = ''
    for job in finishedJobs:
        jobsContent += '<li><span class=\"s1\">%s - %s</span></li>' % (job['title'], job['desc'])

    # last friday

    today = date.today()
    lastFriday = today + relativedelta(weekday=FR(-1))
    lastFriday = lastFriday.strftime("%Y-%m-%d") 

    insertContent = '<h1>%s</h1><p>本周完成</p><ol><li>定制 <ol>%s</ol></li></ol><p>下周计划</p><ol><li>Muzo</li><li>其他定制</li></ol>' % (lastFriday, jobsContent)

    response = os.popen('curl -u \'%s:%s\' https://sh.linkplay.com:8090/rest/api/content/%s?expand=body.storage,version -s' % (wiimu_account, wiimu_pass, weeklyPageId)).read().strip()
    try:
        response = json.loads(response)
        if response.get('version') == None:
            return

        versionNum = int(response.get('version').get('number'))
        versionNum += 1
        title = response.get('title')
        content = response.get('body').get('storage').get('value')
        content = insertContent + content

        content = content.replace('"', '\\"')
        re = os.popen('curl -u \'%s:%s\' -X PUT -H \'Content-Type: application/json\' -d\'{\"id\":\"%s\",\"type\":\"page\",\"title\":\"%s\",\"space\":{\"key\":\"IOS\"},\"body\":{\"storage\":{\"value\":\"%s\",\"representation\":\"storage\"}},\"version\":{\"number\":%d}}\' \'https://sh.linkplay.com:8090/rest/api/content/%s\' -s' % (wiimu_account, wiimu_pass, weeklyPageId, title, content, versionNum, weeklyPageId)).read().strip()
        os.system('open https://sh.linkplay.com:8090/pages/editpage.action?pageId=%s' % todo_page_id)
        os.system('open https://sh.linkplay.com:8090/pages/editpage.action?pageId=%s' % weeklyPageId)

    except Exception, e:
        print e

if __name__ == '__main__':
    weeklyPageId = ''

    # w - weekly page id
    opts, args = getopt.getopt(sys.argv[1:], 'w:s', '')
    for option, value in opts:
        if option == '-w':
            weeklyPageId = value
        elif option == '-s':
            SetupHelper.setup(os.path.realpath(__file__),
                              'alias t2w=\"python %s/%s\"' % (SetupHelper.scriptFolder, os.path.basename(__file__)),
                              'Use \'t2w + weeklyPageId\' to copy your todo finished items to weekly page.')
            sys.exit(0)

    getGerritAccountPass()
    finishedJob = parseTodoData()
    modifyWeeklyPage(finishedJob, weeklyPageId)
