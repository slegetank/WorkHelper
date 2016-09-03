#coding=utf-8

import sys, os, getopt, shutil
reload(sys)
sys.setdefaultencoding('utf-8')

import SetupHelper

if __name__ == '__main__':
    if not os.path.exists('%s/symbolicatecrash' % SetupHelper.scriptFolder):
        print 'First time locate symbolicatecrash cmd...'
        cmdPath = os.popen('find /Applications/Xcode.app -name symbolicatecrash').read().strip()
        if len(cmdPath) == 0:
            print 'Found no symbolicatecrash, please assure your XCode is installed correctly.'
        else:
            shutil.copyfile(cmdPath, '%s/symbolicatecrash' % SetupHelper.scriptFolder)
            os.system('chmod +x %s' % '%s/symbolicatecrash' % SetupHelper.scriptFolder)

    symbolFile = None
    opts, args = getopt.getopt(sys.argv[1:], 'si:', '')
    for option, value in opts:
        # i: input symbolFile
        if option == '-i':
            symbolFile = value
        elif option == '-s':
            SetupHelper.setup(os.path.realpath(__file__),
                              'alias dsym=\"python %s/%s -i\"' % (SetupHelper.scriptFolder, os.path.basename(__file__)),
                              'Use \'dsym + xxx\' to parse your crash log.')
            sys.exit(0)

    if symbolFile == None:
        print 'Found no dSYM file.'
        sys.exit(-1)

    appName = os.path.basename(symbolFile)[:-9]
    count = 0
    logDir = os.path.dirname(symbolFile)
    for logFile in os.listdir(logDir):
        if logFile.startswith(appName) and (logFile.endswith('.ips') or logFile.endswith('.crash')):
            count += 1
            os.system('%s/symbolicatecrash \'%s\' \'%s\' > \'%s/%s%d.log\'' % (SetupHelper.scriptFolder, os.path.join(logDir, logFile), symbolFile, logDir, appName, count))

    if count == 0:
        print 'Found no .crash or .ips, abort'
    else:
        print '--------------------------------\n\xF0\x9f\x8d\xba  Parse %d log files, have fun!' % count
