# ESP8266 radio stream recovery

The radio socket uses nonblocking reads. EAGAIN/EWOULDBLOCK means no bytes
are available yet, not that TCP has failed. The audio task yields and retries;
it does not spin or allocate another stream buffer.

## Receive inactivity deadline

Build setting `CONFIG_YORADIO_STREAM_IDLE_TIMEOUT_MS` defaults to **1000 ms**
and accepts 250..60000 ms in menuconfig. Existing sdkconfig files retain their
explicit values. This setting does not shorten DNS, connection or header timeouts.

Each successful receive resets the deadline. Once it expires, the active
playback loop closes the old connection, supplies neutral PDM, reports
RECONNECTING, waits 250 ms and requests the same station again, provided that
the user has not stopped playback or selected a different station.
The decoder type is reused when appropriate; two failed connection attempts
result in CONNECTION ERROR rather than a false Playing indication.

A one-second deadline recovers sooner but can cause unnecessary reconnections
on bursty streams or weak Wi-Fi. In those conditions 3000..10000 ms may be a
better build setting. Reconnecting cannot eliminate packet loss or compensate
for an undersized audio buffer. ICY titles are not filtered or discarded.

The wrap-safe deadline arithmetic is executed by the host HTTP protocol tests.
Live measurements must distinguish missing network data from a stopped PCM
producer, DMA underruns and HTTP request latency.

## Validation

`/api/native/audio` exposes received bytes, completed PCM frames and DMA
progress without loading the playlist. Run the audio continuity test only
after playback has started, for at least 20 seconds. A decode-only build is
not proof of audio output and is rejected by the test. Digital counters do
not establish analog output quality or whether sound is audible.

After losing a previously acquired client connection, the existing application
poll also starts the recovery AP after the configured Wi-Fi recovery delay.
This uses no additional permanent task.
