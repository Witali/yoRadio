# Small TV device profile

[`small-tv-c2.json`](small-tv-c2.json) is the profile owned by this firmware
project. It uses QEMU schema 1: the existing SPI2 ST7789 wiring and display
properties, plus explicit station/setup SSIDs, the three firmware NTP names
and its HTTP weather endpoint. No owner credentials or API keys are included.

The shared compiler and migration rules are documented in
`QEMU-ESP32/configs/boards/README.md`. QEMU needs the generic `service-hosts`,
`ntp-hosts` and `station-ssid` properties introduced in `f4322a8a8f`; rebuild
its executable before using the updated launcher. Source changes alone are
insufficient.

From the yoRadio repository root:

```powershell
& .\Small_TV\qemu\run.ps1 -Firmware reconstructed -Network clock -Display none
& .\Small_TV\qemu\run.ps1 -Firmware original -Network setup -HttpBasePort 18080 -Persistent
& .\Small_TV\qemu\run.ps1 -Action status -Firmware original -Network setup
& .\Small_TV\qemu\run.ps1 -Action stop -Firmware original -Network setup
```

`run.ps1` passes this exact profile to the QEMU launcher. `-QemuRoot` selects
its source/tools checkout, `-QemuExecutable` selects an alternate built binary,
and `-StateDirectory` selects a disposable/persistent working flash directory.
The default state is `.build/small-tv-vm/<network>-<firmware>` in yoRadio.
Changing saved SSID or firmware requires a new state directory. Source dumps
and archived firmware images are read-only.

`clock` seeds the open station network and exposes its real HTTP handlers on
localhost. `setup` reserves separate consecutive AP/STA ports and follows the
firmware's own configure/save/reboot sequence. `offline` creates no NIC or
network services; adding network metadata to a profile does not enable them.

For a local HTTP fixture use `-ServicePort 19000`. The fixture must listen on
`127.0.0.1:19000` and handle the original Host/path/query. `-ServiceUrl` optionally
overrides the list for that run. An address is assigned per hostname; distinct
ports produce separate SLIRP forwards. Port 0 disables HTTP service aliases.
The list controls reachability and does not rewrite firmware requests or act
as an HTTP path filter. HTTPS requires compatible fixture TLS/certificates.

The guest firmware still chooses its endpoints. For the immutable factory
image, keep the factory NTP and weather names. Changing profile URLs cannot
change a URL compiled into the application. Weather response parsing remains
specific to the Small TV protocol, while the QEMU forwarding uses generic
`ServicePort` and `network.urls`.

The full firmware tests and five-scene comparison use this same profile.
`tests/profile_test.py` also checks production GPIO definitions, unchanged
hardware-only/offline behavior, explicit NTP/SSID configuration, generic
service routing, multiple host/port/path overrides and query metadata removal.
Publication binds the exact profile, launcher/comparison and compiler hashes
to the actual full-firmware test result.
