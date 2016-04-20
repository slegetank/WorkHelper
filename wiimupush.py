#coding=utf-8

import sys, os, json, getopt
reload(sys)
sys.setdefaultencoding('utf-8')

import requests
import biplist

configPlistPath = '%s/.wiimuconfig.plist' % os.path.expanduser('~')
global git_account
global git_pass
global gerrit_currentuser_id
global usernameDic
global dest_branch
usernameDic = {}

# 通过id获取用户名
def getUsernameByID(identity):
    retName = usernameDic.get(identity)
    if retName != None:
        return retName

    response = requests.get("https://sh.wiimu.com:8010/a/accounts/%s" % identity, auth=requests.auth.HTTPDigestAuth(git_account, git_pass))
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

        response = requests.get("https://sh.wiimu.com:8010/a/changes/?q=status:open+project:apps/%s" % project, auth=requests.auth.HTTPDigestAuth(git_account, git_pass))
        jsonStr = response.text[4:]

        for submit in json.loads(jsonStr):
            if dest_branch == submit['branch']:
                if gerrit_currentuser_id == submit['owner']['_account_id']:
                    continue
                else:
                    warningArray.append(submit)

        if len(warningArray) == 0:
            print u'Gerrit is clean, pushing...'
            os.system('git push origin HEAD:refs/for/%s' % dest_branch)
        else:
            printerr(u'Some guy is faster!')
            for submit in warningArray:
                printerr('%s -- %s: %s' % (submit['created'], getUsernameByID(submit['owner']['_account_id']), submit['subject']))
            print u'Push action termited, please contact administrator'

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

    response = requests.get("https://sh.wiimu.com:8010/a/accounts/?q=%s" % git_account, auth=requests.auth.HTTPDigestAuth(git_account, git_pass))
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
        git_pass = raw_input('Current git account is: %s\nYou can get your password here: https://sh.wiimu.com:8010/#/settings/http-password \nPlease enter:' % git_account)
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

if __name__ == '__main__':
    global dest_branch

    if checkIfCurrentDirectoryIsGit() == False:
        printerr('Current dir is not under git control.')
        sys.exit()

    forcePush = False
    dest_branch = None

    opts, args = getopt.getopt(sys.argv[1:], 'fb:', '')
    for option, value in opts:
        if option == '-f':
            forcePush = True
        elif option == '-b':
            dest_branch = value

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

        getAccountAndPass()
        getGerritChanges()
