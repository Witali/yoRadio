"""Exact complete mono/stereo WAV/framemd5 reader; no qualifier startup."""
import hashlib
import io
import re
import wave

def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def decoded_pcm(wav, md5_text, rate, channels, frames, modes):
    with wave.open(io.BytesIO(wav), 'rb') as stream:
        need(stream.getcomptype() == 'NONE' and stream.getframerate() == rate and stream.getnchannels() == channels and
             stream.getsampwidth() == 2 and stream.getnframes() == sum(frames), 'Actual WAV metadata/frame count')
        pcm = stream.readframes(sum(frames) + 1)
    need(len(pcm) == sum(frames) * channels * 2, 'Complete WAV PCM required')
    text = md5_text.decode().replace('\r\n', '\n')
    need(re.search(r'^#tb 0: 1/' + str(rate) + '$', text, re.M) and
         re.search(r'^#sample_rate 0: ' + str(rate) + '$', text, re.M) and '#codec_id 0: pcm_s16le' in text,
         'Actual framemd5 metadata')
    rows = [line for line in text.splitlines() if line.strip() and not line.startswith('#')]
    need(len(rows) == len(frames) - 1 and frames[0] == 0, 'Exact nonprimer packet count')
    cursor = timestamp = 0
    transition_bytes, transition_channels = {}, {}
    for index, (line, count) in enumerate(zip(rows, frames[1:]), 1):
        fields = [item.strip() for item in line.split(',')]
        size = count * channels * 2
        need(len(fields) == 6 and [int(x) for x in fields[:5]] == [0, timestamp, timestamp, count, size],
             'Actual packet PTS/duration/PCM size')
        chunk = pcm[cursor:cursor + size]
        need(hashlib.md5(chunk).hexdigest() == fields[5], 'Actual packet MD5 differs from WAV PCM')
        kind = 'SL'[modes[index - 1]] + 'SL'[modes[index]]
        transition_bytes[kind] = transition_bytes.get(kind, 0) + sum(value != 0 for value in chunk)
        counts = transition_channels.setdefault(kind, [0] * channels)
        for channel in range(channels):
            counts[channel] += sum(chunk[pos:pos + 2] != b'\0\0' for pos in range(channel * 2, len(chunk), channels * 2))
        cursor += size
        timestamp += count
    need(cursor == len(pcm) and set(transition_bytes) == {'SS', 'SL', 'LS', 'LL'} and
         all(transition_bytes.values()) and all(all(values) for values in transition_channels.values()),
         'Every channel must be nonzero in every present transition')
    return pcm, dict(rate=rate, channels=channels, bits=16, frames=frames[1:], pcm_bytes=len(pcm),
        nonzero_bytes=sum(value != 0 for value in pcm), transition_nonzero_bytes=transition_bytes,
        transition_nonzero_frames_per_channel=transition_channels, wav_sha256=sha(wav), pcm_sha256=sha(pcm))

