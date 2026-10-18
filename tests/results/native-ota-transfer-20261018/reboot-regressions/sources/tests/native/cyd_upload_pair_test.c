#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <setjmp.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

static const char *ta="/spiffs/a.tmp",*la="/spiffs/a",*ba="/spiffs/a.bak";
static const char *tb="/spiffs/b.tmp",*lb="/spiffs/b",*bb="/spiffs/b.bak";
static char root[768];
static unsigned step,fail_at,crash_at,scenarios,ordinary_failures,cleanups,interruptions;
static bool fail_second_install,fail_restore_a,fail_restore_b,fail_remove_new;
static jmp_buf crash_exit;
static void path(const char *name,char *out,size_t cap){assert(!strncmp(name,"/spiffs/",8));int size=snprintf(out,cap,"%s/%s",root,name+8);assert(size>0&&(size_t)size<cap);}
static bool before(void){++step;if(step==fail_at){errno=EIO;return false;}return true;}
static void after(void){if(step==crash_at)longjmp(crash_exit,1);}
static int mapped_stat(const char *name,struct stat *info){if(!before())return -1;char out[1024];path(name,out,sizeof(out));int result=stat(out,info);int saved=errno;after();errno=saved;return result;}
static int mapped_remove(const char *name){if(!before())return -1;if(fail_remove_new&&!strcmp(name,la)){errno=EIO;return -1;}char out[1024];path(name,out,sizeof(out));int result=remove(out);int saved=errno;after();errno=saved;return result;}
static int mapped_rename(const char *from,const char *to){if(!before())return -1;if((fail_second_install&&!strcmp(from,tb))||(fail_restore_a&&!strcmp(from,ba))||(fail_restore_b&&!strcmp(from,bb))){errno=EIO;return -1;}char source[1024],target[1024];path(from,source,sizeof(source));path(to,target,sizeof(target));if(!access(target,F_OK)){errno=EEXIST;return -1;}int result=rename(source,target);int saved=errno;after();errno=saved;return result;}
#define stat(...) mapped_stat(__VA_ARGS__)
#define remove(...) mapped_remove(__VA_ARGS__)
#define rename(...) mapped_rename(__VA_ARGS__)
#include "file_transaction.c"
#undef rename
#undef remove
#undef stat
static void text(const char *name,const char *value){char out[1024];path(name,out,sizeof(out));FILE *file=fopen(out,"wb");assert(file&&fwrite(value,1,strlen(value),file)==strlen(value)&&!fclose(file));}
static bool equals(const char *name,const char *value){char out[1024],content[32];path(name,out,sizeof(out));FILE *file=fopen(out,"rb");if(!file)return false;size_t size=fread(content,1,sizeof(content),file);assert(!ferror(file)&&!fclose(file));return size==strlen(value)&&!memcmp(content,value,size);}
static bool exists(const char *name){char out[1024];path(name,out,sizeof(out));return !access(out,F_OK);}
static void reset(unsigned mask){const char *names[]={ta,la,ba,tb,lb,bb};step=fail_at=crash_at=0;fail_second_install=fail_restore_a=fail_restore_b=fail_remove_new=false;for(size_t i=0;i<6;++i){char out[1024];path(names[i],out,sizeof(out));remove(out);}if(mask&1)text(la,"A-old");if(mask&2)text(lb,"B-old");text(ta,"A-new");text(tb,"B-new");++scenarios;}
static bool replace(void){return native_file_replace_pair(ta,la,ba,tb,lb,bb);}
static void assert_old(unsigned mask){assert((mask&1)?equals(la,"A-old"):!exists(la));assert((mask&2)?equals(lb,"B-old"):!exists(lb));}
int main(int argc,char **argv){assert(argc==2&&strlen(argv[1])<sizeof(root));strcpy(root,argv[1]);
    for(unsigned mask=0;mask<4;++mask){reset(mask);assert(replace()&&equals(la,"A-new")&&equals(lb,"B-new"));unsigned operations=step;
        for(unsigned failure=1;failure<=operations;++failure){reset(mask);fail_at=failure;bool ok=replace();if(ok){assert(equals(la,"A-new")&&equals(lb,"B-new"));++cleanups;}else{assert_old(mask);assert(!exists(ba)&&!exists(bb));++ordinary_failures;}}
    }
    const char *valid[]={ta,la,ba,tb,lb,bb};
    for(size_t i=0;i<6;++i){for(unsigned variant=0;variant<2;++variant){reset(3);const char *paths[6];memcpy(paths,valid,sizeof(paths));paths[i]=variant?"":NULL;assert(!native_file_replace_pair(paths[0],paths[1],paths[2],paths[3],paths[4],paths[5])&&!step);assert_old(3);}
        for(size_t j=0;j<i;++j){reset(3);const char *paths[6];memcpy(paths,valid,sizeof(paths));paths[i]=paths[j];assert(!native_file_replace_pair(paths[0],paths[1],paths[2],paths[3],paths[4],paths[5])&&!step);assert_old(3);}}
    reset(3);char out[1024];path(ta,out,sizeof(out));assert(!remove(out));assert(!replace());assert_old(3);
    reset(3);path(tb,out,sizeof(out));assert(!remove(out));assert(!replace());assert_old(3);
    reset(3);text(ba,"A-stale");text(bb,"B-stale");assert(replace()&&equals(la,"A-new")&&equals(lb,"B-new")&&!exists(ba)&&!exists(bb));
    reset(0);text(ba,"A-old");text(bb,"B-old");assert(replace()&&equals(la,"A-new")&&equals(lb,"B-new"));
    for(unsigned failures=1;failures<8;++failures){reset(3);fail_second_install=true;fail_restore_a=(failures&1)!=0;fail_restore_b=(failures&2)!=0;fail_remove_new=(failures&4)!=0;assert(!replace());assert(equals(la,"A-old")||equals(ba,"A-old"));assert(equals(lb,"B-old")||equals(bb,"B-old"));fail_second_install=fail_restore_a=fail_restore_b=fail_remove_new=false;assert(native_file_recover(la,ba)&&native_file_recover(lb,bb));assert(exists(la)&&exists(lb));}
    reset(3);assert(replace());unsigned operations=step;bool mixed_observed=false;
    for(unsigned interruption=1;interruption<=operations;++interruption){reset(3);crash_at=interruption;if(!setjmp(crash_exit))replace();crash_at=0;++interruptions;
        // Recover each absent live independently. A new CSV beside an old
        // index is possible and must be rejected/rebuilt by catalog metadata.
        assert(native_file_recover(la,ba)&&native_file_recover(lb,bb));bool old_a=equals(la,"A-old"),new_a=equals(la,"A-new"),old_b=equals(lb,"B-old"),new_b=equals(lb,"B-new");assert((old_a||new_a)&&(old_b||new_b));if(old_a!=old_b)mixed_observed=true;
    }
    assert(mixed_observed&&ordinary_failures&&cleanups);
    printf("PASS CYD file pairs: %u scenarios, %u ordinary injected failures preserve both old files, %u committed cleanup failures, %u interruption states; six-name validation, empty/missing/stale files, rollback backups retained; mixed crash generation explicitly requires catalog validation\n",scenarios,ordinary_failures,cleanups,interruptions);
    return 0;}
