from pathlib import Path
old=Path('.build/c3-mp3-long');dest=Path('.build/c3-production-radio-mp3-http')
text=(old/'review.py').read_text(encoding='utf-8').replace('esp32c3-idf-6.1-r9a97-quiet-http-txrelease','esp32c3-idf-6.1-r9a97-production-radio').replace("for transport in ('http','https'):","for transport in ('http',):")
(dest/'review.py').write_text(text,encoding='utf-8')
for name in ('freeze.py','verify_commit.py'):
    text=(old/name).read_text(encoding='utf-8').replace('tests/results/esp32c3-public-mp3-long','tests/results/esp32c3-production-radio-mp3-http')
    (dest/name).write_text(text,encoding='utf-8')
root=Path('.build/c3-production-radio-regression');old=Path('.build/c3-http-buffer-regression')
text=(old/'freeze.py').read_text(encoding='utf-8').replace('tests/results/esp32c3-http-buffer-regression','tests/results/esp32c3-production-radio-regression').replace("('review.json','vorbis-review.json')","('review.json',)")
(root/'freeze.py').write_text(text,encoding='utf-8')
text=(old/'verify_commit.py').read_text(encoding='utf-8').replace('tests/results/esp32c3-http-buffer-regression','tests/results/esp32c3-production-radio-regression')
(root/'verify_commit.py').write_text(text,encoding='utf-8')
print('Prepared separate replay/archive paths for production matrix and corrected HTTP control')
