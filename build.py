#!/usr/bin/env python3
import hashlib
import io
import json
import urllib.request
from pathlib import Path


def httpget(*args, **kwargs):
    return urllib.request.urlopen(urllib.request.Request(*args, **kwargs)).read()


def get_url_sha512(url):
    sha512 = hashlib.sha512()
    sha512.update(httpget(url, headers={'Accept': 'application/octet-stream'}))
    return {
        'url': url,
        'sha512': sha512.hexdigest()
    }


def get_url_sha512_size(url):
    data = httpget(url, headers={'Accept': 'application/octet-stream'})
    sha512 = hashlib.sha512()
    sha512.update(data)
    return {
        'url': url,
        'sha512': sha512.hexdigest(),
        'size': len(data)
    }


def get_git_with_tag(url, tag):
    stream = io.TextIOWrapper(urllib.request.urlopen(url + '/info/refs?service=git-upload-pack'))
    refs = {}
    while True:
        line = stream.readline()
        line = line[4:]
        if line == '':
            break
        if line.startswith('#'):
            continue
        line = line.split('\0')[0]
        line = line.split(' ')
        refs[line[1].strip()] = line[0]
    return {
        'type': 'git',
        'url': url,
        'tag': tag,
        'commit': refs.get('refs/tags/' + tag + '^{}', refs.get('refs/tags/' + tag))
    }


def main():
    releases = json.loads(httpget('https://vscode-update.azurewebsites.net/api/releases/stable', headers={'X-API-Version': '2'}).decode())
    base = json.loads(httpget('https://github.com/flathub/io.atom.electron.BaseApp/raw/master/io.atom.electron.BaseApp.json').decode())

    recipe = {
        'app-id': 'com.visualstudio.code',
        'branch': 'stable',
        'base': base['id'],
        'base-version': base['branch'],
        'runtime': base['sdk'],
        'runtime-version': base['runtime-version'],
        'sdk': base['sdk'],
        'command': 'code',
        'tags': ['proprietary'],
        'separate-locales': False,
        'finish-args': [
            '--share=ipc',
            '--socket=x11',
            '--socket=pulseaudio',
            '--share=network',
            '--device=dri',
            '--filesystem=host',
            '--talk-name=org.freedesktop.Notifications',
            '--talk-name=org.freedesktop.secrets',
            '--env=NPM_CONFIG_GLOBALCONFIG=/app/etc/npmrc'
        ],
        'modules': [
            {
                'name': 'libsecret',
                'config-opts': [
                    '--disable-manpages',
                    '--disable-gtk-doc',
                    '--disable-static',
                    '--disable-introspection'
                ],
                'cleanup': [
                    '/bin',
                    '/include',
                    '/lib/pkgconfig',
                    '/share/gtk-doc',
                    '*.la'
                ],
                'sources': [
                    get_git_with_tag('https://git.gnome.org/browse/libsecret.git', '0.18.5')
                ]
            },
            {
                'name': 'xkbfile',
                'cleanup': ['/include', '/lib/*.la', '/lib/pkgconfig'],
                'config-opts': ['--disable-static'],
                'sources': [
                    get_git_with_tag('https://anongit.freedesktop.org/git/xorg/lib/libxkbfile.git', 'libxkbfile-1.0.9')
                ]
            },
            {
                'name': 'nodejs',
                'cleanup': [
                    '/include',
                    '/share',
                    '/app/lib/node_modules/npm/changelogs',
                    '/app/lib/node_modules/npm/doc',
                    '/app/lib/node_modules/npm/html',
                    '/app/lib/node_modules/npm/man',
                    '/app/lib/node_modules/npm/scripts'
                ],
                'sources': [
                    {
                        'type': 'archive',
                        **get_url_sha512('https://nodejs.org/dist/v7.9.0/node-v7.9.0.tar.xz')
                    }
                ]
            },
            {
                'name': 'vscode',
                'buildsystem': 'simple',
                'build-commands': [
                    'install -Dm755 apply_extra /app/bin/apply_extra',
                    'install -Dm755 code.sh /app/bin/code',
                    'install -Dm644 com.visualstudio.code-64.png /app/share/icons/hicolor/64x64/apps/com.visualstudio.code.png',
                    'install -Dm644 com.visualstudio.code-128.png /app/share/icons/hicolor/128x128/apps/com.visualstudio.code.png',
                    'install -Dm644 com.visualstudio.code-256.png /app/share/icons/hicolor/256x256/apps/com.visualstudio.code.png',
                    'install -Dm644 com.visualstudio.code-512.png /app/share/icons/hicolor/512x512/apps/com.visualstudio.code.png',
                    'install -Dm644 com.visualstudio.code.appdata.xml /app/share/appdata/com.visualstudio.code.appdata.xml',
                    'install -Dm644 code.desktop /app/share/applications/com.visualstudio.code.desktop',
                    'install -Dm644 npmrc /app/etc/npmrc'
                ],
                'cleanup': [
                    '/share/lintian',
                    '/share/pixmaps'
                ],
                'sources': [
                    {
                        'type': 'script',
                        'dest-filename': 'apply_extra',
                        'commands': [
                            'tar -xf code.tar.gz',
                            'rm -f code.tar.gz',
                            'mv VSCode-linux-* vscode',
                            'install -Dm644 /app/share/applications/com.visualstudio.code.desktop export/share/applications/com.visualstudio.code.desktop'
                        ]
                    },
                    {
                        'type': 'script',
                        'commands': ['exec env PATH="$PATH:$XDG_DATA_HOME/node_modules/bin" /app/extra/vscode/bin/code --extensions-dir=$XDG_DATA_HOME/vscode/extensions "$@"'],
                        'dest-filename': 'code.sh'
                    },
                    {
                        'type': 'file',
                        'path': 'npmrc'
                    },
                    {
                        'type': 'file',
                        'path': 'com.visualstudio.code.appdata.xml'
                    },
                    {
                        'type': 'file',
                        'path': 'code.desktop'
                    },
                    {
                        'type': 'file',
                        'path': 'com.visualstudio.code-512.png'
                    },
                    {
                        'type': 'file',
                        'path': 'com.visualstudio.code-256.png'
                    },
                    {
                        'type': 'file',
                        'path': 'com.visualstudio.code-128.png'
                    },
                    {
                        'type': 'file',
                        'path': 'com.visualstudio.code-64.png'
                    },
                    {
                        'type': 'extra-data',
                        'filename': 'code.tar.gz',
                        'only-arches': ['x86_64'],
                        **get_url_sha512_size('https://vscode-update.azurewebsites.net/' + releases[0]['version'] + '/linux-x64/stable')
                    },
                    {
                        'type': 'extra-data',
                        'filename': 'code.tar.gz',
                        'only-arches': ['i386'],
                        **get_url_sha512_size('https://vscode-update.azurewebsites.net/' + releases[0]['version'] + '/linux-ia32/stable')
                    }
                ]
            }
        ]
    }
    Path(recipe['app-id'] + '.json').write_text(json.dumps(recipe, indent=2) + '\n')


if __name__ == '__main__':
    main()
