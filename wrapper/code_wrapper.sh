#!/bin/bash

unset LD_PRELOAD
if [ ! -z $ELECTRON_RUN_AS_NODE ]; then
	exec /app/extra/vscode/code "$@"
else
	echo "use zypak-wrapper"
	exec /app/bin/zypak-wrapper.sh /app/extra/vscode/code "$@"
fi
