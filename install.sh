#!/bin/bash

cd `dirname $0`
SOURCE_ROOT=`pwd`
EXEC_CMD="${SOURCE_ROOT}/handytask"

INSTALL_ROOT=~/.local/share
ICON_PATH=${INSTALL_ROOT}/icons/taskwarrior.png
DESKTOP_PATH=${INSTALL_ROOT}/applications/handytask.desktop

if [ "$GI_TYPELIB_PATH" ] ; then
  EXEC_CMD="$EXEC_CMD \"$GI_TYPELIB_PATH\""
else
  EXEC_CMD="$EXEC_CMD \"\""
fi

#pip3 install --user -r requirements.txt

#install -D images/taskwarrior.png $ICON_PATH

cat handytask.desktop.template | \
  sed "s#%%exec_cmd%%#$EXEC_CMD#g" | \
  sed "s#%%icon_path%%#$ICON_PATH#g" | \
  sed "s#%%working_directory%%#$SOURCE_ROOT#g" | \
  cat > $DESKTOP_PATH

