#!/bin/sh
LANG=en_US.UTF-8

SOURCEDIR=$(cd `dirname $0`; pwd)
TEMPDIR=~/WorkHelperTemp
HELPERDIR=~/ScriptHelper

echo 'Please input your rootpass: '
read -s ROOTPASS

mkdir $TEMPDIR
cd $TEMPDIR

echo '******************iterm***********************'
# iterm
if [ ! -d /Applications/iTerm.app ];then
    curl -o iterm.zip https://iterm2.com/downloads/stable/iTerm2-3_0_8.zip
    unzip iterm.zip
    cp -R iTerm.app /Applications/iTerm.app
    defaults write com.apple.dock persistent-apps -array-add '<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>/Applications/iTerm.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>'
    killall Dock
else
    echo 'iTerm already satisfied.'
fi

# zsh
if [ ! $SHELL == /bin/zsh ];then
    echo $ROOTPASS | sudo -S chsh -s /bin/zsh
fi

# oh my zsh
echo '******************oh my zsh***********************'
if [ ! -d ~/.oh-my-zsh ];then
    sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
else
    echo 'oh my zsh already satisified.'
fi

if [ ! -d $HELPERDIR ];then
    mkdir $HELPERDIR
fi

# z.sh
if [ ! -f $HELPERDIR/z.sh ];then
    cp $SOURCEDIR/z.sh $HELPERDIR/z.sh
fi

# .zshrc
if [ ! -f ~/.zshrc ];then
    cp -f $SOURCEDIR/.zshrc ~/.zshrc
    perl -i -pe 's|/Users/.*?(?=/)|'$HOME'|g' ~/.zshrc
fi

echo '******************brew***********************'
if [[ ! `zsh -c 'where brew'` =~ .*brew$ ]];then
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    brew install wget
else
    echo 'brew already satisified.'
fi

# python
echo '******************pip***********************'
if [[ ! `zsh -c 'where pip'` =~ .*pip$ ]];then
    curl -o pip.py https://bootstrap.pypa.io/get-pip.py
    python get-pip.py
    echo $ROOTPASS | sudo -S pip install -r $SOURCEDIR/python/require.txt
else
    echo 'pip already satisfied.'
fi

echo '******************helpers***********************'
pylist=`ls $SOURCEDIR/python/`
cd $SOURCEDIR/python/
for file in $pylist:
do
    if [[ -a $HELPERDIR/$file ]];then
        echo "$file exsits, skip."
        continue
    fi

    if [[ -d $file ]] || [[ ${file##*.} == 'py' ]];then
        python $file -s $ROOTPASS
    fi
done

# clean
rm -rf $TEMPDIR

echo '\xF0\x9f\x8d\xba  All Done. Have Fun!'
