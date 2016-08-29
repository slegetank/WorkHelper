#coding=utf-8

import sys, os, json, getopt
reload(sys)
sys.setdefaultencoding('utf-8')
import subprocess

import re
import SetupHelper

def getLibTargets(projectFilePath):
    retArr = []

    projectFilePath = os.path.join(projectFilePath, 'project.pbxproj')
    projectFile = open(projectFilePath, 'r')
    content = projectFile.read()
    projectFile.close()

    pbproj_to_json_cmd = ['plutil', '-convert', 'json', '-o', '-', projectFilePath]
    json_str = subprocess.check_output(pbproj_to_json_cmd)
    jsonObj = json.loads(json_str)
    rootUid = jsonObj['rootObject']
    objsJson = jsonObj['objects']
    rootJson = objsJson[rootUid]

    for targetUid in rootJson['targets']:
        productReference = objsJson[targetUid]['productReference']
        targetName = objsJson[targetUid]['name']
        product = re.search(r'(?<=%s /\* ).*?(?= \*/,)' % productReference, content)
        if product:
            productName = product.group()
            if productName.endswith('.a'):
                retArr.append({'target':targetName, 'product':productName})

    return retArr

def generateLib(projectPath, targetName, productName):
    BUILD_DIR = os.path.join(projectPath, 'build')
    OUTPUT_DIR = os.path.expanduser('~/Desktop')

    os.chdir(projectPath)
    os.system('xcodebuild clean -configuration Release')
    os.system('xcodebuild -target %s ONLY_ACTIVE_ARCH=NO -configuration Release -sdk iphoneos BUILD_DIR=\"%s\"' % (targetName, BUILD_DIR))
    os.system('xcodebuild -target %s ONLY_ACTIVE_ARCH=NO -configuration Release -sdk iphonesimulator BUILD_DIR=\"%s\"' % (targetName, BUILD_DIR))
    os.system('lipo -create -output \"%s/%s\" \"%s/Release-iphoneos/%s\" \"%s/Release-iphonesimulator/%s\"' % (OUTPUT_DIR, productName, BUILD_DIR, productName, BUILD_DIR, productName))
    os.system('lipo -info \"%s/%s\"' % (OUTPUT_DIR, productName))
    os.system('rm -rf %s' % BUILD_DIR)
    os.system('open %s' % OUTPUT_DIR)
    print '\xF0\x9f\x8d\xba  Cmd execution finished. Have fun.'

if __name__ == '__main__':
    projectFile = None

    # s - setup
    # x - xcodeproj
    opts, args = getopt.getopt(sys.argv[1:], 'sx:', '')
    for option, value in opts:
        if option == '-s':
            SetupHelper.setup(os.path.realpath(__file__),
                              'alias wlipo=\"python %s/%s -x\"' % (SetupHelper.scriptFolder, os.path.basename(__file__)),
                              'Use \'wlipo + xcodeproj\' to make fat .a')
            sys.exit(0)
        elif option == '-x':
            projectFilePath = value
            if not projectFilePath.endswith('xcodeproj'):
                print 'Not a valid xcodeproj file. Abort.'
                sys.exit(-1)

            targets = getLibTargets(projectFilePath)
            if len(targets) == 0:
                print 'Found no lib target. Abort.'
                sys.exit(0)
            elif len(targets) == 1:
                generateLib('%s/../' % projectFilePath, targets[0]['target'], targets[0]['product'])
            else:
                print 'Found multi targets:\n'
                for i in range(len(targets)):
                    targetName = targets[i]['target']
                    print '%d %s' % (i, targetName)

                choice = raw_input('which do you want to build?')
                if int(choice) < len(targets):
                    target = targets[int(choice)]
                    generateLib('%s/../' % projectFilePath, target['target'], target['product'])
