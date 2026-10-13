/* Compile each embedded script without executing page code or browser I/O. */
import {readFileSync} from 'node:fs';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import vm from 'node:vm';

const root = path.dirname(fileURLToPath(import.meta.url));
let count = 0;
const results = [];
for (const page of ['setup', 'settings', 'photo']) {
    const html = readFileSync(path.join(root, 'pages', `${page}.html`), 'utf8');
    const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)];
    if (!scripts.length) throw new Error(`No embedded scripts: ${page}`);
    for (const [index, script] of scripts.entries()) {
        new vm.Script(script[1], {filename:`${page}.html:script-${index + 1}`});
        count++;
    }
    results.push({page, scripts:scripts.length,
        sha256:crypto.createHash('sha256').update(html).digest('hex')});
}
// Execute only the DOM-independent metadata routine against synthetic headers.
// A real Canvas JPEG regression is supplied separately by the browser evidence.
const cleaner = readFileSync(path.join(root,'jpeg_metadata.js'),'utf8');
const cropScript = readFileSync(path.join(root,'photo_crop.js'),'utf8');
const scope = vm.createContext({Blob,Uint8Array});
new vm.Script(cleaner + '\nthis.clean = stripCanvasJpegMetadata;').runInContext(scope);
new vm.Script(cropScript + '\nthis.crop = squareCropBounds; this.resize = resizeSquareCrop;').runInContext(scope);
const segment = (marker, data) => Uint8Array.from([255,marker,(data.length+2)>>8,(data.length+2)&255,...data]);
const scan = [255,0xda,0,8,1,1,0,0,63,0,11,255,0,77,255,0xd9];
const table = [...segment(0xdb,[0,11,22,33])];
const fixture = new Blob([Uint8Array.from([255,0xd8]),segment(0xe0,[74,70,73,70,0]),
    segment(0xe1,[69,120,105,102,0,0,99]),segment(0xe2,[73,67,67,95,80,82,79,70,73,76,69,0]),
    segment(0xfe,[115,121,110,116,104]),Uint8Array.from(table),Uint8Array.from(scan)]);
const cleaned = new Uint8Array(await (await scope.clean(fixture)).arrayBuffer());
const expected = Uint8Array.from([255,0xd8,...table,...scan]);
if (Buffer.compare(Buffer.from(cleaned),Buffer.from(expected))) throw new Error('JPEG pixels/scan changed or metadata retained');
for (const bad of [[1,2,3,4], [255,0xd8,255,0xe2,255,255,255,0xd9], [255,0xd8,255,0xd9]]) {
    let rejected=false;
    try { await scope.clean(new Blob([Uint8Array.from(bad)])); } catch { rejected=true; }
    if (!rejected) throw new Error('Malformed JPEG accepted by metadata filter');
}
// Cover both orientations, both edges, zoom limits and tiny decoded images.
let cropChecks = 0;
for (const [w,h,z,x,y,expected] of [
    [960,640,1,50,50,[160,0,640]], [960,640,1,100,50,[320,0,640]],
    [640,960,1,50,0,[0,0,640]], [640,960,2,50,100,[160,640,320]],
    [240,240,4,100,0,[180,0,60]], [1,1,1,50,50,[0,0,1]]]) {
    const actual = scope.crop(w,h,z,x,y);
    if (JSON.stringify([actual.x,actual.y,actual.size]) !== JSON.stringify(expected))
        throw new Error('Wrong selected source coordinates');
    cropChecks++;
}
for (const [w,h] of [[960,640],[640,960],[240,240],[1,1]]) {
    for (const zoom of [1,1.05,2,4]) for (const x of [0,50,100]) for (const y of [0,50,100]) {
        const crop = scope.crop(w,h,zoom,x,y);
        if (crop.x < 0 || crop.y < 0 || crop.size <= 0 ||
            crop.x + crop.size > w + 1e-8 || crop.y + crop.size > h + 1e-8)
            throw new Error('Selection leaves the source image');
        cropChecks++;
    }
}
for (const args of [[0,240,1,50,50], [240,NaN,1,50,50], [240,240,.5,50,50],
    [240,240,5,50,50], [240,240,1,-1,50], [240,240,1,50,101]]) {
    let rejected = false;
    try { scope.crop(...args); } catch { rejected = true; }
    if (!rejected) throw new Error('Invalid crop accepted');
    cropChecks++;
}
const report = {passed:true,scripts:count,pages:results,metadata_checks:4,crop_checks:cropChecks,
    cleaner_sha256:crypto.createHash('sha256').update(cleaner).digest('hex'),
    crop_sha256:crypto.createHash('sha256').update(cropScript).digest('hex')};
let resizeChecks = 0;
for (const corner of ['nw','ne','sw','se']) {
    const sx = corner.endsWith('e') ? 1 : -1, sy = corner.startsWith('s') ? 1 : -1;
    const start = {x:320,y:160,size:320};
    for (const amount of [-10000,-80,0,80,10000]) {
        const result = scope.resize(start,960,640,corner,sx*amount,sy*amount);
        if (result.x < 0 || result.y < 0 || result.x+result.size > 960 ||
            result.y+result.size > 640 || result.size < 160 || result.size > 640)
            throw new Error('Resized square leaves the image or zoom range');
        const anchor = c => [sx>0 ? c.x : c.x+c.size, sy>0 ? c.y : c.y+c.size];
        if (JSON.stringify(anchor(start)) !== JSON.stringify(anchor(result)))
            throw new Error('Opposite resize corner moved');
        if (amount===-80 && result.size!==240) throw new Error('Corner shrink failed');
        if (amount===80 && result.size!==400) throw new Error('Corner enlargement failed');
        resizeChecks++;
    }
}
for (const args of [[{x:0,y:0,size:240},240,240,'bad',1,1],
    [{x:-1,y:0,size:240},240,240,'se',1,1],
    [{x:0,y:0,size:240},240,240,'se',NaN,1]]) {
    let rejected=false; try {scope.resize(...args);} catch {rejected=true;}
    if (!rejected) throw new Error('Invalid corner resize accepted');
    resizeChecks++;
}
report.resize_checks = resizeChecks;
console.log(process.argv.includes('--json') ? JSON.stringify(report) :
    `PASS JavaScript syntax: ${count} scripts; metadata: 4; crop: ${cropChecks}; corner resize: ${resizeChecks} checks`);
