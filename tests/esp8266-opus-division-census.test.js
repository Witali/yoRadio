const test=require('node:test'),assert=require('node:assert/strict');
const {parse,summarize,instrument}=require('../tools/esp8266_opus_asm/division_census.cjs');
test('division census preserves uint32 operands, order and duplicates',()=>{
 const pairs=parse('0,1\n4294967295,256\n23,257\n23,257\n7,8\n');
 assert.deepEqual(pairs,[[0,1],[4294967295,256],[23,257],[23,257],[7,8]]);
 const r=summarize(pairs);
 assert.equal(r.calls,5);assert.equal(r.small,3);assert.equal(r.fallback,2);assert.equal(r.powers,3);
 assert.equal(r.nmin,0);assert.equal(r.nmax,4294967295);
 assert.deepEqual(r.histogram[0],{d:257,calls:2});
});
test('division census accepts zero calls but rejects malformed or invalid operands',()=>{
 for(const s of ['1,0','-1,2','4294967296,1','1,4294967296','1.5,2','1,2\nbad'])assert.throws(()=>parse(s));
 assert.deepEqual(parse(''),[]);assert.equal(summarize([]).calls,0);assert.equal(summarize([]).nmin,null);
});
test('instrument only the rng/ft division and fail closed on upstream changes',()=>{
 const input='unsigned ec_decode(ec_dec *s,unsigned _ft){\n_this->ext=celt_udiv(_this->rng,_ft);\ns=_this->val/_this->ext;\n}';
 const r=instrument(input);
 assert.match(r,/return n\/d;/);assert.match(r,/s=_this->val\/_this->ext;/);
 assert.match(r,/y_trace_div\(_this->rng,_ft\)/);
 assert.throws(()=>instrument(input+input));assert.throws(()=>instrument('no match'));
});
