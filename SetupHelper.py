#coding=utf-8

import sys, os, shutil
reload(sys)
sys.setdefaultencoding('utf-8')

import re

scriptFolder = os.path.expanduser('~/ScriptHelper')

def setup(scriptFile, command, helperText):
    fileName = os.path.basename(scriptFile)
    scriptPath = os.path.expanduser('%s/%s' % (scriptFolder, fileName))

    # copy to dest dir
    print 'Copy to command zone...'
    if not os.path.exists(scriptFolder):
        os.mkdir(scriptFolder)

    if os.path.exists(scriptPath):
        os.remove(scriptPath)

    # helper udpate
    if os.path.exists('%s/%s' % (scriptFolder, os.path.basename(__file__))):
        os.remove('%s/%s' % (scriptFolder, os.path.basename(__file__)))

    shutil.copyfile(os.path.realpath(__file__), '%s/%s' % (scriptFolder, os.path.basename(__file__)))
    shutil.copyfile(scriptFile, scriptPath)

    print 'Modify command record...'
    # see what shell in use
    confPath = ''
    shellCmd = ''
    shellRet = os.popen('echo $SHELL').read().strip()

    if shellRet.endswith('bash'):
        confPath = os.path.expanduser('~/.bash_profile')
        shellCmd = 'bash'
    elif shellRet.endswith('zsh'):
        confPath = os.path.expanduser('~/.zshrc')
        shellCmd = 'zsh'
    else:
        print 'Not support %s' % shellRet
        sys.exit(-1)

    if not os.path.exists(confPath):
        try:
            confFile = open(confPath, 'w')
            confFile.write('\n# %s\n%s\n' % (helperText, command))
        finally:
            confFile.close()
    else:
        try:
            confFile = open(confPath, 'r+')
            content = confFile.read()
            if not re.search(r'%s' % command, content, re.S):
                confFile.write('\n# %s\n%s\n' % (helperText, command))
        finally:
            confFile.close()

    #print 'Reload command record...\n**********************************************'
    #os.system('%s %s' % (shellCmd, confPath))

    if helperText:
        print '******************** Note ********************\n%s\n******************** Note ********************' % helperText

    print '\xF0\x9f\x8d\xba  Setup finished. Have fun!'
