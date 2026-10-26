/* Independent metadata API semantics and atomic allocation refusal.
   This fixture does not initialize DSP, decode audio or change scheduling. */
#include <assert.h>
#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "vorbis/codec.h"
#include "native_vorbis_xiph_comment_error.h"
#include "vorbis_xiph_alloc.h"

#define CHECK(x) do { int ok=!!(x); assert(ok); if(!ok)abort(); } while(0)
enum { MAX_ROWS=16, MAX_BYTES=96 };
static const uint64_t GUARD=UINT64_C(0xd10c9a7348f2b65e);
static int scenarios;
static const unsigned char binary_comment[]={'B','I','N','=','a',0,'b',0};
static const unsigned char high_comment[]={'X',0xc3,0xa9,'=','h','i','g','h',0};
static const unsigned char high_tag[]={'x',0xc3,0xa9,0};
static const unsigned char other_high_tag[]={'x',0xc3,0x89,0};
static const char *const ordinary[]={
  "ARTIST=alpha","artist=beta","ARTISTX=prefix","ART=short",
  "no separator","=empty-tag","EMPTY="
};
typedef struct {
  vorbis_comment object;
  size_t live,bytes;
  char *pointers[MAX_ROWS+1];
  int lengths[MAX_ROWS+1];
  unsigned char contents[MAX_ROWS][MAX_BYTES];
  unsigned char vendor[MAX_BYTES];
  size_t vendor_bytes;
} snapshot_t;
typedef struct { uint64_t before;char bytes[MAX_BYTES];uint64_t after; } text_t;

static void no_owners(void){CHECK(xiph_port_test_live()==0 && xiph_port_test_bytes()==0);}
static void *owned(size_t size){void *result=xiph_port_test_malloc(size);CHECK(result);return result;}
static char *owned_bytes(const unsigned char *data,size_t length){
  char *result=owned(length+1);memcpy(result,data,length);result[length]=0;return result;
}
static void state_create(vorbis_comment *vc,int shape){
  no_owners();xiph_port_test_reset(0);vorbis_comment_init(vc);CHECK(shape>=0 && shape<=2);
  if(shape==0)return;
  vc->vendor=owned_bytes((const unsigned char *)"Fixture vendor",14);
  vc->comments=shape==2?9:0;
  vc->user_comments=owned(((size_t)vc->comments+1)*sizeof(*vc->user_comments));
  vc->comment_lengths=owned(((size_t)vc->comments+1)*sizeof(*vc->comment_lengths));
  memset(vc->user_comments,0,((size_t)vc->comments+1)*sizeof(*vc->user_comments));
  memset(vc->comment_lengths,0,((size_t)vc->comments+1)*sizeof(*vc->comment_lengths));
  for(int i=0;i<vc->comments;i++){
    const unsigned char *data;
    size_t length;
    if(i<7){data=(const unsigned char *)ordinary[i];length=strlen(ordinary[i]);}
    else if(i==7){data=high_comment;length=sizeof(high_comment)-1;}
    else{data=binary_comment;length=sizeof(binary_comment)-1;}
    CHECK(length<MAX_BYTES);
    vc->user_comments[i]=owned_bytes(data,length);vc->comment_lengths[i]=(int)length;
  }
}
static void state_clear(vorbis_comment *vc){
  vorbis_comment_clear(vc);no_owners();
  const unsigned char *raw=(const unsigned char *)vc;
  for(size_t i=0;i<sizeof(*vc);i++)CHECK(raw[i]==0);
  vorbis_comment_clear(vc);no_owners();
}
static void take_snapshot(const vorbis_comment *vc,snapshot_t *saved){
  memset(saved,0,sizeof(*saved));memcpy(&saved->object,vc,sizeof(*vc));
  saved->live=xiph_port_test_live();saved->bytes=xiph_port_test_bytes();
  CHECK(vc->comments>=0 && vc->comments<=MAX_ROWS);
  if(vc->user_comments)memcpy(saved->pointers,vc->user_comments,((size_t)vc->comments+1)*sizeof(*vc->user_comments));
  if(vc->comment_lengths)memcpy(saved->lengths,vc->comment_lengths,((size_t)vc->comments+1)*sizeof(*vc->comment_lengths));
  for(int i=0;i<vc->comments;i++){
    CHECK(vc->comment_lengths[i]>=0 && vc->comment_lengths[i]<MAX_BYTES);
    memcpy(saved->contents[i],vc->user_comments[i],(size_t)vc->comment_lengths[i]+1);
  }
  if(vc->vendor){saved->vendor_bytes=strlen(vc->vendor)+1;CHECK(saved->vendor_bytes<=MAX_BYTES);memcpy(saved->vendor,vc->vendor,saved->vendor_bytes);}
}
static void old_strings_unchanged(const vorbis_comment *vc,const snapshot_t *saved){
  CHECK(vc->vendor==saved->object.vendor);
  if(saved->vendor_bytes)CHECK(memcmp(vc->vendor,saved->vendor,saved->vendor_bytes)==0);
  for(int i=0;i<saved->object.comments;i++){
    CHECK(vc->user_comments[i]==saved->pointers[i] && vc->comment_lengths[i]==saved->lengths[i]);
    CHECK(memcmp(vc->user_comments[i],saved->contents[i],(size_t)saved->lengths[i]+1)==0);
  }
}
static void state_unchanged(const vorbis_comment *vc,const snapshot_t *saved){
  CHECK(memcmp(vc,&saved->object,sizeof(*vc))==0);
  CHECK(xiph_port_test_live()==saved->live && xiph_port_test_bytes()==saved->bytes);
  if(vc->user_comments)CHECK(memcmp(vc->user_comments,saved->pointers,((size_t)vc->comments+1)*sizeof(*vc->user_comments))==0);
  if(vc->comment_lengths)CHECK(memcmp(vc->comment_lengths,saved->lengths,((size_t)vc->comments+1)*sizeof(*vc->comment_lengths))==0);
  old_strings_unchanged(vc,saved);
}
static void text_set(text_t *text,const char *value){
  text->before=text->after=GUARD;memset(text->bytes,0xa5,sizeof(text->bytes));
  CHECK(strlen(value)<sizeof(text->bytes));memcpy(text->bytes,value,strlen(value)+1);
}
static void text_unchanged(const text_t *actual,const text_t *saved){
  CHECK(actual->before==GUARD && actual->after==GUARD);
  CHECK(memcmp(actual->bytes,saved->bytes,sizeof(actual->bytes))==0);
}
static int append_call(vorbis_comment *vc,int mode,const char *raw,const char *tag,const char *value){
  CHECK(mode>=0 && mode<4);
  if(mode==0)return native_xiph_comment_add(vc,raw);
  if(mode==1)return native_xiph_comment_add_tag(vc,tag,value);
  if(mode==2)vorbis_comment_add(vc,raw);else vorbis_comment_add_tag(vc,tag,value);
  return 0;
}
static void appended(const vorbis_comment *vc,const snapshot_t *saved,const char *expected){
  int slot=saved->object.comments;
  CHECK(vc->comments==slot+1 && vc->user_comments && vc->comment_lengths);
  CHECK(vc->user_comments[slot]!=NULL && vc->user_comments[slot+1]==NULL);
  CHECK(vc->comment_lengths[slot]==(int)strlen(expected));
  CHECK(strcmp(vc->user_comments[slot],expected)==0);
  old_strings_unchanged(vc,saved);
}
static void insertion_sweep(void){
  for(int shape=0;shape<3;shape++)for(int mode=0;mode<4;mode++)for(int zero=0;zero<2;zero++){
    for(size_t ordinal=0;ordinal<=3;ordinal++){
      vorbis_comment vc;state_create(&vc,shape);snapshot_t saved;take_snapshot(&vc,&saved);
      text_t raw,tag,value;text_set(&raw,"RETRY=gamma");text_set(&tag,"RETRY");text_set(&value,"gamma");
      text_t before_raw=raw,before_tag=tag,before_value=value;
      xiph_port_test_reset(ordinal);xiph_port_test_zero_null(zero);
      int status=append_call(&vc,mode,raw.bytes,tag.bytes,value.bytes);
      CHECK(xiph_port_test_attempts()==(ordinal?ordinal:3U));
      CHECK(xiph_port_test_failures()==(ordinal?1U:0U) && xiph_port_test_realloc_attempts()==0);
      text_unchanged(&raw,&before_raw);text_unchanged(&tag,&before_tag);text_unchanged(&value,&before_value);
      if(ordinal){if(mode<2)CHECK(status==OV_EFAULT);state_unchanged(&vc,&saved);}
      else{CHECK(status==0);appended(&vc,&saved,"RETRY=gamma");}
      scenarios++;
      if(ordinal){
        xiph_port_test_reset(0);xiph_port_test_zero_null(zero);
        CHECK(append_call(&vc,mode,raw.bytes,tag.bytes,value.bytes)==0);
        CHECK(xiph_port_test_attempts()==3 && xiph_port_test_failures()==0 && xiph_port_test_realloc_attempts()==0);
        appended(&vc,&saved,"RETRY=gamma");scenarios++;
      }
      /* Arguments are copied; later caller writes must not change storage. */
      memset(raw.bytes,'!',sizeof(raw.bytes));memset(tag.bytes,'!',sizeof(tag.bytes));memset(value.bytes,'!',sizeof(value.bytes));
      CHECK(strcmp(vc.user_comments[vc.comments-1],"RETRY=gamma")==0);
      char *borrowed=vc.user_comments[vc.comments-1]+6;
      xiph_port_test_reset(1);CHECK(vorbis_comment_query_count(&vc,"retry")==1);
      CHECK(vorbis_comment_query(&vc,"ReTrY",0)==borrowed && strcmp(borrowed,"gamma")==0);
      CHECK(xiph_port_test_attempts()==0 && xiph_port_test_failures()==0);
      state_clear(&vc);
    }
  }
}
static void query_matrix(void){
  static const struct {const char *tag;int count,first,second,offset;} cases[]={
    {"artist",2,0,1,7},{"ARTISTX",1,2,-1,8},{"aRt",1,3,-1,4},
    {"ARTIS",0,-1,-1,0},{"ARTISTXY",0,-1,-1,0},{"no separator",0,-1,-1,0},
    {"",1,5,-1,1},{"EMPTY",1,6,-1,6},{"BIN",1,8,-1,4},
    {"missing",0,-1,-1,0},{"ARTIST=alpha",0,-1,-1,0}
  };
  for(int shape=0;shape<3;shape++){
    vorbis_comment vc;state_create(&vc,shape);snapshot_t saved;take_snapshot(&vc,&saved);xiph_port_test_reset(1);
    for(unsigned c=0;c<sizeof(cases)/sizeof(*cases);c++){
      int count=shape==2?cases[c].count:0;
      CHECK(vorbis_comment_query_count(&vc,cases[c].tag)==count);
      for(int index=-1;index<=count+1;index++){
        char *expected=NULL;
        if(index>=0 && index<count)expected=vc.user_comments[index?cases[c].second:cases[c].first]+cases[c].offset;
        CHECK(vorbis_comment_query(&vc,cases[c].tag,index)==expected);scenarios++;
      }
      CHECK(vorbis_comment_query(&vc,cases[c].tag,INT_MAX)==NULL);scenarios++;
    }
    CHECK(vorbis_comment_query_count(&vc,(const char *)high_tag)==(shape==2?1:0));
    CHECK(vorbis_comment_query_count(&vc,(const char *)other_high_tag)==0);
    CHECK(vorbis_comment_query(&vc,(const char *)high_tag,0)==(shape==2?vc.user_comments[7]+4:NULL));
    CHECK(vorbis_comment_query(&vc,(const char *)other_high_tag,0)==NULL);scenarios++;
    CHECK(xiph_port_test_attempts()==0 && xiph_port_test_failures()==0 && xiph_port_test_realloc_attempts()==0);
    state_unchanged(&vc,&saved);
    /* Allocation-free lookup must leave the first refusal armed. */
    CHECK(native_xiph_comment_add(&vc,"AFTER_QUERY=refused")==OV_EFAULT);
    CHECK(xiph_port_test_attempts()==1 && xiph_port_test_failures()==1 && xiph_port_test_realloc_attempts()==0);
    state_unchanged(&vc,&saved);scenarios++;
    xiph_port_test_reset(0);state_clear(&vc);
  }
}
static void alias_sweep(void){
  for(int mode=0;mode<4;mode++)for(size_t ordinal=0;ordinal<=3;ordinal++){
    vorbis_comment vc;state_create(&vc,2);snapshot_t saved;take_snapshot(&vc,&saved);
    char *value=vorbis_comment_query(&vc,"ARTIST",0),*tag=vorbis_comment_query(&vc,"ART",0);
    CHECK(value==vc.user_comments[0]+7 && tag==vc.user_comments[3]+4);
    const char *expected=(mode==0 || mode==2)?"alpha":"short=alpha";
    xiph_port_test_reset(ordinal);int status=append_call(&vc,mode,value,tag,value);
    CHECK(xiph_port_test_attempts()==(ordinal?ordinal:3U) && xiph_port_test_failures()==(ordinal?1U:0U));
    if(ordinal){if(mode<2)CHECK(status==OV_EFAULT);state_unchanged(&vc,&saved);}
    else{CHECK(status==0);appended(&vc,&saved,expected);}
    scenarios++;
    if(ordinal){
      xiph_port_test_reset(0);CHECK(append_call(&vc,mode,value,tag,value)==0);
      CHECK(xiph_port_test_attempts()==3 && xiph_port_test_failures()==0);appended(&vc,&saved,expected);scenarios++;
    }
    xiph_port_test_reset(1);CHECK(vorbis_comment_query(&vc,"artist",0)==value);
    CHECK(strcmp(value,"alpha")==0 && strcmp(tag,"short")==0);
    CHECK(memcmp(vc.user_comments[8],binary_comment,sizeof(binary_comment))==0);
    CHECK(xiph_port_test_attempts()==0 && xiph_port_test_failures()==0);state_clear(&vc);
  }
}
static void literal_controls(void){
  static const struct {const char *raw,*tag,*value,*expected;} cases[]={
    {"","","","="},{"plain","KEY","","KEY="},
    {"=raw","","value","=value"},{"A=B=C","A=B","C=D","A=B=C=D"},
    {"x\xc3\xa9=raw","X\xc3\xa9","v\xc3\xa9","X\xc3\xa9=v\xc3\xa9"}
  };
  for(unsigned c=0;c<sizeof(cases)/sizeof(*cases);c++)for(int mode=0;mode<4;mode++){
    vorbis_comment vc;state_create(&vc,0);xiph_port_test_reset(0);
    CHECK(append_call(&vc,mode,cases[c].raw,cases[c].tag,cases[c].value)==0);
    const char *expected=(mode==0 || mode==2)?cases[c].raw:cases[c].expected;
    CHECK(vc.comments==1 && vc.comment_lengths[0]==(int)strlen(expected));
    CHECK(strcmp(vc.user_comments[0],expected)==0 && vc.user_comments[1]==NULL);
    CHECK(xiph_port_test_attempts()==3 && xiph_port_test_failures()==0 && xiph_port_test_realloc_attempts()==0);
    if(mode==1 || mode==3){
      xiph_port_test_reset(1);
      CHECK(vorbis_comment_query_count(&vc,cases[c].tag)==1);
      CHECK(vorbis_comment_query(&vc,cases[c].tag,0)==vc.user_comments[0]+strlen(cases[c].tag)+1);
      CHECK(strcmp(vorbis_comment_query(&vc,cases[c].tag,0),cases[c].value)==0);
      CHECK(vorbis_comment_query(&vc,cases[c].tag,1)==NULL);
      CHECK(xiph_port_test_attempts()==0 && xiph_port_test_failures()==0 && xiph_port_test_realloc_attempts()==0);
    }
    state_clear(&vc);scenarios++;
  }
}
static void progressive_controls(void){
  vorbis_comment vc;state_create(&vc,1);char *first=NULL;
  static const char digits[]="0123456789abcdef";
  for(int item=0;item<32;item++){
    char value[3]={digits[item/16],digits[item%16],0};xiph_port_test_reset(0);
    if(item%2)vorbis_comment_add_tag(&vc,"dup",value);
    else CHECK(native_xiph_comment_add_tag(&vc,"dup",value)==0);
    CHECK(vc.comments==item+1 && xiph_port_test_attempts()==3 && xiph_port_test_failures()==0);
    value[0]=value[1]='!';
    xiph_port_test_reset(1);CHECK(vorbis_comment_query_count(&vc,"DUP")==item+1);
    for(int index=0;index<=item;index++){
      char expected[3]={digits[index/16],digits[index%16],0};char *found=vorbis_comment_query(&vc,"DuP",index);
      CHECK(found==vc.user_comments[index]+4 && strcmp(found,expected)==0);
    }
    if(!first)first=vorbis_comment_query(&vc,"dup",0);
    CHECK(vorbis_comment_query(&vc,"dup",0)==first && !strcmp(first,"00"));
    CHECK(vorbis_comment_query(&vc,"dup",item+1)==NULL);
    CHECK(xiph_port_test_attempts()==0 && xiph_port_test_failures()==0);scenarios++;
  }
  state_clear(&vc);
  vorbis_comment_init(&vc);xiph_port_test_reset(0);CHECK(native_xiph_comment_add(&vc,"REINIT=ok")==0);
  CHECK(vorbis_comment_query_count(&vc,"reinit")==1 && !strcmp(vorbis_comment_query(&vc,"REINIT",0),"ok"));
  state_clear(&vc);scenarios++;
}
static void invalid_controls(void){
  vorbis_comment vc;vorbis_comment_init(&vc);vorbis_comment saved;
  static const int counts[]={-1,INT_MAX};
  for(unsigned c=0;c<sizeof(counts)/sizeof(*counts);c++){
    vc.comments=counts[c];memcpy(&saved,&vc,sizeof(vc));xiph_port_test_reset(1);
    CHECK(native_xiph_comment_add(&vc,"A=B")==OV_EINVAL);
    CHECK(native_xiph_comment_add_tag(&vc,"A","B")==OV_EINVAL);
    CHECK(memcmp(&vc,&saved,sizeof(vc))==0 && xiph_port_test_attempts()==0 && xiph_port_test_failures()==0);scenarios++;
  }
  /* Large metadata counts are refused before any huge allocation or copy.
     On LP64 the products fit, so the armed first allocation must refuse;
     on ESP32 the array products do not fit SIZE_MAX and need no allocation.
     The dummy arrays are never traversed or passed to comment_clear. */
  char *dummy_comments[1]={NULL};int dummy_lengths[1]={0};
  vorbis_comment_init(&vc);vc.comments=INT_MAX-1;
  vc.user_comments=dummy_comments;vc.comment_lengths=dummy_lengths;
  memcpy(&saved,&vc,sizeof(vc));
  size_t slots=(size_t)INT_MAX+1;
  int representable=slots<=SIZE_MAX/sizeof(*vc.user_comments) && slots<=SIZE_MAX/sizeof(*vc.comment_lengths);
  for(int tagged=0;tagged<2;tagged++){
    xiph_port_test_reset(1);
    int status=tagged?native_xiph_comment_add_tag(&vc,"A","B"):native_xiph_comment_add(&vc,"A=B");
    CHECK(status==(representable?OV_EFAULT:OV_EINVAL));
    CHECK(xiph_port_test_attempts()==(representable?1U:0U) && xiph_port_test_failures()==(representable?1U:0U));
    CHECK(xiph_port_test_realloc_attempts()==0 && memcmp(&vc,&saved,sizeof(vc))==0);
    CHECK(dummy_comments[0]==NULL && dummy_lengths[0]==0);no_owners();scenarios++;
  }
  vorbis_comment_init(&vc);memcpy(&saved,&vc,sizeof(vc));xiph_port_test_reset(1);
  CHECK(native_xiph_comment_add(NULL,"A=B")==OV_EINVAL);
  CHECK(native_xiph_comment_add(&vc,NULL)==OV_EINVAL);
  CHECK(native_xiph_comment_add_tag(NULL,"A","B")==OV_EINVAL);
  CHECK(native_xiph_comment_add_tag(&vc,NULL,"B")==OV_EINVAL);
  CHECK(native_xiph_comment_add_tag(&vc,"A",NULL)==OV_EINVAL);
  CHECK(memcmp(&vc,&saved,sizeof(vc))==0 && xiph_port_test_attempts()==0 && xiph_port_test_failures()==0);
  state_clear(&vc);scenarios++;
}
int xiph_comment_tests(void){
  scenarios=0;no_owners();query_matrix();insertion_sweep();alias_sweep();
  literal_controls();progressive_controls();invalid_controls();
  no_owners();xiph_port_test_reset(0);return scenarios;
}
