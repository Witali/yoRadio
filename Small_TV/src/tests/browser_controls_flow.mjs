/* Exercise the shipped controls through Chrome and the real guest HTTP server. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';

const args=Object.fromEntries(process.argv.slice(2).reduce((out,v,i,a)=>i%2?out:[...out,[v.slice(2),a[i+1]]],[]));
const base=new URL(args.url),out=args.output;
assert.equal(base.hostname,'127.0.0.1','Use only the owned loopback guest');
const {chromium}=createRequire(import.meta.url)(path.join(args.modules,'playwright'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const report={passed:false,stage:args.stage,checks:[],console:[],page_errors:[],posts:[],pages:[],
    script_sha256:sha(await fs.readFile(new URL(import.meta.url)))};
let browser,page,context;

/* Keep the failing assertion and every preceding observation in the report. */
function check(name,condition,details={}) {
    report.checks.push({name,passed:Boolean(condition),...details});assert(condition,name);
}

/* Require a successful actual guest read; fixtures never replace HTTP responses. */
async function get(route,json=true) {
    const response=await context.request.get(new URL(route,base).href);
    assert.equal(response.status(),200,route);
    return json?response.json():Number(await response.text());
}

/* Read all public persistent controls independently of their displayed values. */
async function snapshot() {
    return {flags:await get('/getsettings'),theme:await get('/getclocktype',false),
        animation:await get('/getgifvalue',false),date:await get('/GetTimeModeValue',false),
        day:(await get('/get_led_brightness')).brightness,colors:await get('/get_clock_colors'),
        start:await get('/GetNightStartTime',false),stop:await get('/GetNightStopTime',false),
        night:(await get('/get_night_brightness')).brightness,
        interval:(await get('/get_display_time')).displaytime,photos:await get('/get_checkbox_state')};
}

/* Wait for the page's own loaders before checking or manipulating its controls. */
async function open(route,kind) {
    const response=await page.goto(new URL(route,base).href,{waitUntil:'domcontentloaded'});
    check(`${args.stage}-${route}-http`,response.status()===200);
    report.pages.push({route,sha256:sha(await response.body()),viewport:page.viewportSize()});
    if(kind==='settings') await page.waitForFunction(()=>document.querySelector('#switch-status')?.textContent==='' &&
        ['temp-unit-switch','hour-format-switch','mile-display-switch'].every(id=>!document.getElementById(id).disabled));
    if(kind==='photo') await page.waitForFunction(()=>Array.from({length:5},(_,i)=>document.querySelector('#thumbnail'+(i+1)))
        .every(image=>image?.complete&&image.naturalWidth===240) && document.querySelector('#loading-overlay').style.display==='none');
    check(`${route}-fits-${page.viewportSize().width}`,await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
}

/* Observe one real UI write and its acknowledgement, without injecting HTTP. */
async function change(route,action) {
    const pending=page.waitForResponse(r=>new URL(r.url()).pathname===route&&r.request().method()==='POST');
    await action();const response=await pending;
    check(`${route}-acknowledged`,response.status()===200);
    await response.finished();
}

/* Input/change are the page's public event interface; native selectors use real events. */
async function input(id,value,event,route) {
    await change(route,()=>page.locator('#'+id).evaluate((node,{value,event})=>{
        node.value=String(value);node.dispatchEvent(new Event(event,{bubbles:true}));
    },{value,event}));
}

/* Use the visible label for CSS-hidden switches and real checkbox clicks otherwise. */
async function flag(id,value,route,hidden=false) {
    if(await page.locator('#'+id).isChecked()!==value)
        await change(route,()=>hidden?page.locator('#'+id).locator('..').click():page.locator('#'+id).setChecked(value));
}

/* Check reloaded DOM values against API state after all asynchronous GETs finish. */
async function settingsMatch(state,label) {
    await page.waitForFunction(s=>['tempUnit','hourFormat','mileDisplay','timeSync'].every((key,i)=>
        Number(document.getElementById(['temp-unit-switch','hour-format-switch','mile-display-switch','time-sync-switch'][i]).checked)===s.flags[key]) &&
        document.getElementById('themeselect').value===String(s.theme) &&
        document.getElementById('giflist').value===String(s.animation) &&
        document.getElementById('timelist').value===String(s.date) &&
        Number(document.getElementById('ledBrightness').value)===s.day &&
        [0,1,2].every(i=>document.getElementById('colorPicker'+i).value===s.colors['color'+i]),state);
    check(label,true);
    check('browser-time-sync-disabled',await page.locator('#time-sync-switch').isDisabled());
}

/* Night schedule and password privacy are observed separately from the clock page. */
async function advancedMatch(state,label,ntp) {
    await page.waitForFunction(s=>Number(document.getElementById('night').checked)===s.flags.nightmode &&
        Number(document.getElementById('start').value)===s.start && Number(document.getElementById('stop').value)===s.stop &&
        Number(document.getElementById('brightness').value)===s.night,state);
    check(label,true);check(label+'-private-key-empty',await page.locator('#key').inputValue()==='');
    if(ntp!==undefined)check(label+'-saved-ntp',await page.locator('#ntp').inputValue()===ntp);
}

/* Photo settings are meaningful only after every thumbnail and handler is ready. */
async function photoMatch(state,label) {
    await page.waitForFunction(s=>Number(document.getElementById('displaytime').value)===s.interval &&
        [1,2,3,4,5].every(i=>document.getElementById(`file${i}-switch`).checked===s.photos[`file${i}_switch`]),state);
    check(label,true);
}

try {
    browser=await chromium.launch({executablePath:args.browser,headless:true});report.browser_version=browser.version();
    context=await browser.newContext({viewport:{width:1280,height:900},serviceWorkers:'block'});
    await context.route('**/*',route=>{
        const url=new URL(route.request().url());
        return ['http:','https:'].includes(url.protocol)&&url.origin!==base.origin?route.abort():route.continue();
    });
    page=await context.newPage();page.setDefaultTimeout(45000);
    page.on('pageerror',error=>report.page_errors.push(String(error)));
    page.on('console',message=>{if(['warning','error'].includes(message.type()))report.console.push({type:message.type(),text:message.text()});});
    page.on('request',request=>{if(request.method()==='POST')report.posts.push(new URL(request.url()).pathname);});
    page.on('dialog',dialog=>dialog.accept());
    const expected=args.stage==='cold'?JSON.parse(await fs.readFile(path.join(out,'expected-controls.json'),'utf8')):null;
    for(const viewport of [{width:1280,height:900},{width:390,height:844}]) {
        await page.setViewportSize(viewport);
        const label=String(viewport.width);
        await open('/settings','settings');await settingsMatch(await snapshot(),'initial-settings-'+label);
        if(args.stage!=='cold') {
            for(const [id,post,read,values] of [
                ['themeselect','/setclocktype','/getclocktype',[0,1,2,3]],
                ['giflist','/setgifvalue','/getgifvalue',[0,1,2,3,4]],
                ['timelist','/SetTimeModeValue','/GetTimeModeValue',[0,1,2]]])
                for(const value of values){await change(post,()=>page.locator('#'+id).selectOption(String(value)));check(id+'-'+value,await get(read,false)===value);}
            for(const [id,key] of [['temp-unit-switch','tempUnit'],['hour-format-switch','hourFormat'],['mile-display-switch','mileDisplay']])
                for(const value of [true,false,true]){await flag(id,value,'/settings',true);check(key+'-'+value,(await get('/getsettings'))[key]===Number(value));}
            for(const value of [0,100,37]){await input('ledBrightness',value,'input','/set_led_brightness');check('day-'+value,(await get('/get_led_brightness')).brightness===value);}
            for(const [i,value] of ['#123456','#abcdef','#7f4081'].entries()) {
                await input('colorPicker'+i,value,'change','/set_clock_color');
                const channels=value.slice(1).match(/../g).map(v=>parseInt(v,16));
                const q=channels.map((v,c)=>c===1?((v>>2)<<2)|(v>>6):((v>>3)<<3)|(v>>5));
                const wanted='#'+q.map(v=>v.toString(16).padStart(2,'0')).join('');
                check('color-'+i,(await get('/get_clock_colors'))['color'+i]===wanted);
            }
            await page.locator('#cityInput').fill('  Fixture,CN  ');
            await change('/updateCity',()=>page.locator('#cityForm button').click());
        }
        const state=await snapshot();await open('/','settings');await settingsMatch(state,'root-settings-reload-'+label);
        if(expected)check('cold-clock-api-'+label,JSON.stringify(state)===JSON.stringify(expected.state));
        await page.screenshot({path:path.join(out,`${args.stage}-settings-${label}.png`),fullPage:true});
        await open('/advanced','advanced');await advancedMatch(await snapshot(),'initial-advanced-'+label,args.stage==='cold'?expected.ntp:undefined);
        if(args.stage!=='cold') {
            for(const value of [false,true]){await flag('night',value,'/settings');check('night-'+value,(await get('/getsettings')).nightmode===Number(value));}
            for(const [id,post,read,values] of [['start','/SetNightStartTime','/GetNightStartTime',[18,23]],['stop','/SetNightStopTime','/GetNightStopTime',[12,5]]])
                for(const value of values){await input(id,value,'change',post);check(id+'-'+value,await get(read,false)===value);}
            for(const value of [2,99]){await input('brightness',value,'change','/set_night_brightness');check('night-brightness-'+value,(await get('/get_night_brightness')).brightness===value);}
            for(const ntp of ['clock&"<\'>.invalid','pool.ntp.org']) {
                await page.locator('#ntp').fill(ntp);await page.locator('#key').fill('SYNTHETIC_BROWSER_KEY');
                await change('/advancedset',()=>page.locator('#f button').click());
                await open('/advanced','advanced');await advancedMatch(await snapshot(),'advanced-reload-'+label,ntp);
            }
        }
        await page.screenshot({path:path.join(out,`${args.stage}-advanced-${label}.png`),fullPage:true});
        await open('/photo','photo');await photoMatch(await snapshot(),'initial-photos-'+label);
        if(args.stage!=='cold') {
            for(const value of [3,60]){await input('displaytime',value,'change','/set_display_time');check('photo-interval-'+value,(await get('/get_display_time')).displaytime===value);}
            for(const mask of [0,1,17,31]) {
                for(let i=1;i<=5;i++)await flag(`file${i}-switch`,Boolean(mask&(1<<(i-1))),'/set_checkbox_state');
                const actual=await get('/get_checkbox_state');
                check('photo-mask-'+mask,[1,2,3,4,5].every(i=>actual[`file${i}_switch`]===Boolean(mask&(1<<(i-1)))));
            }
        }
        const stateAfter=await snapshot();await open('/photo','photo');await photoMatch(stateAfter,'photo-reload-'+label);
        if(expected)check('cold-all-api-'+label,JSON.stringify(stateAfter)===JSON.stringify(expected.state));
        await page.screenshot({path:path.join(out,`${args.stage}-photo-${label}.png`),fullPage:true});
    }
    report.final=await snapshot();
    if(args.stage!=='cold')await fs.writeFile(path.join(out,'expected-controls.json'),JSON.stringify({state:report.final,ntp:'pool.ntp.org',city:'Fixture',country:'CN'}));
    else check('cold-stage-read-only',report.posts.length===0);
    check('no-javascript-exceptions',report.page_errors.length===0);
    check('no-console-warnings-errors',report.console.length===0);
    report.passed=true;
} catch(error){report.error=String(error);process.exitCode=1;}
finally {
    if(browser)await browser.close();
    await fs.writeFile(path.join(out,'browser-controls-'+args.stage+'.json'),JSON.stringify(report,null,2)+'\n');
}
