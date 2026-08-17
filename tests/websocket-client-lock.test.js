const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const source = fs.readFileSync(
  path.join(__dirname, '..', 'yoRadio', 'src', 'AsyncWebServer', 'AsyncWebSocket.cpp'),
  'utf8',
);

function functionBody(signature, nextSignature) {
  const start = source.indexOf(signature);
  const end = source.indexOf(nextSignature, start + signature.length);
  assert.notEqual(start, -1, `${signature} must exist`);
  assert.notEqual(end, -1, `${nextSignature} must follow ${signature}`);
  return source.slice(start, end);
}

test('WebSocket client additions are serialized', () => {
  const body = functionBody(
    'void AsyncWebSocket::_addClient',
    'void AsyncWebSocket::_handleDisconnect',
  );
  assert.match(body, /AsyncWebLockGuard\s+l\(_lock\)/);
});

test('broadcast snapshots clients without holding the lock while sending', () => {
  const body = functionBody(
    'void AsyncWebSocket::textAll(AsyncWebSocketMessageBuffer * buffer)',
    'void AsyncWebSocket::textAll(const char * message, size_t len)',
  );
  assert.match(body, /AsyncWebLockGuard\s+l\(_lock\)/);
  assert.match(body, /clients\[clientCount\+\+\]\s*=\s*c/);
  assert.match(body, /clients\[i\]->text\(buffer\)/);
  const lockEnd = body.indexOf('\n  }\n  buffer->lock()');
  const send = body.indexOf('clients[i]->text(buffer)');
  assert.ok(lockEnd > 0 && send > lockEnd, 'send must happen after releasing the list lock');
});

test('disconnected WebSocket clients are deleted by deferred cleanup', () => {
  const disconnect = functionBody(
    'void AsyncWebSocketClient::_onDisconnect',
    'void AsyncWebSocketClient::_onData',
  );
  assert.match(disconnect, /_status\s*=\s*WS_DISCONNECTED/);
  assert.match(disconnect, /_disconnectedClient\s*=\s*client/);

  const cleanup = functionBody(
    'void AsyncWebSocket::cleanupClients',
    'void AsyncWebSocket::ping',
  );
  assert.match(cleanup, /remove_first/);
  assert.match(cleanup, /c->status\(\)\s*==\s*WS_DISCONNECTED/);
});
