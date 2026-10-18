/* Exercise shipped setup JavaScript in Chrome against an owned loopback guest. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';

const args=Object.fromEntries(process.argv.slice(2).reduce((rows,item,index,all)=>
    index%2 ? rows : [...rows,[item.slice(2),all[index+1]]],[]));
const setup=new URL(args.url),station=new URL(args.station);
for(const url of [setup,station])assert.equal(url.hostname,'127.0.0.1');
const {chromium}=createRequire(import.meta.url)(path.join(args.modules,'playwright'));
const digest=data=>crypto.createHash('sha256').update(data).digest('hex');
const report={passed:false,scenario:args.scenario,stage:args.stage,checks:[],requests:[],
    dialogs:[],console:[],page_errors:[],script_sha256:digest(await fs.readFile(new URL(import.meta.url)))};
let browser;

/* Record each observed assertion before propagating a browser failure. */
function check(name,condition,details={}) {
    report.checks.push({name,passed:Boolean(condition),...details});assert(condition,name);
}

try {
    browser=await chromium.launch({executablePath:args.browser,headless:true});
    report.browser_version=browser.version();
    const context=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'block'});
    await context.route('**/*',route=> {
        const url=new URL(route.request().url());
        return ['http:','https:'].includes(url.protocol) && ![setup.origin,station.origin].includes(url.origin)
            ? route.abort() : route.continue();
    });
    const page=await context.newPage();page.setDefaultTimeout(45000);
    page.on('console',message=> {
        if(['error','warning'].includes(message.type()))report.console.push({type:message.type(),text:message.text()});
    });
    page.on('pageerror',error=>report.page_errors.push(String(error)));
    page.on('request',request=> {
        if(new URL(request.url()).pathname==='/configure') {
            const body=request.postDataJSON();
            report.requests.push({method:request.method(),ssid:body.ssid,password_bytes:Buffer.byteLength(body.password)});
        }
    });

    /* Drive real modal events; prompt cancellation must never submit credentials. */
    async function submit(promptReply) {
        const alerts=[];
        const handler=async dialog=> {
            report.dialogs.push({type:dialog.type(),message:dialog.message()});
            if(dialog.type()==='prompt') {
                if(promptReply===null)await dialog.dismiss();else await dialog.accept(promptReply);
            } else {alerts.push(dialog.message());await dialog.accept();}
        };
        page.on('dialog',handler);
        try {
            await page.locator('#wifiForm button[type=submit]').click();
            return {alerts,close:()=>page.off('dialog',handler)};
        } catch(error) {page.off('dialog',handler);throw error;}
    }

    if(args.stage!=='cold') {
        const scanning=page.waitForResponse(response=>new URL(response.url()).pathname==='/scan');
        const response=await page.goto(setup.href,{waitUntil:'domcontentloaded'});
        check('guest-setup-html',response.status()===200);
        report.served_html_sha256=digest(await response.body());
        const scan=await scanning;report.scan={status:scan.status(),records:await scan.json()};
        check('real-scan-response',report.scan.status===200 && Array.isArray(report.scan.records));
        await page.waitForFunction(()=>document.querySelector('#ssid option:not([disabled])')?.value);
        const options=await page.locator('#ssid option').evaluateAll(nodes=>nodes.map(option=>
            ({value:option.value,label:option.textContent,manual:option.dataset.manualEntry==='true'})));
        report.options=options;
        if(args.scenario==='manual-entry') {
            check('offline-scan-empty',report.scan.records.length===0);
            check('manual-option-is-marked',options.some(option=>option.manual && option.value==='manual'));
            await page.locator('#ssid').selectOption({index:options.findIndex(option=>option.manual)});
        } else {
            const record=report.scan.records.find(row=>row.ssid===args.ssid);
            check('configured-ap-found',Boolean(record));
            check('signed-signal-strength',record.rssi<0 && options.some(option=>
                option.value===args.ssid && option.label===`${args.ssid} (${record.rssi}dBm)`));
            await page.locator('#ssid').selectOption(args.ssid);
            check('discovered-network-is-not-manual-input',options.some(option=>option.value===args.ssid && !option.manual));
        }
        check('setup-fits-mobile-viewport',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
        if(args.stage==='preflight') {
            if(args.scenario==='manual-entry') {
                for(const [name,reply] of [['cancel',null],['empty','']]) {
                    const before=report.requests.length,dialogs=report.dialogs.length;
                    const submission=await submit(reply);submission.close();
                    check(`manual-${name}-does-not-post`,report.requests.length===before && report.dialogs.length===dialogs+1);
                }
            }
            await page.locator('#password').fill('short');
            const responsePromise=page.waitForResponse(response=>new URL(response.url()).pathname==='/configure');
            const submission=await submit(args.ssid);
            const rejected=await responsePromise;
            await page.waitForFunction(()=>document.querySelector('#wifiForm')?.style.display!=='none');
            // Response consumption and the alert run in a subsequent browser task.
            const deadline=Date.now()+10000;
            while(!submission.alerts.length && Date.now()<deadline)await new Promise(resolve=>setTimeout(resolve,25));
            submission.close();
            check('invalid-password-rejected',rejected.status()===400 && report.requests.length===1);
            check('invalid-password-alert',submission.alerts.length===1 && submission.alerts[0].startsWith('Failed to save configuration:'));
            check('invalid-submit-stays-in-setup',page.url()===setup.href && await page.locator('#wifiForm').isVisible());
            check('literal-manual-never-prompts',args.scenario==='manual-entry' || !report.dialogs.some(dialog=>dialog.type==='prompt'));
            await page.screenshot({path:path.join(args.output,'setup-'+args.scenario+'.png'),fullPage:true});
        } else {
            await page.locator('#password').fill('');
            const responsePromise=page.waitForResponse(response=>new URL(response.url()).pathname==='/configure');
            const submission=await submit(args.ssid),accepted=await responsePromise;
            check('valid-configure-accepted',accepted.status()===200 && report.requests.length===1 &&
                report.requests[0].ssid===args.ssid && report.requests[0].password_bytes===0);
            // The orchestrator restores only the external AP after a hidden-network
            // submit; the guest's reboot and association remain its own code.
            await fs.writeFile(path.join(args.output,'configuration-accepted.json'),JSON.stringify({accepted:true}));
            await page.waitForURL('about:blank');submission.close();
            check('factory-success-blank-target',page.url()==='about:blank' && submission.alerts.includes('Configuration saved successfully!'));
            check('correct-prompt-count',report.dialogs.filter(dialog=>dialog.type==='prompt').length===(args.scenario==='manual-entry'?1:0));
        }
    }
    if(args.stage!=='preflight') {
        /* Wait for the real STA port after reboot before rendering its actual UI. */
        const deadline=Date.now()+100000;let ready=false;
        while(Date.now()<deadline) {
            try {const reply=await context.request.get(station.href,{timeout:2500});
                if(reply.status()===200 && (await reply.text()).includes('/setclocktype')){ready=true;break;}
            }catch{}
            await new Promise(resolve=>setTimeout(resolve,200));
        }
        check('station-http-ready',ready);
        const response=await page.goto(station.href,{waitUntil:'domcontentloaded'});
        report.station_html_sha256=digest(await response.body());
        await page.waitForFunction(()=>document.querySelector('#switch-status')?.textContent==='' &&
            ['temp-unit-switch','hour-format-switch','mile-display-switch'].every(id=>
                document.getElementById(id)?.disabled===false));
        const settings=await (await context.request.get(new URL('/getsettings',station).href)).json();
        const displayed=await page.evaluate(()=>Object.fromEntries([
            ['tempUnit','temp-unit-switch'],['hourFormat','hour-format-switch'],
            ['mileDisplay','mile-display-switch'],['timeSync','time-sync-switch']
        ].map(([key,id])=>[key,Number(document.getElementById(id).checked)])));
        check('station-settings-finished-loading',await page.title()==='Smart Weather Clock' &&
            Object.keys(displayed).every(key=>displayed[key]===settings[key]),{displayed,settings});
        check('station-fits-mobile-viewport',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
        await page.screenshot({path:path.join(args.output,'station-'+args.stage+'.png'),fullPage:true});
    }
    check('no-javascript-exceptions',report.page_errors.length===0);
    const unexpected=report.console.filter(message=>!(args.stage==='preflight' &&
        (/Failed to load resource.*400/.test(message.text) || /Error:.*Network response was not ok/.test(message.text))));
    check('no-unexpected-console-errors',unexpected.length===0,{unexpected});
    report.passed=true;
}catch(error) {report.error=String(error.stack||error);process.exitCode=1;}
finally {
    if(browser)await browser.close();
    await fs.writeFile(path.join(args.output,'browser-'+args.stage+'.json'),JSON.stringify(report,null,2)+'\n');
}
