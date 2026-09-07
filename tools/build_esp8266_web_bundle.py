"""Build a compressed native-player bootstrap from the shared WebUI sources.

No playlist/settings/credentials are embedded. A runtime content fingerprint
must match SPIFFS before firmware may serve this acceleration. Default source
assets remain authoritative; a custom upload invalidates the bundle.
"""
import argparse
import gzip
import json
from pathlib import Path
import re

FILES = ('theme.css', 'style.css', 'script.js', 'dragpl.js',
         'player.html', 'logo.svg', 'options.html')


def fnv(data):
    result = 2166136261
    for value in data:
        result = ((result ^ value) * 16777619) & 0xffffffff
    return result


def build(root):
    web = root / 'yoRadio/data/www'
    compressed = {name: (web / (name + '.gz')).read_bytes() for name in FILES}
    assets = {name: gzip.decompress(data).decode('utf-8')
              for name, data in compressed.items()}
    if 'function fetchUiResource(' not in assets['script.js']:
        raise ValueError('Shared WebUI lacks preloaded-fragment support')
    header = (root / 'yoRadio/src/core/netserver.h').read_text(encoding='utf-8')
    section = header.split('const char index_html[] PROGMEM = ', 1)[1]
    section = section.split('const char emergency_form', 1)[0]
    chunks = re.findall(r'R"\((.*?)\)"', section, re.S)
    if len(chunks) != 4:
        raise ValueError('Shared index shell structure changed')
    head, n = re.subn(r'<script>\s*const bootToken =.*?</script>', '',
                      chunks[0], flags=re.S)
    if n != 1:
        raise ValueError('Shared boot variables anchor changed')
    revision = '%08x' % fnv(b''.join(compressed.values()))
    variables = ("var yoVersion='esp8266-native',webUiRevision='%s',"
                 "formAction='',playMode='player',equalizerEnabled=false,"
                 "nativeFirmwareOnly=true;" % revision)
    preloaded = json.dumps({name: assets[name] for name in ('player.html','logo.svg')},
                          ensure_ascii=True, separators=(',', ':')).replace('<', r'\u003c')
    variables += 'window.yoUiAssets=' + preloaded + ';'
    variables += ("history.replaceState(null,'',location.pathname+'?ui='+webUiRevision);")
    def script(text):
        return '<script>' + re.sub(r'</script', r'<\\/script', text, flags=re.I) + '</script>'
    css = assets['theme.css'] + '\n' + assets['style.css']
    if '</style' in css.lower():
        raise ValueError('Unsafe inline stylesheet terminator')
    html = (head + '<style>' + css + '</style>' + script(variables) +
            script(assets['script.js']) + script(assets['dragpl.js']) + chunks[-1])
    return gzip.compress(html.encode('utf-8'), compresslevel=9, mtime=0), compressed, revision


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--html-gzip', type=Path)
    args = parser.parse_args()
    data, originals, revision = build(args.root)
    lines = ['/* Generated from shared WebUI; do not edit. */', '#pragma once',
             '#include <stdint.h>',
             'static const unsigned char web_bundle_gzip[] __attribute__((aligned(4))) = {']
    for offset in range(0, len(data), 24):
        lines.append('  ' + ','.join('0x%02x' % value for value in data[offset:offset+24]) + ',')
    lines += ['};', 'static const struct { const char *path; uint32_t hash; } web_bundle_files[] = {']
    for name, original in originals.items():
        lines.append('  {"/spiffs/www/%s.gz", 0x%08xU},' % (name, fnv(original)))
    lines += ['};', '#define WEB_BUNDLE_REVISION "%s"' % revision]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    if args.html_gzip:
        args.html_gzip.write_bytes(data)
    print('Shared player bundle: %d gzip bytes, revision %s' % (len(data), revision))


if __name__ == '__main__':
    main()
