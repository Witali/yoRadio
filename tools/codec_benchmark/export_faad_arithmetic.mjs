// Export the retained measurements as one flat Excel/CSV table.
// Run with the bundled Node runtime. Link its node_modules into
// .build/faad-arithmetic-table/node_modules before running this builder.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const scratch = path.join(root, '.build/faad-arithmetic-table');
const require = createRequire(path.join(scratch, 'entry.js'));
const {Workbook, SpreadsheetFile} = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const evidence = path.join(root, 'tests/results/faad2-arithmetic-20261001');
const output = path.join(root, 'outputs/01a0a51b-5ba3-70a3-8fba-6f4113c001fe');
const source = JSON.parse(await fs.readFile(path.join(evidence, 'comparison.json'), 'utf8'));
const order = ['lc-22050-mono','lc-44100-stereo','lc-48000-stereo','he-44100-stereo',
 'he-48000-stereo','hev2-44100-stereo','abba64','groovesalad16','groovesalad32','groovesalad64','groovesalad128'];
const headers = ['Input', 'Scope', 'Output rate (Hz)', 'Channel layout', 'Max abs (LSB)',
 'RMS (LSB)', 'Mean signed (LSB)', 'Signal/diff (dB)', 'Abs > 2 (count)', 'Abs > 5 (count)',
 'Samples (count)', 'Different (count)', 'P95 abs (LSB)', 'P99 abs (LSB)', 'P99.9 abs (LSB)',
 'Input frames', 'PS frames', 'Passes', 'Repeat identical', 'Observation'];
function percentile(hist, fraction) {
 const pairs = Object.entries(hist).map(([k,v])=>[Number(k),v]).sort((a,b)=>a[0]-b[0]);
 const threshold = Math.ceil(pairs.reduce((sum,p)=>sum+p[1],0)*fraction);
 let n=0;
 for (const [error,count] of pairs) { n+=count; if (n>=threshold) return error; }
 throw Error('Empty histogram');
}
const notes = {
 'lc-22050-mono':'FAAD default upsamples low-rate LC',
 'he-44100-stereo':'Sustained SBR discrepancy', 'he-48000-stereo':'Sustained SBR discrepancy',
 'hev2-44100-stereo':'Sustained SBR/PS discrepancy', 'abba64':'Large transient at PS onset, frames 11–12',
 'groovesalad16':'Actual mono output, PS inactive',
};
const rows=[];
for (const name of order) {
 const r=source.rows.find(x=>x.input===name);
 if (!r) throw Error('Missing input '+name);
 const rates=[...new Set(r.output_layouts.map(x=>x[0]))];
 if(rates.length!==1) throw Error('Unexpected rate transition');
 const layout=r.output_layouts.map(x=>x[1]===1?'mono':'stereo').join(' to ');
 const measurements=[['All',r.total],...r.channels.map(c=>[c.channel===0?'L / mono':'R',c])];
 for(const [scope,m] of measurements) {
  rows.push([name,scope,rates[0],layout,m.maximum,m.rms_lsb,m.mean_error_lsb,m.signal_to_difference_db,
   m.over_two,m.over_five,m.samples,m.different,percentile(m.histogram,.95),percentile(m.histogram,.99),
   percentile(m.histogram,.999),r.runs.float.frames,r.runs.float.ps_frames,r.repeats,
   ['float','fixed'].every(mode=>Object.entries(r.runs[mode].repeat_hashes).every(([k,v])=>r.runs[mode][k]===v)),
   scope==='All'?(notes[name]??''):'' ]);
 }
}
const csvCell = v => typeof v==='string' ? '"'+v.replaceAll('"','""')+'"' : String(v);
await fs.writeFile(path.join(evidence,'summary.csv'), [headers,...rows].map(r=>r.map(csvCell).join(',')).join('\n')+'\n');
await fs.mkdir(output,{recursive:true});
const wb=Workbook.create();
const sheet=wb.worksheets.add('Float vs fixed');
sheet.showGridLines=false;
sheet.tabColor='#32445A';
const bottom=7+rows.length;
sheet.getRange(`A1:T${bottom}`).format.font={name:'Arial',size:10,color:'#182230'};
sheet.getRange(`A1:T${bottom}`).format.verticalAlignment='center';
sheet.getRange(`A7:T${bottom}`).format.rowHeight=24;
sheet.getRange('A2').values=[['FAAD2 float32 versus fixed-point']];
sheet.getRange('A2').format.font={name:'Arial',size:15,bold:true};
sheet.getRange('A2:T2').format.rowHeight=28;
sheet.getRange('A3').values=[['Signed 16-bit PCM. Fixed minus float. 11 inputs, 22 main decodes and 22 repeatability controls.']];
sheet.getRange('A4').values=[['Source: FAAD2 arithmetic comparison.json, 2026-10-01. Upstream revision '+source.source_revision+'.']];
sheet.getRange('A5').values=[['No history compression. Large differences are retained. Float/fixed differences are separate from packed-storage accuracy limits.']];
sheet.getRange('A3:T5').format.rowHeight=22;
sheet.getRange('A3:T4').format.font={name:'Arial',size:10,italic:true,color:'#526174'};
sheet.getRange('A6:T6').format.borders={bottom:{style:'thin',color:'#AEBAC8'}};
sheet.getRange('A7:T7').values=[headers];
sheet.getRange(`A8:T${bottom}`).values=rows;
const table=sheet.tables.add(`A7:T${bottom}`,true,'FaadArithmeticResults');
table.style='TableStyleMedium2';
sheet.getRange('A7:T7').format={fill:'#32445A',font:{name:'Arial',size:10,color:'#FFFFFF',bold:true},
 wrapText:true,horizontalAlignment:'center',verticalAlignment:'center',rowHeight:42};
sheet.getRange(`A8:T${bottom}`).format.horizontalAlignment='left';
sheet.getRange(`C8:C${bottom}`).format.horizontalAlignment='right';
sheet.getRange(`E8:R${bottom}`).format.horizontalAlignment='right';
sheet.getRange(`C8:C${bottom}`).setNumberFormat('#,##0');
sheet.getRange(`E8:E${bottom}`).setNumberFormat('#,##0');
sheet.getRange(`F8:G${bottom}`).setNumberFormat('0.000000');
sheet.getRange(`H8:H${bottom}`).setNumberFormat('0.00');
sheet.getRange(`I8:R${bottom}`).setNumberFormat('#,##0');
const widths=[215,85,112,130,104,116,116,118,116,116,126,126,108,108,110,102,96,82,110,330];
widths.forEach((width,c)=>sheet.getRangeByIndexes(0,c,bottom,1).format.columnWidthPx=width);
for(let i=0;i<rows.length;i++) if(rows[i][1]==='All') {
 sheet.getRange(`A${i+8}:T${i+8}`).format.borders={top:{style:'thin',color:'#B5C0CD'}};
 sheet.getRange(`A${i+8}:B${i+8}`).format.font.bold=true;
}
sheet.freezePanes.freezeRows(7);
sheet.freezePanes.freezeColumns(2);
wb.recalculate();
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',
 options:{useRegex:true,maxResults:20},summary:'Final error scan'});
await fs.writeFile(path.join(scratch,'verification.json'),JSON.stringify({rows:rows.length,errorScan:errors.ndjson},null,2));
// The workbook is a retained measurement export, with no editable model/formulas.
const delivered=sheet.getRange(`A8:T${bottom}`).values;
for(let r=0;r<rows.length;r++) for(let c=0;c<headers.length;c++) {
 if(delivered[r][c]!==rows[r][c]) throw Error(`Value mismatch ${r},${c}`);
}
for(const [label,range] of [['left',`A1:J${bottom}`],['right',`K7:T${bottom}`]]) {
 const image=await wb.render({sheetName:sheet.name,range,scale:1,format:'png'});
 await fs.writeFile(path.join(scratch,label+'.png'),new Uint8Array(await image.arrayBuffer()));
}
const xlsx=await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(path.join(output,'faad-float-fixed.xlsx'));
console.log(JSON.stringify({rows:rows.length,columns:headers.length,xlsx:path.join(output,'faad-float-fixed.xlsx')}));
