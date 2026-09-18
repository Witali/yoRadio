const test=require('node:test'),assert=require('node:assert/strict');
const {evaluate}=require('./esp8266_audio_profile/run_station_continuity.cjs');
function fixture() {
  const audio={generation:4,uptime_ms:10000,rx_bytes:100,pcm_frames:100,sample_rate:44100,
    pcm_age_ms:0,underruns:20,free_heap:8000,dma_eofs:100,output_enabled:true,tx_driver_fail:2};
  const status={playing:true,connecting:false,error:'',station:'test',codec:'MP3',app_address:65536,bitrate:128,rssi:-60,min_heap:452};
  const response=body=>({http:200,body});
  return {station:1,name:'test',command:{messages:[{current:1}]},observed_ms:65000,
    before:{audio:response(audio),status:response(status)},
    after:{audio:response({...audio,uptime_ms:75000,rx_bytes:1000100,pcm_frames:100+44100*65,dma_eofs:10000}),status:response({...status})}};
}
test('MP3 supports 44.1kHz and ignores historical underruns/minimum heap',()=>assert.equal(evaluate(fixture()).pass,true));
test('a single new DMA miss fails',()=>{const r=fixture();r.after.audio.body.underruns++;assert.equal(evaluate(r).pass,false);});
test('no PCM and stopped state never pass',()=>{const r=fixture();r.after.audio.body.pcm_frames=100;r.after.status.body.playing=false;assert.equal(evaluate(r).pass,false);});
test('wrong station fails even with flowing PCM',()=>{const r=fixture();r.after.status.body.station='other';assert.equal(evaluate(r).pass,false);});
test('missing measurement cannot become a pass',()=>{const r=fixture();r.after.audio={error:'timeout'};assert.equal(evaluate(r).pass,false);});
test('Opus requires a current autonomous window inside observation',()=>{
  const r=fixture();for(const side of [r.before,r.after]){side.status.body.codec='OPUS';side.audio.body.sample_rate=48000;}
  r.after.audio.body.pcm_frames=100+48000*65;
  r.quiet={http:200,body:{valid:true,generation:4,start_ms:40000,end_ms:65000,frames:1200000,sample_rate:48000,underruns:0,age_ms:10000}};
  assert.equal(evaluate(r).pass,true);r.quiet.body.start_ms=0;assert.equal(evaluate(r).pass,false);
});
