# ESP8266 physical test corpus through192 kbps

The user selected lower-rate testing, not a runtime codec bitrate limit.
Use12/24/64/128/192kbps for new physical measurements. The prior510kbps
fixture and archived runs remain unchanged for historical reproduction.

`stereo-192` is the same locally synthesized997/10007Hz left,1703Hz right
and seed7349 white-noise signal as the original corpus:1.2s,48kHz,stereo,
20ms CELT, FFmpeg libopus CBR192k. No recorded radio/music.
The manifest references the original four lower-rate packet files and
contains the hashes and generation command for the new192kbps fixture.

```powershell
node tools/esp8266_opus_profile/generate_192_corpus.cjs
node tools/esp8266_opus_profile/build_board_fixtures.cjs --corpus tests/fixtures/opus_native/through192 --output-dir .build/esp8266-opus-board-through192
node --test tests/esp8266-opus-through192.test.js
```

Build with `-OpusBenchmarkFixtures .build/esp8266-opus-board-through192`.
Observe with `run_board.cjs --fixtures .build/esp8266-opus-board-through192`
or `run_repeated_board.ps1 -Fixtures .build/esp8266-opus-board-through192`.
This checks hashes/sample counts returned by the board and uses the correct
fixture labels instead of the legacy510 label for the fifth case.

The generated board header/manifest hashes are recorded in each firmware
manifest. Do not compare images using different corpora as an optimization A/B.
