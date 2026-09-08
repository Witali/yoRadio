const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),main=path.join(root,'esp8266/rtos-sdk-native/main');
const wsl=process.platform==='win32',p=f=>wsl?'/mnt/'+f[0].toLowerCase()+f.slice(2).replace(/\\/g,'/'):f;

test('actual WebUI writers keep UTF-8 frames valid with malformed ICY and bounded buffers',()=>{
  const dir=fs.mkdtempSync(path.join(root,'.build/json-text-'));
  const source=fs.readFileSync(path.join(main,'web_service.c'),'utf8');
  const escape=source.slice(source.indexOf('static void json_escape'),source.indexOf('static uint32_t text_hash'));
  const writers=source.slice(source.indexOf('static void json_writer_init'),source.indexOf('static void capture_status'));
  fs.writeFileSync(path.join(dir,'test.c'),`#include "json_text.h"
#include <stdio.h>
#include <stdbool.h>
#include <stdarg.h>
#include <assert.h>
typedef struct {char *output;size_t capacity,length;bool valid;} json_writer_t;
${escape}
${writers}
int main(void) {
  /* Minimal real-board regression: the Opera ICY name contained raw F1. */
  const char *inputs[]={"Pl\\xf1" "cido", "\\xc3\\xb1 \\xd1\\x91 \\xe2\\x80\\x94 \\xf0\\x9f\\x8e\\xb5",
    "\\xc0\\xaf\\xed\\xa0\\x80\\xf4\\x90\\x80\\x80", "end\\xe2\\x82", "quote\\\"slash\\\\", "\\n\\r\\t"};
  for(size_t i=0;i<sizeof(inputs)/sizeof(inputs[0]);++i) {
    char output[1088];json_writer_t w;json_writer_init(&w,output,sizeof(output));
    json_writer_raw(&w,"{\\\"meta\\\":\\\"");json_writer_escaped(&w,inputs[i]);
    json_writer_format(&w,"\\\",\\\"v\\\":%u}",42U);assert(w.valid);puts(output);
    for(size_t cap=1;cap<24;++cap){char small[24];memset(small,'x',sizeof(small));
      json_escape(inputs[i],small,cap);assert(strlen(small)<cap);
      assert(small[cap]=='x');printf("\\\"%s\\\"\\n",small);}
  }
  char output[4];json_writer_t w;json_writer_init(&w,output,sizeof(output));
  json_writer_escaped(&w,"\\xf0\\x9f\\x8e\\xb5");assert(!w.valid && !output[0]);
  json_escape("x",output,0);return 0;
}
`);
  const bin=path.join(dir,'test'),args=['-std=c11','-Wall','-Wextra','-Werror','-fsanitize=undefined', '-I'+p(main),p(path.join(dir,'test.c')),'-o',p(bin)];
  let r=spawnSync(wsl?'wsl.exe':'cc',wsl?['--exec','gcc',...args]:args,{encoding:'utf8'});assert.equal(r.status,0,r.stderr);
  r=spawnSync(wsl?'wsl.exe':bin,wsl?['--exec',p(bin)]:[],{});assert.equal(r.status,0,r.stderr.toString());
  const text=new TextDecoder('utf-8',{fatal:true}).decode(r.stdout);
  const rows=text.trim().split('\n').map(line=>JSON.parse(line));
  const values=rows.filter(r=>typeof r==='object').map(r=>r.meta);
  assert.deepEqual(values,['Pl?cido','\u00f1 \u0451 \u2014 \ud83c\udfb5','?????????','end??','quote"slash\\','']);
  assert.equal(rows.length,6*24);
});
