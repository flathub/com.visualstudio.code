#!/usr/bin/sh
set -e

bsdtar -Oxf code.deb 'data.tar*' |
  bsdtar -xf - \
    --strip-components=4 ./usr/share/code
rm code.deb

cp /app/bin/stub_sandbox chrome-sandbox
