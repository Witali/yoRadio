// Package the complete measured operand stream, without reordering/subsampling.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash}=require('./export.cjs');
function generate(){
 const dir=path.join(root,'.build/opus-bands-division-census');
 const report=JSON.parse(fs.readFileSync(path.join(dir,'census.json')));
 const data=fs.readFileSync(path.join(dir,'operands.bin'));
 assert.equal(hash(data),report.payload_sha256);assert.equal(data.length,report.payload_bytes);
 assert.equal(report.cases.length,5);assert.equal(data.length%8,0);
 let cursor=0;for(const r of report.cases){assert.equal(r.first_pair,cursor);cursor+=r.calls;}
 assert.equal(cursor,data.length/8);
 const lines=['/* Generated complete host census; uint32 numerator/divisor pairs. */',
  '#pragma once','#include <stdint.h>','#define OPUS_DIVISION_PAIR_COUNT '+cursor,
  'typedef struct { uint32_t first, count; } opus_division_fixture_t;',
  'static const opus_division_fixture_t opus_division_fixtures[] = {',
  ...report.cases.map(r=>' {'+r.first_pair+'U,'+r.calls+'U},'),'};',
  'static const uint32_t opus_division_pairs[] __attribute__((aligned(4))) = {'];
 for(let i=0;i<data.length;i+=32){const row=[];for(let j=i;j<Math.min(i+32,data.length);j+=4)row.push(data.readUInt32LE(j)+'U');lines.push(' '+row.join(',')+',');}
 lines.push('};','');const file=path.join(dir,'opus_division_fixtures.h');
 fs.writeFileSync(file,lines.join('\n'));console.log(JSON.stringify({file,bytes:data.length,sha256:hash(fs.readFileSync(file))}));return file;
}
module.exports={generate};if(require.main===module)generate();
