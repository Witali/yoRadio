#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "sources/idf/components/native_wifi_store/native_wifi_json.c"
static unsigned checks;
static void check_string(const char *input, bool expected) {
    struct { unsigned char before[8]; char out[5]; unsigned char after[8]; } guarded;
    memset(&guarded,0xa7,sizeof(guarded));
    reader_t reader={.at=(const uint8_t*)input,.end=(const uint8_t*)input+strlen(input)};
    assert(string(&reader,guarded.out,sizeof(guarded.out))==expected);
    for(size_t i=0;i<8;i++){assert(guarded.before[i]==0xa7);assert(guarded.after[i]==0xa7);}
    if(expected)assert(strlen(guarded.out)<sizeof(guarded.out));
    ++checks;
}
int main(void) {
    for (size_t capacity=0;capacity<=9;capacity++)for(size_t used=0;used<=16;used++)for(size_t count=0;count<=17;count++) {
        unsigned char data[32];memset(data,'x',sizeof(data));
        struct { unsigned char before[8]; char out[17]; unsigned char after[8]; } guarded;
        memset(&guarded,0xa7,sizeof(guarded));size_t actual=used;
        bool expected=used<capacity && count<capacity-used;
        assert(append(guarded.out,capacity,&actual,data,count)==expected);
        if(expected){assert(actual==used+count);assert(actual<capacity);assert(guarded.out[actual]==0);}
        else assert(actual==used);
        for(size_t i=0;i<8;i++){assert(guarded.before[i]==0xa7);assert(guarded.after[i]==0xa7);}
        ++checks;
    }
    for(size_t used=0;used<7;used++){
        char output[5]="abcd";size_t actual=used;
        assert(!append(output,5,&actual,(const uint8_t*)"",SIZE_MAX));assert(actual==used);++checks;
    }
    for(unsigned point=0;point<=0xffff;point++){
        char hex[8];snprintf(hex,sizeof(hex),"%04x",point);
        reader_t reader={.at=(const uint8_t*)hex,.end=(const uint8_t*)hex+4};uint32_t actual=UINT32_MAX;
        assert(hex4(&reader,&actual));assert(actual==point);assert(actual<=0xffff);++checks;
        for(unsigned prefix=0;prefix<=4;prefix++){
            char input[32];char *at=input;*at++='"';for(unsigned n=0;n<prefix;n++)*at++='x';
            snprintf(at,sizeof(input)-(size_t)(at-input),"\\u%04x\"",point);
            unsigned width=point<0x80?1:point<0x800?2:3;
            bool valid=point!=0 && !(point>=0xd800 && point<=0xdfff);
            check_string(input,valid && prefix+width<5);
        }
    }
    const unsigned lows[]={0xdc00,0xdc01,0xdffe,0xdfff};
    for(unsigned high=0xd800;high<=0xdbff;high++)for(unsigned j=0;j<4;j++)for(unsigned prefix=0;prefix<=4;prefix++){
        char input[40];char *at=input;*at++='"';for(unsigned n=0;n<prefix;n++)*at++='x';
        snprintf(at,sizeof(input)-(size_t)(at-input),"\\u%04x\\u%04x\"",high,lows[j]);
        check_string(input,prefix==0);
    }
    const char *raw[]={"\xc2\xa2","\xe2\x82\xac","\xf0\x9f\x98\x80"};
    const char *esc[]={"\\u007f","\\u0080","\\u07ff","\\u0800","\\uffff","\\ud800\\udc00","\\udbff\\udfff"};
    const unsigned widths[]={1,2,2,3,3,4,4};
    for(unsigned r=0;r<3;r++)for(unsigned e=0;e<7;e++){
        char input[64];snprintf(input,sizeof(input),"\"%s%s\"",raw[r],esc[e]);
        check_string(input,strlen(raw[r])+widths[e]<5);
    }
    printf("%u direct helper boundary checks passed; all BMP escapes and representative surrogate/raw UTF-8 boundaries; exact actual helper code\n",checks);
}
