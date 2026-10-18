#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "websocket_message.h"

static uint64_t scalars, split_cases, utf8_oracles, protocol_cases, close_codes, limit_cases, timeout_cases;

// Independent numeric decoder: derive Unicode scalar and minimum permitted
// value instead of using the production lead-byte/second-byte range tables.
static bool reference_utf8_check(const uint8_t *text, size_t size, bool final) {
    size_t i=0;
    while(i<size) {
        uint32_t value=text[i++], minimum;
        unsigned following;
        if(value<128) continue;
        if((value&0xe0U)==0xc0U) { value&=31; following=1; minimum=128; }
        else if((value&0xf0U)==0xe0U) { value&=15; following=2; minimum=2048; }
        else if((value&0xf8U)==0xf0U) { value&=7; following=3; minimum=65536; }
        else return false;
        while(following--) {
            if(i==size) {
                if(final) return false;
                unsigned missing=following+1;
                uint32_t minimum_possible=value << (6U*missing);
                uint32_t maximum_possible=minimum_possible+((1U << (6U*missing))-1U);
                if(maximum_possible<minimum || minimum_possible>0x10ffffU) return false;
                return !(minimum_possible>=0xd800U && maximum_possible<=0xdfffU);
            }
            uint8_t next=text[i++];
            if((next&0xc0U)!=0x80U) return false;
            value=value*64U+(next&63U);
        }
        if(value<minimum || value>0x10ffffU || (value>=0xd800U && value<=0xdfffU)) return false;
    }
    return true;
}

static size_t encode_scalar(uint32_t value, uint8_t *out) {
    if(value<128) { out[0]=(uint8_t)value; return 1; }
    if(value<2048) { out[0]=(uint8_t)(0xc0U|value/64); out[1]=(uint8_t)(0x80U|value%64); return 2; }
    if(value<65536) {
        out[0]=(uint8_t)(0xe0U|value/4096); out[1]=(uint8_t)(0x80U|(value/64)%64); out[2]=(uint8_t)(0x80U|value%64); return 3;
    }
    out[0]=(uint8_t)(0xf0U|value/262144); out[1]=(uint8_t)(0x80U|(value/4096)%64);
    out[2]=(uint8_t)(0x80U|(value/64)%64); out[3]=(uint8_t)(0x80U|value%64); return 4;
}

static void expect(websocket_message_result_t result, websocket_message_event_t event, uint16_t code) {
    assert(result.event==event && result.close_code==code);
}

static websocket_message_t initialized(uint8_t *buffer, size_t capacity, uint64_t timeout) {
    websocket_message_t message;
    assert(websocket_message_init(&message,buffer,capacity,timeout));
    assert(!message.used && !message.active && !message.close_sent && !message.close_received && !message.failure_code);
    return message;
}

static void test_scalars_and_splits(void) {
    uint8_t text[8], buffer[16], reason[8];
    for(uint32_t scalar=0;scalar<=0x10ffffU;++scalar) {
        if(scalar>=0xd800U && scalar<=0xdfffU) continue;
        size_t size=encode_scalar(scalar,text);
        assert(websocket_message_utf8_valid(text,size)); ++scalars;
        for(size_t split=0;split<=size;++split) {
            websocket_message_t message=initialized(buffer,sizeof(buffer),100);
            expect(websocket_message_feed(&message,1,false,text,split,0),WEBSOCKET_MESSAGE_NONE,0);
            websocket_message_result_t result=websocket_message_feed(&message,0,true,text+split,size-split,1);
            expect(result,WEBSOCKET_MESSAGE_TEXT,0);
            assert(result.size==size && result.data==buffer && !memcmp(result.data,text,size) && !buffer[size]);
            assert(!message.used && !message.active); ++split_cases;
        }
        // Close reasons use exactly the same UTF-8 interpretation.
        reason[0]=3; reason[1]=0xe8; memcpy(reason+2,text,size);
        websocket_message_t message=initialized(buffer,sizeof(buffer),100);
        websocket_message_result_t result=websocket_message_feed(&message,8,true,reason,size+2,0);
        expect(result,WEBSOCKET_MESSAGE_CLOSE,1000); assert(result.data==reason && result.size==size+2 && message.close_received);
    }
}

static void check_utf8_case(const uint8_t *text, size_t size) {
    bool valid=reference_utf8_check(text,size,true);
    assert(websocket_message_utf8_valid(text,size)==valid);
    uint8_t buffer[32]; websocket_message_t message=initialized(buffer,sizeof(buffer),1000);
    websocket_message_result_t result=websocket_message_feed(&message,1,true,text,size,0);
    expect(result,valid?WEBSOCKET_MESSAGE_TEXT:WEBSOCKET_MESSAGE_ERROR,valid?0:1007);
    for(size_t split=0;split<=size;++split) {
        message=initialized(buffer,sizeof(buffer),1000);
        bool prefix=reference_utf8_check(text,split,false);
        expect(websocket_message_feed(&message,1,false,text,split,0),prefix?WEBSOCKET_MESSAGE_NONE:WEBSOCKET_MESSAGE_ERROR,prefix?0:1007);
        result=websocket_message_feed(&message,0,true,text+split,size-split,1);
        expect(result,valid?WEBSOCKET_MESSAGE_TEXT:WEBSOCKET_MESSAGE_ERROR,valid?0:1007);
    }
    ++utf8_oracles;
}

static void test_utf8_invalid_and_oracle(void) {
    uint8_t text[16];
    for(unsigned first=0;first<256;++first) for(unsigned second=0;second<256;++second) {
        text[0]=(uint8_t)first; text[1]=(uint8_t)second; check_utf8_case(text,2);
    }
    // All leading/second-byte combinations with canonical continuation suffixes
    // exercise overlong sequences, surrogate bounds, >U+10FFFF and truncation.
    for(unsigned first=0;first<256;++first) for(unsigned second=0;second<256;++second) {
        text[0]=(uint8_t)first; text[1]=(uint8_t)second; text[2]=text[3]=0x80;
        check_utf8_case(text,3); check_utf8_case(text,4);
    }
    uint32_t random=0x456789ab;
    for(unsigned test=0;test<100000;++test) {
        size_t size=test%9;
        for(size_t i=0;i<size;++i) { random=random*1664525U+1013904223U; text[i]=(uint8_t)(random>>24); }
        check_utf8_case(text,size);
    }
    assert(websocket_message_utf8_valid(NULL,0) && !websocket_message_utf8_valid(NULL,1));
    const uint8_t invalid_prefix[]={0xed,0xa0};
    uint8_t buffer[8]; websocket_message_t message=initialized(buffer,sizeof(buffer),100);
    expect(websocket_message_feed(&message,1,false,invalid_prefix,sizeof(invalid_prefix),0),WEBSOCKET_MESSAGE_ERROR,1007);
    expect(websocket_message_feed(&message,9,true,NULL,0,1),WEBSOCKET_MESSAGE_ERROR,1007);
    ++protocol_cases;
}

static void test_state_and_control(void) {
    uint8_t buffer[256], payload[126]; memset(payload,'x',sizeof(payload));
    for(unsigned opcode=0;opcode<=255;++opcode) for(unsigned final=0;final<2;++final) {
        websocket_message_t message=initialized(buffer,sizeof(buffer),100);
        websocket_message_result_t result=websocket_message_feed(&message,(uint8_t)opcode,final,payload,2,0);
        if(opcode==1 || opcode==2) expect(result,final?(opcode==1?WEBSOCKET_MESSAGE_TEXT:WEBSOCKET_MESSAGE_BINARY):WEBSOCKET_MESSAGE_NONE,0);
        else if((opcode==9 || opcode==10) && final) expect(result,opcode==9?WEBSOCKET_MESSAGE_PING:WEBSOCKET_MESSAGE_PONG,0);
        else expect(result,WEBSOCKET_MESSAGE_ERROR,1002); // Close payload xx is an invalid code.
        ++protocol_cases;
    }
    for(unsigned control=8;control<=10;++control) for(unsigned size=0;size<=126;++size) for(unsigned final=0;final<2;++final) {
        websocket_message_t message=initialized(buffer,sizeof(buffer),100);
        payload[0]=3; payload[1]=0xe8;
        expect(websocket_message_feed(&message,1,false,(const uint8_t *)"a",1,0),WEBSOCKET_MESSAGE_NONE,0);
        websocket_message_result_t result=websocket_message_feed(&message,(uint8_t)control,final,payload,size,1);
        if(!final || size>125 || (control==8 && size==1)) expect(result,WEBSOCKET_MESSAGE_ERROR,1002);
        else if(control==8) {
            expect(result,WEBSOCKET_MESSAGE_CLOSE,size?1000:0);
            assert(!message.active && message.close_received);
        } else {
            expect(result,control==9?WEBSOCKET_MESSAGE_PING:WEBSOCKET_MESSAGE_PONG,0);
            assert(result.data==payload && result.size==size && message.active && message.used==1 && buffer[0]=='a');
            result=websocket_message_feed(&message,0,true,(const uint8_t *)"b",1,2);
            expect(result,WEBSOCKET_MESSAGE_TEXT,0); assert(result.size==2 && !memcmp(result.data,"ab",2));
        }
        ++protocol_cases;
    }
    for(unsigned replacement=1;replacement<=2;++replacement) {
        websocket_message_t message=initialized(buffer,sizeof(buffer),100);
        expect(websocket_message_feed(&message,1,false,NULL,0,0),WEBSOCKET_MESSAGE_NONE,0);
        expect(websocket_message_feed(&message,(uint8_t)replacement,true,NULL,0,1),WEBSOCKET_MESSAGE_ERROR,1002);
        expect(websocket_message_feed(&message,0,true,NULL,0,2),WEBSOCKET_MESSAGE_ERROR,1002); ++protocol_cases;
    }
    for(unsigned opcode=1;opcode<=2;++opcode) {
        websocket_message_t message=initialized(buffer,sizeof(buffer),100);
        expect(websocket_message_feed(&message,(uint8_t)opcode,false,NULL,0,0),WEBSOCKET_MESSAGE_NONE,0);
        for(unsigned i=1;i<=20;++i) expect(websocket_message_feed(&message,0,false,NULL,0,i),WEBSOCKET_MESSAGE_NONE,0);
        websocket_message_result_t result=websocket_message_feed(&message,0,true,NULL,0,21);
        expect(result,opcode==1?WEBSOCKET_MESSAGE_TEXT:WEBSOCKET_MESSAGE_BINARY,0); assert(!result.size); ++protocol_cases;
    }
    static const uint8_t multicode[]={0,0x7f,0xc2,0x80,0xe0,0xa0,0x80,0xef,0xbf,0xbf,0xf0,0x90,0x80,0x80,0xf4,0x8f,0xbf,0xbf};
    websocket_message_t message=initialized(buffer,sizeof(buffer),1000);
    for(size_t i=0;i<sizeof(multicode);++i) {
        websocket_message_result_t result=websocket_message_feed(&message,i?0:1,i+1==sizeof(multicode),multicode+i,1,i*3);
        expect(result,i+1==sizeof(multicode)?WEBSOCKET_MESSAGE_TEXT:WEBSOCKET_MESSAGE_NONE,0);
        if(i+1<sizeof(multicode)) {
            expect(websocket_message_feed(&message,9,true,payload,125,i*3+1),WEBSOCKET_MESSAGE_PING,0);
            expect(websocket_message_feed(&message,10,true,payload,125,i*3+2),WEBSOCKET_MESSAGE_PONG,0);
        } else assert(result.size==sizeof(multicode) && !memcmp(result.data,multicode,sizeof(multicode)));
    }
    ++protocol_cases;
}

static void test_close_codes_and_reasons(void) {
    uint8_t buffer[16], close[126];
    for(uint32_t code=0;code<=65535;++code) {
        // Independent small table/ranges based on IANA, not production helper.
        static const uint16_t standard[]={1000,1001,1002,1003,1007,1008,1009,1010,1011,1012,1013,1014};
        bool valid=code>=3000 && code<5000;
        for(size_t i=0;i<sizeof(standard)/sizeof(*standard);++i) if(code==standard[i]) valid=true;
        assert(websocket_message_close_code_valid((uint16_t)code)==valid);
        close[0]=(uint8_t)(code/256); close[1]=(uint8_t)(code%256);
        websocket_message_t message=initialized(buffer,sizeof(buffer),100);
        websocket_message_result_t result=websocket_message_feed(&message,8,true,close,2,0);
        expect(result,valid?WEBSOCKET_MESSAGE_CLOSE:WEBSOCKET_MESSAGE_ERROR,valid?(uint16_t)code:1002);
        ++close_codes;
    }
    const uint8_t malformed[][6]={{0xc0,0x80},{0xed,0xa0,0x80},{0xf4,0x90,0x80,0x80},{0xe2,0x82},{0xff}};
    const size_t lengths[]={2,3,4,2,1};
    for(size_t i=0;i<sizeof(lengths)/sizeof(*lengths);++i) {
        close[0]=3; close[1]=0xe8; memcpy(close+2,malformed[i],lengths[i]);
        websocket_message_t message=initialized(buffer,sizeof(buffer),100);
        expect(websocket_message_feed(&message,8,true,close,lengths[i]+2,0),WEBSOCKET_MESSAGE_ERROR,1007); ++protocol_cases;
    }
    for(unsigned closing=0;closing<2;++closing) for(unsigned opcode=0;opcode<=10;++opcode) {
        websocket_message_t message=initialized(buffer,sizeof(buffer),100);
        expect(websocket_message_feed(&message,1,false,(const uint8_t *)"a",1,0),WEBSOCKET_MESSAGE_NONE,0);
        if(closing) expect(websocket_message_feed(&message,8,true,NULL,0,1),WEBSOCKET_MESSAGE_CLOSE,0);
        else websocket_message_mark_close_sent(&message);
        websocket_message_result_t result=websocket_message_feed(&message,(uint8_t)opcode,true,NULL,0,2);
        if(opcode==8) expect(result,WEBSOCKET_MESSAGE_CLOSE,0);
        else if(opcode==9 || opcode==10)
            expect(result,closing?WEBSOCKET_MESSAGE_NONE:
                   (opcode==9?WEBSOCKET_MESSAGE_PING:WEBSOCKET_MESSAGE_PONG),0);
        else expect(result,WEBSOCKET_MESSAGE_ERROR,1002);
        assert(!message.active); ++protocol_cases;
    }
}

static void check_canaries(const uint8_t *allocation,size_t capacity) {
    for(unsigned i=0;i<8;++i) assert(allocation[i]==0xa5 && allocation[8+capacity+i]==0xa5);
}
static void test_limits_and_initialization(void) {
    uint8_t payload[300]; memset(payload,'a',sizeof(payload));
    const size_t capacities[]={1,2,4,97,256};
    for(size_t k=0;k<sizeof(capacities)/sizeof(*capacities);++k) {
        size_t capacity=capacities[k]; uint8_t *allocation=malloc(capacity+16); assert(allocation);
        for(size_t total=0;total<=capacity+1;++total) for(size_t split=0;split<=total;++split) {
            memset(allocation,0xa5,capacity+16);
            websocket_message_t message=initialized(allocation+8,capacity,100);
            websocket_message_result_t first=websocket_message_feed(&message,1,false,payload,split,0);
            websocket_message_result_t result=websocket_message_feed(&message,0,true,payload+split,total-split,1);
            if(total<capacity) {
                expect(first,WEBSOCKET_MESSAGE_NONE,0); expect(result,WEBSOCKET_MESSAGE_TEXT,0);
                assert(result.size==total && !memcmp(result.data,payload,total) && !result.data[total]);
            } else expect(result,WEBSOCKET_MESSAGE_ERROR,1009);
            check_canaries(allocation,capacity); ++limit_cases;
        }
        memset(allocation,0xa5,capacity+16); websocket_message_t message=initialized(allocation+8,capacity,100);
        expect(websocket_message_feed(&message,2,true,payload,SIZE_MAX,0),WEBSOCKET_MESSAGE_ERROR,1009);
        check_canaries(allocation,capacity); ++limit_cases; free(allocation);
    }
    websocket_message_t invalid; uint8_t buffer[16];
    assert(!websocket_message_init(NULL,buffer,sizeof(buffer),1));
    assert(!websocket_message_init(&invalid,NULL,sizeof(buffer),1));
    expect(websocket_message_expire(&invalid,0),WEBSOCKET_MESSAGE_ERROR,1002);
    assert(!websocket_message_init(&invalid,buffer,0,1));
    assert(!websocket_message_init(&invalid,buffer,sizeof(buffer),0));
    assert(!websocket_message_init(&invalid,buffer,sizeof(buffer),(uint64_t)INT64_MAX+1U));
    websocket_message_t message=initialized(buffer,sizeof(buffer),1);
    expect(websocket_message_feed(&message,1,true,NULL,1,0),WEBSOCKET_MESSAGE_ERROR,1002);
    expect(websocket_message_feed(NULL,1,true,NULL,0,0),WEBSOCKET_MESSAGE_ERROR,1002);
    websocket_message_mark_close_sent(NULL); ++limit_cases;
}

static void test_deadlines_and_independence(void) {
    uint8_t buffer[16];
    const uint64_t starts[]={0,(uint64_t)INT64_MAX-5,(uint64_t)INT64_MAX,(uint64_t)INT64_MAX+1,UINT64_MAX-5,UINT64_MAX};
    const uint64_t budgets[]={1,10,1000000,(uint64_t)INT64_MAX};
    for(size_t i=0;i<sizeof(starts)/sizeof(*starts);++i) for(size_t j=0;j<sizeof(budgets)/sizeof(*budgets);++j) {
        uint64_t start=starts[i], budget=budgets[j];
        websocket_message_t message=initialized(buffer,sizeof(buffer),budget);
        expect(websocket_message_feed(&message,1,false,NULL,0,start),WEBSOCKET_MESSAGE_NONE,0);
        expect(websocket_message_expire(&message,start+budget-1),WEBSOCKET_MESSAGE_NONE,0);
        expect(websocket_message_expire(&message,start+budget),WEBSOCKET_MESSAGE_ERROR,1008);
        expect(websocket_message_expire(&message,start+budget+1),WEBSOCKET_MESSAGE_ERROR,1008);
        expect(websocket_message_feed(&message,0,true,NULL,0,start+budget+2),WEBSOCKET_MESSAGE_ERROR,1008); ++timeout_cases;
    }
    websocket_message_t message=initialized(buffer,sizeof(buffer),10);
    expect(websocket_message_feed(&message,1,false,NULL,0,1),WEBSOCKET_MESSAGE_NONE,0);
    expect(websocket_message_feed(&message,0,false,NULL,0,8),WEBSOCKET_MESSAGE_NONE,0);
    expect(websocket_message_feed(&message,9,true,NULL,0,10),WEBSOCKET_MESSAGE_PING,0);
    expect(websocket_message_feed(&message,0,true,NULL,0,11),WEBSOCKET_MESSAGE_ERROR,1008); ++timeout_cases;
    message=initialized(buffer,sizeof(buffer),10);
    expect(websocket_message_feed(&message,1,true,NULL,0,0),WEBSOCKET_MESSAGE_TEXT,0);
    expect(websocket_message_expire(&message,UINT64_MAX),WEBSOCKET_MESSAGE_NONE,0); ++timeout_cases;
    uint8_t other_buffer[16]; websocket_message_t other=initialized(other_buffer,sizeof(other_buffer),10);
    message=initialized(buffer,sizeof(buffer),100);
    expect(websocket_message_feed(&message,1,false,(const uint8_t *)"a",1,0),WEBSOCKET_MESSAGE_NONE,0);
    expect(websocket_message_feed(&other,2,false,(const uint8_t *)"b",1,0),WEBSOCKET_MESSAGE_NONE,0);
    websocket_message_mark_close_sent(&other);
    websocket_message_result_t result=websocket_message_feed(&message,0,true,(const uint8_t *)"c",1,1);
    expect(result,WEBSOCKET_MESSAGE_TEXT,0); assert(result.size==2 && !memcmp(result.data,"ac",2));
    expect(websocket_message_feed(&other,0,true,NULL,0,1),WEBSOCKET_MESSAGE_ERROR,1002); ++timeout_cases;
}

int main(void) {
    test_scalars_and_splits(); test_utf8_invalid_and_oracle(); test_state_and_control();
    test_close_codes_and_reasons(); test_limits_and_initialization(); test_deadlines_and_independence();
    printf("{\"passed\":true,\"unicode_scalars\":%"PRIu64",\"scalar_splits\":%"PRIu64",\"utf8_oracles\":%"PRIu64",\"protocol_cases\":%"PRIu64",\"close_codes\":%"PRIu64",\"limit_cases\":%"PRIu64",\"timeout_cases\":%"PRIu64",\"state_bytes\":%zu}\n",
        scalars,split_cases,utf8_oracles,protocol_cases,close_codes,limit_cases,timeout_cases,sizeof(websocket_message_t));
    return 0;
}
