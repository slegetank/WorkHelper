#coding=utf-8

import sys, os, shutil, getopt
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import SetupHelper
import wcmdUI

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], 's', '')
    for option, value in opts:
        if option == '-s':
            SetupHelper.setup(os.path.realpath(__file__),
                              'alias wc=\"python %s/%s\"' % (SetupHelper.scriptFolder, os.path.basename(os.path.dirname(__file__))),
                              'Use \'wc\' to start.')
            sys.exit(0)

    wcmdUI.main()
