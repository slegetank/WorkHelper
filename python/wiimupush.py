#coding=utf-8

import sys, os, json, getopt, re
reload(sys)
sys.setdefaultencoding('utf-8')

import requests
import biplist
import SetupHelper
import time

configPlistPath = '%s/.wiimuconfig.plist' % os.path.expanduser('~')
global git_account
global git_pass
global wiimu_account
global wiimu_pass
global gerrit_currentuser_id
global usernameDic
global dest_branch
usernameDic = {}

confluence_page_id = '7209080'

# 通过id获取用户名
def getUsernameByID(identity):
    retName = usernameDic.get(identity)
    if retName != None:
        return retName

    response = requests.get("https://sh.linkplay.com:8010/a/accounts/%s" % identity, auth=requests.auth.HTTPDigestAuth(git_account, git_pass))
    jsonStr = response.text[4:]

    usernameDic[identity] = json.loads(jsonStr)['name']
    return usernameDic.get(identity)

def getGitProject():
    remoteUrl = os.popen('git config remote.origin.url').read().rstrip()

    if len(remoteUrl) == 0:
        printerr(u'remote.origin.url is empty')
        return

    appsIndex = remoteUrl.find('/apps/')
    if appsIndex == -1:
        printerr(u'git url illegal')
        return None

    return remoteUrl[appsIndex+6:]

def getGerritChanges():
    global git_account
    global git_pass
    global git_currentuser_id

    project = getGitProject()

    if project:
        print u'Checking gerrit clean or not...'

        warningArray = []

        response = requests.get("https://sh.linkplay.com:8010/a/changes/?q=status:open+project:apps/%s" % project, auth=requests.auth.HTTPDigestAuth(git_account, git_pass))
        jsonStr = response.text[4:]

        for submit in json.loads(jsonStr):
            if dest_branch == submit['branch']:
                if gerrit_currentuser_id == submit['owner']['_account_id']:
                    continue
                else:
                    warningArray.append(submit)

        if len(warningArray) == 0:
            print u'Gerrit is clean, pushing...'
            ret = os.system('git push origin HEAD:refs/for/%s' % dest_branch)

            # muzoplayer的主分支需要记录
            if ret == 0 and os.popen('basename `git rev-parse --show-toplevel`').read().strip() == 'ios_muzoplayer' and dest_branch == 'master':
                modifyVersionRecordWeb(dest_branch)
        else:
            printerr(u'Some guy is faster!')
            for submit in warningArray:
                printerr('%s -- %s: %s' % (submit['created'], getUsernameByID(submit['owner']['_account_id']), submit['subject']))
            print u'Push action termited, please contact administrator'

def modifyVersionRecordWeb(branch):
    print 'Try to modify record web page...'
    response = os.popen('curl -u \'%s:%s\' https://sh.linkplay.com:8090/rest/api/content/%s?expand=body.storage,version -s' % (wiimu_account, wiimu_pass, confluence_page_id)).read().strip()
    try:
        response = json.loads(response)
        if response.get('version') == None:
            return

        versionNum = int(response.get('version').get('number'))
        versionNum += 1
        title = response.get('title')
        content = response.get('body').get('storage').get('value')
        if '</tbody></table>' in content:
            #get confluence user key, this api really hard to find...
            response = os.popen('curl -u \'%s:%s\' \'https://sh.linkplay.com:8090/rest/prototype/1/search/user.json?max-results=1&query=%s\' -s' % (wiimu_account, wiimu_pass, wiimu_account)).read().strip()
            response = json.loads(response)
            if response.get('result') == None:
                return

            confluenceUserKey = response['result'][0]['userKey']

            # get all commits
            allCommitMsg = os.popen('git log %s --not --remotes --oneline' % branch).read().strip()
            for line in allCommitMsg.split('\n'):
                insertIndex = content.rindex('</tbody></table>')
                commitId = line[:7]
                commitMsg = line[8:]

                # get gerrit change number
                response = requests.get('https://sh.linkplay.com:8010/a/changes/?q=commit:%s' % commitId, auth=requests.auth.HTTPDigestAuth(git_account, git_pass))
                if response.status_code != 200:
                    continue

                # gerrit bug fix
                retStr = response.text[4:]
                gerritNum = json.loads(retStr)[0]['_number']

                # date
                formatTime = time.strftime("%Y.%m.%d", time.localtime())

                content = content[:insertIndex]+'<tr><td colspan=\"1\">%s</td><td colspan=\"1\"><a href=\"https://sh.linkplay.com:8010/#/c/%s/\">%s</a></td><td colspan=\"1\"><ac:link><ri:user ri:userkey=\"%s\" /></ac:link></td><td colspan=\"1\"><div class=\"com-google-gerrit-client-change-CommitBox_BinderImpl_GenCss_style-collapsed\"><div class=\"com-google-gerrit-client-change-CommitBox_BinderImpl_GenCss_style-scroll\"><div class=\"com-google-gerrit-client-change-CommitBox_BinderImpl_GenCss_style-text\">%s</div></div></div></td><td colspan=\"1\">无</td><td colspan=\"1\">无</td><td colspan=\"1\"> </td></tr>' % (formatTime, gerritNum, gerritNum, confluenceUserKey, commitMsg)+content[insertIndex:]

            # 更新web页面
            content = content.replace('"', '\\"')
            re = os.popen('curl -u \'%s:%s\' -X PUT -H \'Content-Type: application/json\' -d\'{\"id\":\"%s\",\"type\":\"page\",\"title\":\"%s\",\"space\":{\"key\":\"IOS\"},\"body\":{\"storage\":{\"value\":\"%s\",\"representation\":\"storage\"}},\"version\":{\"number\":%d}}\' \'https://sh.linkplay.com:8090/rest/api/content/%s\' -s' % (wiimu_account, wiimu_pass, confluence_page_id, title, content, versionNum, confluence_page_id)).read().strip()
            os.system('open https://sh.linkplay.com:8090/pages/editpage.action?pageId=%s' % confluence_page_id)

    except Exception, e:
        print e

def getCurrentBranch():
    branchStr = os.popen('git branch').read().rstrip()
    branchArray = branchStr.split('\n')

    for branch in branchArray:
        if branch.startswith('*'):
            return branch[2:]

def getCurrentUserIdentity():
    global git_account
    global gerrit_currentuser_id

    configPlist = biplist.readPlist(configPlistPath)
    gerrit_currentuser_id = configPlist.get('gerrit_identity')

    if gerrit_currentuser_id != None:
        return

    response = requests.get("https://sh.linkplay.com:8010/a/accounts/?q=%s" % git_account, auth=requests.auth.HTTPDigestAuth(git_account, git_pass))
    jsonStr = response.text[4:]

    gerrit_currentuser_id = json.loads(jsonStr)[0]['_account_id']
    configPlist['gerrit_identity'] = gerrit_currentuser_id
    biplist.writePlist(configPlist, configPlistPath)

# 获取当前目录的git账户、密码
def getAccountAndPass():
    global git_account
    global git_pass

    email = os.popen('git config user.email').read().rstrip()

    atIndex = email.find('@')
    git_account = email[:atIndex]

    if os.path.exists(configPlistPath):
        configPlist = biplist.readPlist(configPlistPath)
        git_pass = configPlist['gitpass']
    else:
        git_pass = raw_input('Current git account is: %s\nYou can get your password here: https://sh.linkplay.com:8010/#/settings/http-password \nPlease enter:' % git_account)
        f = file(configPlistPath, 'w')
        f.close()

        configPlist = {'gitpass':git_pass}
        biplist.writePlist(configPlist, configPlistPath)

    getCurrentUserIdentity()

def checkIfCurrentDirectoryIsGit():
    if os.system('git rev-parse') == 0:
        return True
    else:
        return False

def checkIfNeedRebase():
    os.system('git fetch')
    aheadBehind = os.popen('git rev-list --left-right --count origin/%s...%s' % (dest_branch, getCurrentBranch())).read()
    if aheadBehind.startswith('0') == False:
        return True

    return False

def printerr(errMessage):
    print '\033[31m%s\033[0m' % errMessage

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

if __name__ == '__main__':
    global dest_branch

    forcePush = False
    dest_branch = None

    opts, args = getopt.getopt(sys.argv[1:], 'fb:s', '')
    for option, value in opts:
        if option == '-f':
            forcePush = True
        elif option == '-b':
            dest_branch = value
        elif option == '-s':
            SetupHelper.setup(os.path.realpath(__file__),
                              'alias wpush=\"python %s/%s\"' % (SetupHelper.scriptFolder, os.path.basename(__file__)),
                              'Use \'wpush\' to push your code to gerrit.')
            sys.exit(0)

    if checkIfCurrentDirectoryIsGit() == False:
        printerr('Current dir is not under git control.')
        sys.exit()

    if dest_branch == None:
        dest_branch = getCurrentBranch()

    if forcePush == True:
        print 'force pushing...'
        os.system('git push origin HEAD:refs/for/%s' % dest_branch)
        sys.exit()
    else:
        if checkIfNeedRebase():
            printerr(u'Your code is old! Rebase!')
            sys.exit()

        getGerritAccountPass()
        getAccountAndPass()
        getGerritChanges()
