/* Real Chrome controls, Canvas output and guest HTTP; only synthetic images. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';

const args=Object.fromEntries(process.argv.slice(2).reduce((out,value,index,all)=>
    index%2 ? out : [...out,[value.slice(2),all[index+1]]],[]));
const base=new URL(args.url);
assert(['127.0.0.1','localhost'].includes(base.hostname),'Only a disposable loopback guest is allowed');
const out=args.output;
await fs.mkdir(out,{recursive:true});
const {chromium}=createRequire(import.meta.url)(path.join(args.modules,'playwright'));
const digest=data=>crypto.createHash('sha256').update(data).digest('hex');
const report={passed:false,stage:args.stage,checks:[],requests:[],console:[],page_errors:[],
    script_sha256:digest(await fs.readFile(new URL(import.meta.url)))};
let browser;
/* Save each acceptance condition before failing the owned browser run. */
function check(name,condition,details={}) {
    report.checks.push({name,passed:Boolean(condition),...details});
    assert(condition,name);
}

/* Build legal JPEG metadata around synthetic Canvas pixels, never user data. */
function addMetadata(jpeg) {
    const author=Buffer.from('SYNTHETIC_PRIVATE_AUTHOR\0');
    const tiff=Buffer.alloc(26+author.length);
    tiff.write('II');tiff.writeUInt16LE(42,2);tiff.writeUInt32LE(8,4);
    tiff.writeUInt16LE(1,8);tiff.writeUInt16LE(0x13b,10);tiff.writeUInt16LE(2,12);
    tiff.writeUInt32LE(author.length,14);tiff.writeUInt32LE(26,18);author.copy(tiff,26);
    const segment=(marker,payload)=> {
        const header=Buffer.from([255,marker,0,0]);header.writeUInt16BE(payload.length+2,2);
        return Buffer.concat([header,payload]);
    };
    return Buffer.concat([jpeg.subarray(0,2),segment(0xe1,Buffer.concat([Buffer.from('Exif\0\0'),tiff])),
        segment(0xeb,Buffer.from('SYNTHETIC_GPS_DO_NOT_KEEP')),
        segment(0xfe,Buffer.from('SYNTHETIC_PRIVATE_COMMENT')),jpeg.subarray(2)]);
}

/* Inspect JPEG syntax without reusing the production metadata stripper. */
function inspectJpeg(bytes) {
    assert(bytes.readUInt16BE(0)===0xffd8 && bytes.readUInt16BE(bytes.length-2)===0xffd9);
    let position=2,frame,scan=false;
    const metadata=[];
    while(position+4<=bytes.length) {
        assert.equal(bytes[position],255);
        const marker=bytes[position+1],length=bytes.readUInt16BE(position+2);
        assert(length>=2 && position+2+length<=bytes.length);
        if(marker>=0xe0 && marker<=0xef || marker===0xfe)metadata.push(marker);
        if(marker===0xc0)frame={height:bytes.readUInt16BE(position+5),width:bytes.readUInt16BE(position+7)};
        if(marker===0xda){scan=true;break;}
        position+=2+length;
    }
    assert(scan && frame);
    return {metadata,...frame,bytes:bytes.length,sha256:digest(bytes)};
}

try {
    browser=await chromium.launch({executablePath:args.browser,headless:true});
    report.browser_version=browser.version();
    const context=await browser.newContext({viewport:{width:1280,height:900},serviceWorkers:'block'});
    await context.route('**/*',route=> {
        const url=new URL(route.request().url());
        return ['http:','https:'].includes(url.protocol) && url.origin!==base.origin ? route.abort() : route.continue();
    });
    const page=await context.newPage();
    page.setDefaultTimeout(30000);
    page.on('console',message=> {
        if(['error','warning'].includes(message.type()))report.console.push({type:message.type(),text:message.text()});
    });
    page.on('pageerror',error=>report.page_errors.push(String(error)));
    page.on('request',request=> {
        const url=new URL(request.url());
        if(['/start_upload','/upload_chunk','/finish_upload'].includes(url.pathname))
            report.requests.push({method:request.method(),path:url.pathname});
    });
    const response=await page.goto(new URL('/photo',base).href,{waitUntil:'domcontentloaded'});
    check('actual-guest-html',response.status()===200);
    report.served_html_sha256=digest(await response.body());
    await page.waitForFunction(()=>Array.from({length:5},(_,i)=>document.querySelector('#thumbnail'+(i+1)))
        .every(image=>image?.complete && image.naturalWidth===240));
    await page.waitForFunction(()=>document.querySelector('#loading-overlay').style.display==='none');
    check('five-decoded-previews',true);

    /* Reassemble the guest's public multipart download protocol exactly. */
    async function download(slot) {
        const info=await context.request.get(new URL(`/get_Photo_File?file=${slot}&chunk=0&size=0`,base).href);
        assert.equal(info.status(),200);
        const metadata=await info.json();assert(metadata.exists && metadata.size>0);
        const chunks=[];
        for(let n=0;n<Math.ceil(metadata.size/10240);n++) {
            const reply=await context.request.get(new URL(`/get_Photo_File?file=${slot}&chunk=${n}&size=10240`,base).href);
            assert.equal(reply.status(),200);chunks.push(await reply.body());
        }
        const bytes=Buffer.concat(chunks);assert.equal(bytes.length,metadata.size);return bytes;
    }
    /* Decode the actual HTTP JPEG with Chrome and inspect its complete RGB mean. */
    async function pixels(bytes) {
        return page.evaluate(async data=> {
            const image=new Image();image.src='data:image/jpeg;base64,'+data;await image.decode();
            const canvas=document.createElement('canvas');canvas.width=image.naturalWidth;canvas.height=image.naturalHeight;
            const c=canvas.getContext('2d');c.drawImage(image,0,0);
            const values=c.getImageData(0,0,canvas.width,canvas.height).data,mean=[0,0,0];
            for(let i=0;i<values.length;i+=4)for(let channel=0;channel<3;channel++)mean[channel]+=values[i+channel];
            return mean.map(value=>value/(canvas.width*canvas.height));
        },bytes.toString('base64'));
    }

    if(args.stage==='cold') {
        for(const slot of [4,5]) {
            const bytes=await download(slot),expected=await fs.readFile(path.join(out,`final-slot${slot}.jpg`));
            check(`cold-slot${slot}-exact`,bytes.equals(expected),{sha256:digest(bytes)});
        }
    } else {
        /* Construct inputs using native Canvas, then add explicit private tags. */
        /* Produce only deterministic colors/noise and explicit synthetic private tags. */
        async function fixture(kind) {
            const data=await page.evaluate(kind=> {
                const canvas=document.createElement('canvas');
                canvas.width=kind==='portrait'?360:kind==='noise'?240:640;
                canvas.height=kind==='portrait'?640:kind==='noise'?240:480;
                const c=canvas.getContext('2d');
                if(kind==='noise') {
                    const pixels=c.createImageData(240,240);let state=0x12345678;
                    for(let i=0;i<pixels.data.length;i+=4){for(let k=0;k<3;k++){state=(Math.imul(state,1664525)+1013904223)>>>0;pixels.data[i+k]=state>>>24;}pixels.data[i+3]=255;}
                    c.putImageData(pixels,0,0);
                } else {
                    c.fillStyle=kind==='portrait'?'#00ff00':'#ff0000';c.fillRect(0,0,canvas.width,canvas.height);
                    c.fillStyle=kind==='portrait'?'#ffff00':'#0000ff';
                    if(kind==='portrait')c.fillRect(0,320,360,320);else c.fillRect(320,0,320,480);
                }
                return canvas.toDataURL('image/jpeg',1).split(',')[1];
            },kind);
            const bytes=addMetadata(Buffer.from(data,'base64'));
            const info=inspectJpeg(bytes);
            check(kind+'-input-carries-private-metadata',[0xe1,0xeb,0xfe].every(marker=>info.metadata.includes(marker)));
            await fs.writeFile(path.join(out,`input-${kind}.jpg`),bytes);
            return {name:`synthetic-${kind}.jpg`,mimeType:'image/jpeg',buffer:bytes};
        }
        const landscape=await fixture('landscape'),portrait=await fixture('portrait'),noise=await fixture('noise');
        const before=await download(4),initialRequests=report.requests.length;
        await page.locator('#imageFile4').setInputFiles(landscape);
        await page.locator('#crop-dialog').waitFor({state:'visible'});
        check('no-upload-before-crop-confirm',report.requests.length===initialRequests);
        await page.locator('#crop-cancel').click();
        await page.locator('#crop-dialog').waitFor({state:'hidden'});
        check('cancel-preserves-flash-photo',(await download(4)).equals(before) && report.requests.length===initialRequests);

        /* Trigger the actual file-input handler and wait for the user's crop UI. */
        async function select(slot,file) {
            await page.locator(`#imageFile${slot}`).setInputFiles(file);
            await page.locator('#crop-dialog').waitFor({state:'visible'});
        }
        /* Confirm the UI upload, then validate bytes read back from the guest. */
        async function finish(slot,name,expectedColor) {
            await page.locator('#crop-confirm').click();
            await page.waitForFunction(n=>document.querySelector('#status').textContent.includes(`File ${n} uploaded successfully`),slot);
            const bytes=await download(slot),info=inspectJpeg(bytes);
            check(name+'-size-and-metadata',info.width===240 && info.height===240 && info.metadata.length===0 && !bytes.includes(Buffer.from('SYNTHETIC_')),info);
            if(expectedColor) {
                const mean=await pixels(bytes);
                check(name+'-selected-pixels',mean.every((value,i)=>Math.abs(value-expectedColor[i])<5),{mean});
            }
            await fs.writeFile(path.join(out,`${name}.jpg`),bytes);
            await fs.writeFile(path.join(out,`final-slot${slot}.jpg`),bytes);
            return bytes;
        }
        await select(4,landscape);
        await page.locator('#crop-preview').scrollIntoViewIfNeeded();
        const box=await page.locator('#crop-preview').boundingBox();
        const first=Number(await page.locator('#crop-zoom').inputValue());
        const corner={x:box.x+box.width*.875,y:box.y+box.height-2};
        await page.mouse.move(corner.x,corner.y);await page.mouse.down();
        await page.mouse.move(corner.x-box.width*.1,corner.y-box.height*.1,{steps:8});await page.mouse.up();
        const smaller=Number(await page.locator('#crop-zoom').inputValue());
        check('corner-drag-shrinks-frame',smaller>first,{first,smaller});
        const currentSize=480/smaller;
        const next={x:box.x+(80+currentSize)*.75*box.width/480-2,y:box.y+currentSize*.75*box.height/360-2};
        await page.mouse.move(next.x,next.y);await page.mouse.down();
        await page.mouse.move(next.x+box.width*.04,next.y+box.height*.04,{steps:8});await page.mouse.up();
        const larger=Number(await page.locator('#crop-zoom').inputValue());
        check('corner-drag-grows-frame',larger<smaller,{smaller,larger});
        await page.locator('#crop-zoom').focus();await page.keyboard.press('End');
        await page.locator('#crop-horizontal').focus();await page.keyboard.press('End');
        await page.screenshot({path:path.join(out,'landscape-crop.png')});
        await finish(4,'landscape-blue',[0,0,255]);

        await page.setViewportSize({width:390,height:844});
        await select(5,portrait);
        const bounds=await page.locator('#crop-dialog').boundingBox();
        check('mobile-dialog-fits-width',bounds.x>=0 && bounds.x+bounds.width<=391,{bounds});
        await page.locator('#crop-zoom').focus();await page.keyboard.press('End');
        await page.locator('#crop-vertical').focus();await page.keyboard.press('End');
        await page.screenshot({path:path.join(out,'portrait-mobile-crop.png')});
        const yellow=await finish(5,'portrait-yellow',[255,255,0]);
        const prior=report.requests.length;
        await select(5,portrait);await page.keyboard.press('Escape');
        await page.locator('#crop-dialog').waitFor({state:'hidden'});
        check('escape-preserves-flash-photo',report.requests.length===prior && (await download(5)).equals(yellow));

        await page.setViewportSize({width:1280,height:900});
        await select(4,noise);
        const uploadsBefore=report.requests.filter(item=>item.path==='/upload_chunk').length;
        const noisy=await finish(4,'noise-multipart');
        const chunkCount=report.requests.filter(item=>item.path==='/upload_chunk').length-uploadsBefore;
        check('actual-multiple-browser-multipart-chunks',chunkCount>=2 && chunkCount===Math.ceil(noisy.length/4096),{bytes:noisy.length,chunkCount});
    }
    check('no-page-script-errors',report.page_errors.length===0,{errors:report.page_errors});
    report.passed=true;
} catch(error) {
    report.error=error.stack ?? String(error);
    process.exitCode=1;
} finally {
    if(browser)await browser.close();
    await fs.writeFile(path.join(out,`browser-${args.stage}.json`),JSON.stringify(report,null,2)+'\n');
}
