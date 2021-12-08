#!/bin/bash

set -e
shopt -s nullglob

FIRST_RUN="${XDG_CONFIG_HOME}/flatpak-vscode-first-run"

if [ ! -f ${FIRST_RUN} ]; then
  WARNING_FILE="/app/share/vscode/flatpak-warning.txt"
  touch ${FIRST_RUN}
fi


VSCODE_PATH="/app/extra/vscode"

ELECTRON="$VSCODE_PATH/code"
CLI="$VSCODE_PATH/resources/app/out/cli.js"

export CHROME_WRAPPER="/app/bin/code-wrapper"
#export ZYPAK_DISABLE_SANDBOX=1

exec env ELECTRON_RUN_AS_NODE=1 /app/bin/zypak-wrapper  "$ELECTRON" "$CLI" \
  --ms-enable-electron-run-as-node --extensions-dir=${XDG_DATA_HOME}/vscode/extensions \
  "$@" ${WARNING_FILE}
