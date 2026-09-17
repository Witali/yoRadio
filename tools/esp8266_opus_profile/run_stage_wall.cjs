#!/usr/bin/env node
// Read-only diagnostic sampling. Start a stream explicitly before running.
const http = require('node:http'), fs = require('node:fs'), path = require('node:path');
const {analyze} = require('../test_esp8266_audio_continuity.cjs');
const legacyNames = ['read', 'decode_exclusive', 'output', 'wait'];
const splitNames = ['read', 'decode_exclusive', 'output', 'post_decode_wait', 'input_wait'];
const delta = (a,b) => (a-b) >>> 0;
function summarize(samples, seconds = 25) {
  const continuity = analyze(samples.map(s => ({...s.health, host_ms:s.host_ms, error:s.error})), seconds);
  const result = {continuity, timing_kind:'wall time including preemption and DMA waits, NOT CPU utilization'};
  if (samples.length !== 2 || samples.some(s => s.error)) return {...result, profile_error:'missing samples'};
  const [a,b] = samples.map(s => s.profile);
  if (![a,b].every(p => p && Array.isArray(p.stages) &&
      ((p.profile_version === undefined && p.stages.length === 4) ||
       (p.profile_version === 2 && p.stages.length === 5)) && p.stages.every(s =>
    s.length === 4 && s.every(v => Number.isInteger(v) && v >= 0 && v <= 0xffffffff))))
    return {...result, profile_error:'invalid stages'};
  if (a.profile_version !== b.profile_version)
    return {...result, profile_error:'profile version mismatch'};
  const names = a.profile_version === 2 ? splitNames : legacyNames;
  if (a.generation !== b.generation || b.uptime_ms <= a.uptime_ms ||
      b.uptime_ms - a.uptime_ms >= 3600000 || samples.some(s => s.profile.generation !== s.health.generation))
    return {...result, profile_error:'generation/reset/interval mismatch'};
  const us = (b.uptime_ms - a.uptime_ms) * 1000;
  result.profile_board_ms = us / 1000;
  result.stages = names.map((name,i) => {
    const time = delta(b.stages[i][0],a.stages[i][0]), calls = delta(b.stages[i][2],a.stages[i][2]);
    return {name, wall_ms:time/1000, wall_percent:100*time/us, calls,
      mean_us:calls ? time/calls : 0, maximum_since_boot_us:b.stages[i][1],
      misses:delta(b.stages[i][3],a.stages[i][3])};
  });
  result.timing_valid = !result.stages.some(s => s.maximum_since_boot_us >= 0x80000000);
  if (!result.timing_valid) result.profile_error = 'implausible stage maximum; possible non-monotonic SDK clock; retain misses but do not qualify wall timings';
  result.unattributed_misses_approx = continuity.underruns - result.stages.reduce((n,s) => n+s.misses,0);
  result.note = 'Health and profile are successive requests, not an atomic combined snapshot. Maxima are since boot. All failures are retained.';
  return result;
}
function json(base, route, timeoutMs = 5000) {
  return new Promise((resolve,reject) => {
    const req = http.get(new URL(route, base), {agent:false, headers:{Connection:'close'}}, res => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', s => {body += s; if (body.length > 4096) req.destroy(Error('oversized response'));});
      res.on('error',reject);
      res.on('end', () => {try {if (res.statusCode !== 200) throw Error('HTTP '+res.statusCode); resolve(JSON.parse(body));}catch(e){reject(e);}});
    });
    const timeout = setTimeout(() => req.destroy(Error('request timeout '+route)), timeoutMs);
    req.on('close', () => clearTimeout(timeout)); req.on('error',reject);
  });
}
async function collectSample(read, started, now = () => performance.now()) {
  const begin = now(), row = {};
  try {
    row.health = await read('/api/native/audio');
    row.host_ms = now() - started;
    row.profile = await read('/api/native/audio?stages=1');
  } catch (e) {
    // A late profile response must not erase the already received health.
    // Retain the error too: incomplete samples still cannot qualify a run.
    row.error = e.message;
    row.host_ms ??= now() - started;
  }
  row.request_ms = now() - begin;
  return row;
}
async function main() {
  const args = process.argv.slice(2), opt = (key, d) => args.includes(key) ? args[args.indexOf(key)+1] : d;
  const base = opt('--base','http://192.168.100.6'), output = opt('--output','.build/opus-stage-wall.json');
  const seconds = Number(opt('--seconds','25'));
  const timeoutMs = Number(opt('--request-timeout-ms','5000'));
  if (!Number.isInteger(seconds) || seconds < 20 || seconds > 55) throw Error('--seconds must be 20..55');
  if (!Number.isInteger(timeoutMs) || timeoutMs < 1000 || timeoutMs > 15000) throw Error('--request-timeout-ms must be 1000..15000');
  const report = {date:new Date().toISOString(), base, seconds, request_timeout_ms:timeoutMs, samples:[]}, started = performance.now();
  for (let i=0; i<2; ++i) {
    report.samples.push(await collectSample(route => json(base,route,timeoutMs), started));
    console.log(JSON.stringify(report.samples.at(-1)));
    if (!i) await new Promise(r => setTimeout(r,(seconds+2)*1000));
  }
  report.result = summarize(report.samples,seconds);
  fs.mkdirSync(path.dirname(output),{recursive:true});
  fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report.result));
  process.exitCode = report.result.continuity.pass && !report.result.profile_error ? 0 : 1;
}
module.exports = {summarize, collectSample};
if (require.main === module) main().catch(e => {console.error(e);process.exitCode=1;});
