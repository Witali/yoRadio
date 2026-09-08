#!/usr/bin/env node
// Explicitly combine interrupted/restarted campaigns without overwriting IDs
// or constructing pairs across a reset. Original captures remain authoritative.
const fs = require('node:fs');
const {readLog} = require('./summarize_mp3_matrix.cjs');
const {summarize} = require('./summarize_network.cjs');
const {analyze} = require('./summarize_network_sweep.cjs');

function combine(logs, minimum = 10) {
  if (!logs.length) throw Error('At least one capture is required');
  const lines = [], runs = [];
  let nextId = 0;
  for (const [epoch, log] of logs.entries()) {
    const raw = summarize(log);
    if (raw.starts !== 1) throw Error('Split captures at reboot boundaries before combining');
    const ids = new Map();
    for (const row of raw.cases.filter(c => c.path)) ids.set(row.case, nextId++);
    runs.push({epoch,declared_cases:raw.cases.length,attempted:ids.size,
      ended:raw.complete,all_declared_finished:raw.complete && raw.cases.every(c =>
        c.error !== undefined || c.open !== undefined || c.allocation_failed)});
    if (epoch) lines.push(`net_bench: recovery begin campaign_restart=${epoch}`);
    for (const line of log.split(/\r?\n/)) {
      if (!line.includes('net_bench:') && !line.includes('net_cpu:')) continue;
      if (line.includes('net_bench: begin ') || line.includes('net_bench: complete')) continue;
      lines.push(line.replace(/\bcase=(-?\d+)/g, (_, id) => {
        const n = Number(id);
        if (n < 0) return `case=${-epoch-1}`;
        if (!ids.has(n)) throw Error(`Result without begin: epoch ${epoch}, case ${n}`);
        return `case=${ids.get(n)}`;
      }));
    }
  }
  const lastFinished = runs.at(-1).all_declared_finished;
  const merged = `net_bench: begin cases=${nextId}\n` + lines.join('\n') +
    (lastFinished ? '\nnet_bench: complete\n' : '\n');
  return {...analyze(merged,minimum),runs};
}
module.exports = {combine};
if (require.main === module) {
  const [destination,...files] = process.argv.slice(2);
  if (!destination || !files.length) throw Error('Usage: summarize_network_campaign.cjs report.json capture1.log [capture2.log ...]');
  const report = combine(files.map(readLog));
  report.captures = files;
  fs.writeFileSync(destination,JSON.stringify(report,null,2)+'\n');
  console.log(`Attempts ${report.finished}/${report.declared_cases}, complete=${report.complete}`);
  console.table(report.groups.map(g=>({fixture:g.fixture,variant:g.variant,
    attempts:g.attempts,ok:g.complete_windows,failed:g.failed,
    reader:g.reader_percent_complete.median?.toFixed(2),
    busy:g.non_idle_percent_complete.median?.toFixed(2),
    kbps:g.rx_kbps_complete.median?.toFixed(1)})));
  if (!report.complete) process.exitCode=1;
}
