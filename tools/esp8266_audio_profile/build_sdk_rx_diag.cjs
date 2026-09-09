#!/usr/bin/env node
'use strict';

// Diagnostic-only, fail-closed source overlay. Never edits the installed SDK.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');
const normalize = value => value.toString('utf8').replace(/\r\n/g, '\n');
const marker = ' /* sdk-rx-diag */';
const call = (indent, text) => `${indent}${text}${marker}\n`;
const include = anchor => ({anchor, replacement: anchor + call('', '#include "sdk_rx_diag.h"')});
const specs = [
  {
    source: 'components/tcpip_adapter/tcpip_adapter_lwip.c',
    output: 'tcpip_adapter_lwip.c', component: 'tcpip_adapter',
    sha256: 'b0eb5eb0f65d6656ced48da5f1725191e0d1f1c831ba646fe19486e76ad4c9f5',
    patches: [
      include('#include "tcpip_adapter.h"\n'),
      {
        anchor: '    struct tcpip_adapter_pbuf *pa = (struct tcpip_adapter_pbuf *)p;\n',
        replacement: '    struct tcpip_adapter_pbuf *pa = (struct tcpip_adapter_pbuf *)p;\n' +
          call('    ', 'sdk_rx_diag_custom_release();'),
      },
      {
        anchor: '    ethernetif_input(netif, pbuf);\n',
        replacement: call('    ', 'sdk_rx_diag_custom_acquire();') + '    ethernetif_input(netif, pbuf);\n',
      },
      {
        anchor: 'no_mem:\n    return -ENOMEM;',
        replacement: 'no_mem:\n' + call('    ', 'sdk_rx_diag_count(SDK_RX_DIAG_CUSTOM_FAIL);') + '    return -ENOMEM;',
      },
    ],
  },
  {
    source: 'components/lwip/lwip/src/api/tcpip.c', output: 'tcpip.c', component: 'lwip',
    sha256: '96cb16299ec7b720ee117df81281167b3d8c14f4822eaf721866b81de8fcfa6a',
    patches: [
      include('#include "lwip/priv/tcpip_priv.h"\n'),
      {
        anchor: '  msg = (struct tcpip_msg *)memp_malloc(MEMP_TCPIP_MSG_INPKT);\n  if (msg == NULL) {\n',
        replacement: '  msg = (struct tcpip_msg *)memp_malloc(MEMP_TCPIP_MSG_INPKT);\n  if (msg == NULL) {\n' +
          call('    ', 'sdk_rx_diag_count(SDK_RX_DIAG_ENQUEUE_NOMEM);'),
      },
      {
        anchor: '  if (sys_mbox_trypost(&tcpip_mbox, msg) != ERR_OK) {\n    memp_free(MEMP_TCPIP_MSG_INPKT, msg);\n',
        replacement: '  if (sys_mbox_trypost(&tcpip_mbox, msg) != ERR_OK) {\n' +
          call('    ', 'sdk_rx_diag_count(SDK_RX_DIAG_ENQUEUE_FULL);') + '    memp_free(MEMP_TCPIP_MSG_INPKT, msg);\n',
      },
    ],
  },
  {
    source: 'components/lwip/port/esp8266/netif/wlanif.c', output: 'wlanif.c', component: 'lwip',
    sha256: '6854117ffdd58914386abbf15d68f81fac0564504116803946648402f6a53893',
    patches: [
      include('#include "esp_aio.h"\n'),
      {
        anchor: '    if (!p) {\n        LWIP_DEBUGF(NETIF_DEBUG, ("low_level_output: lack memory\\n"));\n',
        replacement: '    if (!p) {\n' + call('        ', 'sdk_rx_diag_count(SDK_RX_DIAG_TX_TRANSFORM_FAIL);') +
          '        LWIP_DEBUGF(NETIF_DEBUG, ("low_level_output: lack memory\\n"));\n',
      },
      {
        anchor: '    err = ieee80211_output_pbuf(&aio);\n    if (err != ERR_OK) {\n',
        replacement: '    err = ieee80211_output_pbuf(&aio);\n    if (err != ERR_OK) {\n' +
          call('        ', 'sdk_rx_diag_count(SDK_RX_DIAG_TX_DRIVER_FAIL);'),
      },
    ],
  },
];

function patchSource(source, spec) {
  let output = source;
  for (const {anchor, replacement} of spec.patches) {
    const first = output.indexOf(anchor);
    if (first < 0 || output.indexOf(anchor, first + 1) >= 0)
      throw new Error(`${spec.source}: expected exactly one overlay anchor: ${JSON.stringify(anchor)}`);
    output = output.slice(0, first) + replacement + output.slice(first + anchor.length);
  }
  // Removing only inserted lines must recover every original SDK byte after
  // newline normalization, including every return value and ownership action.
  const stripped = output.split('\n').filter(line => !line.endsWith(marker)).join('\n');
  if (stripped !== source) throw new Error(`${spec.source}: overlay changed original SDK text`);
  return output;
}

function inside(parent, child) {
  const relative = path.relative(parent, child);
  return relative === '' || (!relative.startsWith('..' + path.sep) && relative !== '..' && !path.isAbsolute(relative));
}

// Resolve symlink/junction ancestors even when the output directory is new.
function resolvedDestination(destination) {
  if (fs.existsSync(destination)) return fs.realpathSync(destination);
  return path.join(resolvedDestination(path.dirname(destination)), path.basename(destination));
}

function generate(sdkDirectory, outputDirectory) {
  const sdk = fs.realpathSync(sdkDirectory);
  const out = resolvedDestination(path.resolve(outputDirectory));
  if (inside(sdk, out)) throw new Error('Overlay output must be outside the installed SDK');
  const prepared = specs.map(spec => {
    const original = fs.readFileSync(path.join(sdk, spec.source));
    const normalized = normalize(original);
    const actual = sha256(normalized);
    if (actual !== spec.sha256)
      throw new Error(`${spec.source}: SDK SHA-256 mismatch; expected ${spec.sha256}, got ${actual}`);
    const text = patchSource(normalized, spec);
    return {spec, text, originalSha256: sha256(original)};
  });
  // Validate all pins/anchors/destinations before producing any output. Never
  // follow an output-file symlink back into the SDK (or any unrelated file).
  for (const name of [...specs.map(spec => spec.output), 'manifest.json']) {
    const filename = path.join(out, name);
    const entry = fs.lstatSync(filename, {throwIfNoEntry: false});
    if (entry && (!entry.isFile() || entry.nlink !== 1))
      throw new Error(`Overlay output is not an unlinked regular file: ${filename}`);
  }
  const manifest = {
    format: 1, diagnostic: 'YORADIO_ESP8266_SDK_RX_DIAG', counterBytes: 32,
    normalization: 'CRLF to LF only',
    files: prepared.map(({spec, text, originalSha256}) => ({
      source: spec.source, output: spec.output, component: spec.component,
      originalSha256, normalizedSha256: spec.sha256, outputSha256: sha256(text),
      insertions: spec.patches.length,
    })),
  };
  fs.mkdirSync(out, {recursive: true});
  for (const {spec, text} of prepared) fs.writeFileSync(path.join(out, spec.output), text);
  fs.writeFileSync(path.join(out, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  return manifest;
}

if (require.main === module) {
  try {
    const args = process.argv.slice(2);
    if (args.length !== 4 || args[0] !== '--sdk' || args[2] !== '--out')
      throw new Error('Usage: node build_sdk_rx_diag.cjs --sdk SDK_DIRECTORY --out BUILD_OVERLAY_DIRECTORY');
    generate(args[1], args[3]);
    process.stdout.write(`SDK RX diagnostic overlay: ${path.resolve(args[3], 'manifest.json')}\n`);
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  }
}

module.exports = {generate, patchSource, specs, normalize, sha256};
