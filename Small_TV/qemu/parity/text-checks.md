# Text encoding and field checks

The immutable factory text loop at `0x4200abee` treats high bytes as pairs.
Its helper at `0x4200aae0` maps an unrecognized pair to the Celsius bitmap.
Consequently UTF-8 Cyrillic and Chinese labels become repeated Celsius symbols.
The historical [observation](text-encoding-observation.json) records the
pre-fix reconstructed image and retains its original identities.

The reconstructed scalar decoder follows [RFC 3629](https://www.rfc-editor.org/rfc/rfc3629.html):
one to four bytes, no overlong encoding, surrogate or value beyond U+10FFFF.
Invalid input consumes one byte and produces a replacement. The renderer uses
`?` when a scalar has no glyph. Exact legacy A1E6/A848 tokens and Unicode
℃/℉/°C/°F keep the recovered unit bitmaps. Factory ASCII remains unchanged.
The bundled BSD-2-Clause Spleen BDF supplies 452 additional scalars, scaled to
16/24/32-pixel cells; this does not provide every language, shaping or bidi.

The original weather callback at `0x4200fccc` retains 15 bytes of each label,
which can split a scalar. The corrected copy keeps the same byte budget and
stops before a valid scalar would cross it. Width, centering, field clipping
and requested scrolling share the same token boundaries.

The original weather fetch at `0x42010864` inserts raw city bytes in the URL.
The call at `0x42010988` passes the initialization result directly to
`esp_http_client_perform`. A real UTF-8 city POST reproduces a NULL-client
Load access fault: MEPC `0x4203e8f0`, caller `0x4201098c`, address `0xc`.
The native fetch percent-encodes UTF-8 bytes, using the explicit ASCII
unreserved set from [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986.html), and
checks initialization. Locale cannot change the escaping rules.

`tests/text_oracle.py` executes both actual RV32 programs. The native oracle
uses independently read raw BDF and factory bitmap files for every glyph in
all three sizes, whole retained panels, transparent/bounded/scrolled windows,
scalar boundaries, malformed sequences and prefix/guard cases. Factory
ASCII/unit equality and intentional Unicode corrections are separate checks.

`tests/text_qemu.py` executes the complete applications with real loopback
HTTP. It sends browser-style UTF-8 JSON, splits a multibyte weather character
between server writes, reads the actual cache without modification, and checks
native fields and guard strips pixel by pixel. Cyrillic, accented Latin,
unsupported CJK/emoji, both 15-byte boundaries and a full scrolling cycle are
mandatory. The expected factory city crash uses a separate disposable VM;
factory weather-cache checks use ASCII locations to stay on a healthy path.
Only fault addresses and synthetic data are published, without UART stacks,
credentials or full flash copies. Every owned VM/listener closes on exit.

The full runner requires `machine_text` and `qemu.text_http`. Publication binds
their app/source/ELF/font/emulator hashes and rejects missing required cases.
When another task changes the QEMU checkout, an optional immutable committed
HTTP-client overlay can be used without switching its branch. Its distinct
Python module and recorded SHA avoid silently reusing an imported older helper.
Emulator, board profile and canonical helper hashes must remain unchanged
throughout the suite. A passing result covers these cases, not complete factory
parity, physical operation or universal Unicode support.
