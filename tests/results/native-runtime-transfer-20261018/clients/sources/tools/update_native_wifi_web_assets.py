"""Embed the maintained native Wi-Fi editor into the shared legacy gzip asset."""
import gzip
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / 'yoRadio/data/www/script.js.gz'
EDITOR = ROOT / 'tools/web/native_wifi_editor.js'
BEGIN = '/* BEGIN NATIVE WIFI EDITOR: tools/web/native_wifi_editor.js */'
END = '/* END NATIVE WIFI EDITOR */'


def once(text, before, after):
    if after in text:
        return text
    if text.count(before) != 1:
        raise RuntimeError('Asset replacement anchor is not unique: ' + before)
    return text.replace(before, after)


def main():
    # Only a tracked public WebUI asset is decompressed. Never read data/wifi.csv.
    source = gzip.decompress(ASSET.read_bytes()).decode('utf-8').replace('\r\n', '\n')
    if BEGIN in source:
        start = source.index(BEGIN)
        end = source.index(END, start) + len(END)
        source = source[:start] + source[end:].lstrip('\n')
    editor = EDITOR.read_text(encoding='utf-8').replace('\r\n', '\n').rstrip() + '\n'
    source = once(source, 'function handleWiFiData(fileData) {', editor + 'function handleWiFiData(fileData) {')
    source = once(source, 'function handleWiFiData(fileData) {\n',
                  'function handleWiFiData(fileData) {\n  if (nativeWiFiMode()) return;\n')
    source = once(source, 'function getWiFi(path){\n',
                  'function getWiFi(path){\n  if (nativeWiFiMode()) return getNativeWiFi();\n')
    source = once(source, 'function submitWiFi(){\n',
                  'function submitWiFi(){\n  if (nativeWiFiMode()) return submitNativeWiFi();\n')
    source = once(source,
        'case "wifiexport": window.open(`http://${hostname}/data/wifi.csv`+"?"+new Date().getTime()); break;',
        'case "wifiexport": if (nativeWiFiMode()) exportNativeWiFi(); else window.open(`http://${hostname}/data/wifi.csv`+"?"+new Date().getTime()); break;')
    ASSET.write_bytes(gzip.compress(source.encode('utf-8'), compresslevel=9, mtime=0))
    print('Updated native Wi-Fi metadata/keep/set editor; legacy branch retained')


if __name__ == '__main__':
    main()
