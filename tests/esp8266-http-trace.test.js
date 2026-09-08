const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),component=path.join(root,'esp8266/rtos-sdk-native/components/esp_http_server');
const wsl=process.platform==='win32',p=f=>wsl?'/mnt/'+f[0].toLowerCase()+f.slice(2).replace(/\\/g,'/'):f;
const {analyze,decodeTrace}=require('../tools/analyze_esp8266_web_trace.cjs');

test('physical volume benchmark starts inward at either limit and never awaits a clamped no-op',()=>{
  const source=fs.readFileSync(path.join(root,'tools/test_esp8266_webui_latency.cjs'),'utf8');
  const fn=source.slice(source.indexOf('function volumeButtonSelector'),source.indexOf('async function buttons'));
  const selector=require('node:vm').runInNewContext(fn+';volumeButtonSelector');
  assert.match(source,/if\(!await load\(page,'playing-'\+codec,round\)\)[\s\S]*?throw new Error/);
  for(const original of [0,1,2,128,253,254]) {
    let current=original;
    for(let i=0;i<10;++i){const next=Math.min(254,Math.max(0,current+(selector(original,i)==='#volpbutton'?2:-2)));
      assert.notEqual(next,current);current=next;}
    assert.equal(current,original);
  }
});
test('latency analysis excludes only proven TX wait; RAM, unknown and raw outliers remain',()=>{
  const good={id:'a-1',path:'/',total_us:1000000,tx_wait_us:900000,tx_sleep_budget_us:900000,mem_wait_us:0,other_wait_us:0,mem_errors:0,result:0};
  const records=[good,{...good,id:'a-2',mem_errors:1},{...good,id:'a-3',tx_sleep_budget_us:1000},{...good,id:'a-4',result:-1}];
  const loads=['a-1','a-2','a-3','a-4','missing'].map(traceId=>({kind:'cold',readyMs:1200,pass:false,resources:[{path:'/',traceId,totalMs:1100}]}));
  const r=analyze({loads},records.map(r=>'WEBTRACE '+JSON.stringify(r)).join('\n'));
  assert.equal(r.excluded,1);assert.equal(r.raw.count,5);assert.equal(r.processingSample.count,4);
  assert.equal(r.rawFailures,5);assert.equal(r.processingFailures,4);assert.equal(loads.length,5);
  assert.equal(analyze({loads},'').excluded,0);
  assert.equal(analyze({loads},[good,good].map(r=>'WEBTRACE '+JSON.stringify(r)).join('\n')).excluded,0);
  const mixed={...loads[0],resources:[...loads[0].resources,{path:'/',traceId:'a-2',totalMs:1100}]};
  assert.equal(analyze({loads:[mixed]},records.map(r=>'WEBTRACE '+JSON.stringify(r)).join('\n')).excluded,0);
  assert.equal(analyze({loads:[{...loads[0],readyMs:3000}]},'WEBTRACE '+JSON.stringify(good)).excluded,0);
  const withTime={...loads[4],resources:[{...loads[4].resources[0],startTime:1000}]};
  const ping={samples:[{startTime:1000,elapsedMs:750,rttMs:null,status:'TimedOut'}]};
  const linked=analyze({loads:[withTime]},'',ping);
  assert.equal(linked.samples[0].pingDuringLoad.failures,1);assert.equal(linked.excluded,0);
});
test('actual HTTP trace separates TX backpressure, RAM retries, I/O and wrap-safe wall time',()=>{
  const dir=fs.mkdtempSync(path.join(root,'.build/http-trace-'));
  fs.copyFileSync(path.join(component,'include/httpd_trace.h'),path.join(dir,'httpd_trace.h'));
  fs.writeFileSync(path.join(dir,'esp_http_server.h'),'#pragma once\n#include <stddef.h>\ntypedef struct {const char *uri;} httpd_req_t;\nint httpd_resp_set_hdr(httpd_req_t *,const char *,const char *);\n');
  fs.writeFileSync(path.join(dir,'esp_timer.h'),'#include <stdint.h>\nint64_t esp_timer_get_time(void);\n');
  fs.writeFileSync(path.join(dir,'esp_system.h'),'#include <stdint.h>\nuint32_t esp_random(void);\n');
  fs.writeFileSync(path.join(dir,'esp_log.h'),'#define ESP_LOG_INFO 3\n#define esp_log_write(level,tag,...) do {(void)(level);(void)(tag);printf(__VA_ARGS__);}while(0)\n');
  fs.writeFileSync(path.join(dir,'test.c'),`#include "httpd_trace.h"
#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <errno.h>
static uint32_t now=0xfffffff0U;
int64_t esp_timer_get_time(void){errno=EDOM;return now;}
uint32_t esp_random(void){return 0xabcdef01;}
int httpd_resp_set_hdr(httpd_req_t *r,const char *k,const char *v){(void)r;assert(!strcmp(k,"X-YoRadio-Trace"));assert(!strcmp(v,"abcdef01-1"));return 0;}
int main(void){
  httpd_req_t r={"/data/playlist.csv?private=must-not-log"};
  httpd_trace_begin();now+=20;httpd_trace_route(&r);
  uint32_t s=now;now+=40;httpd_trace_read(s);
  s=now;now+=30;httpd_trace_recv(s);
  s=now;now+=50;errno=EAGAIN;httpd_trace_send(s,100,0);assert(errno==EAGAIN);
  s=now;now+=10;httpd_trace_send(s,-1,EAGAIN);
  s=now;now+=300000;httpd_trace_wait(s,EAGAIN,1000);
  s=now;now+=5;httpd_trace_send(s,-1,ENOMEM);
  s=now;now+=90000;httpd_trace_wait(s,ENOMEM,1000);
  s=now;now+=1000;httpd_trace_wait(s,EINTR,1000);
  httpd_trace_end(0);httpd_trace_end(0);
  httpd_trace_index_begin();assert(!httpd_trace_ws_begin());now+=100;httpd_trace_end(0);
  assert(httpd_trace_ws_begin());now+=1;httpd_trace_ws_end(0);
  assert(httpd_trace_ws_begin());now+=100;httpd_trace_ws_end(-1);
  uint32_t selected=now;now+=250000;
  httpd_trace_dispatch(selected,now,true);now+=32000;
  httpd_trace_request_begin(true);s=now;now+=700;httpd_trace_recv(s);
  httpd_trace_index_begin();now+=20;httpd_trace_end(0);httpd_trace_end(0);
  return 0;}
`);
  const bin=path.join(dir,'test'),args=['-std=c11','-Wall','-Wextra','-Werror','-fsanitize=undefined','-DYORADIO_ESP8266_WEB_PROFILE=1','-I'+p(dir),'-I'+p(path.join(component,'include')),p(path.join(dir,'test.c')),p(path.join(component,'src/httpd_trace.c')),'-o',p(bin)];
  let r=spawnSync(wsl?'wsl.exe':'cc',wsl?['--exec','gcc',...args]:args,{encoding:'utf8'});assert.equal(r.status,0,r.stderr);
  r=spawnSync(wsl?'wsl.exe':bin,wsl?['--exec',p(bin)]:[],{encoding:'utf8'});assert.equal(r.status,0,r.stderr);
  const lines=r.stdout.trim().split('\n');assert.equal(lines.length,4);
  const record=decodeTrace(JSON.parse(lines[0].slice('WEBTRACE '.length)));
  assert.equal(record.total_us,391155);assert.equal(record.tx_wait_us,300000);
  assert.equal(record.tx_sleep_budget_us,1000);
  assert.equal(record.mem_wait_us,90000);assert.equal(record.other_wait_us,1000);
  assert.equal(record.mem_errors,1);assert.equal(record.read_us,40);assert.equal(record.recv_us,30);
  assert.equal(record.send_us,65);assert.equal(record.max_send_us,50);assert.equal(record.bytes,100);
  assert.equal(record.path,'/data/playlist.csv');assert.ok(!r.stdout.includes('private'));
  assert.equal(record.last_errno,12); // ENOMEM on the POSIX test host.
  assert.equal(decodeTrace(JSON.parse(lines[1].slice('WEBTRACE '.length))).path,'/ws:getindex');
  assert.equal(decodeTrace(JSON.parse(lines[2].slice('WEBTRACE '.length))).result,-1);
  const dispatch=decodeTrace(JSON.parse(lines[3].slice('WEBTRACE '.length)));
  assert.equal(dispatch.path,'/ws:getindex');assert.equal(dispatch.select_wait_us,250000);
  assert.equal(dispatch.dispatch_us,32000);assert.equal(dispatch.dispatch_flags,1);
  assert.equal(dispatch.recv_us,700);assert.equal(dispatch.parse_us,700);
  assert.equal(dispatch.total_us,720);assert.equal(dispatch.tx_wait_us,0);
});

test('startup correlation bounds delay before WS dispatch without calling it network wait',()=>{
  const base={total_us:10000,parse_us:1000,recv_us:500,send_us:8000,result:0,
    tx_wait_us:0,tx_sleep_budget_us:0,mem_wait_us:0,other_wait_us:0,mem_errors:0};
  const root={...base,id:'a-1',path:'/',start_us:0xffff0000};
  const index={...base,id:'a-2',path:'/ws:getindex',start_us:(root.start_us+300000)>>>0,
    select_wait_us:250000,dispatch_us:1000,dispatch_flags:1};
  const playlist={...base,id:'a-3',path:'/data/playlist.csv',start_us:(root.start_us+350000)>>>0};
  const resources=[{path:'/',traceId:'a-1',startTime:1000,requestStart:0,ttfbMs:10,totalMs:20},
    {path:'/data/playlist.csv',traceId:'a-3',startTime:1350,requestStart:0,ttfbMs:10,totalMs:20}];
  const loads=[{kind:'cold',readyMs:600,pass:false,resources,pageTrace:{timeOrigin:1000,indexSentMs:100}}];
  const serial=[root,index,playlist].map(r=>'WEBTRACE '+JSON.stringify(r)).join('\n');
  const r=analyze({loads},serial),s=r.samples[0].startup;
  assert.deepEqual(s.commandToSessionStartMs,{min:200,max:210});
  assert.equal(s.clockOffsetUncertaintyMs,10);assert.equal(s.readyToSessionMs,1);
  assert.equal(s.sessionToCommandParsedMs,1);assert.equal(s.selectWaitMs,250);
  assert.equal(r.excluded,0);assert.equal(r.processingFailures,1);
  assert.equal(analyze({loads},serial+'\nWEBTRACE '+JSON.stringify(index)).samples[0].startup,null);
  assert.equal(analyze({loads:[{...loads[0],pageTrace:{indexSentMs:100}}]},serial).samples[0].startup,null);
  for(const n of [18,19,22])assert.ok(decodeTrace(Array(n).fill(0)));
  assert.throws(()=>decodeTrace(Array(20).fill(0)),/Unknown/);
});
