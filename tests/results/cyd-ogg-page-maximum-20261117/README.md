# CYD Opus at the large-page boundaries

Two test streams derive from the same 48 kHz stereo Opus signal. Each
produces the original PCM under FFmpeg with libopus. The 65,307-byte
OpusTags page has 255 full laces and ends its continued comment packet on
the following page. The 65,306-byte audio page completes one packet and
starts a second padded packet of 61,255 bytes. An audio page of 65,307
bytes has no terminating lace and would carry at least 65,025 bytes of
one packet. The Family 0 policy allows up to 61,440 bytes per packet.
[Ogg page structure](https://www.rfc-editor.org/rfc/rfc3533.html#section-6) · [Ogg Opus packet size policy](https://www.rfc-editor.org/rfc/rfc7845.html#section-6)

The previous packet-mode image accepted the full audio page but failed a
61,440-byte allocation to copy the partially assembled padded packet, after
648 PCM frames. The comment-page control failed the 26,504-byte stereo
decoder allocation with zero PCM while the comment storage was still
resident. Both controls used verified radio TLS and HTTPS WebUI.

The packet reader now removes Code 3 padding when it has to copy a Family 0
packet. It accounts for all original bytes in the packet limit and receives
only CRC-verified pages. The audio frame bytes and timing survive the copy.
The comment parser retires acknowledged large pages before creating
the decoder. Queued PCM and audio page ownership still follow the same
generation and end-of-link rules.
[Opus padding syntax](https://www.rfc-editor.org/rfc/rfc6716.html#section-3.2.5)

Both replays use the same PDM image and the same two TLS sessions with
`CONFIG_YORADIO_OGG_OPUS_RAW=y`. Each receives the complete response in
16 KiB TLS records and a tail, recovers the single induced Mbed TLS
allocation failure by releasing one idle input slot, and emits 528,000 PCM
frames matching the original Espressif digest. The same HTTPS connection
serves the WebUI script after EOF. No guest fault occurs.

The sanitizer tests cover copied and split padded packets, allocation
refusal and retry, an oversized encoded packet, and the established
Family 1 packet and playback cases.

[Measurements](observed.json) · [Reproduction](../../target/cyd_full_app_openeth_qemu/README.md#radio-tls-and-https-webui-under-pressure)
