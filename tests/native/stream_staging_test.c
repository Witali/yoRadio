#include "stream_confirm.h"
/* STAGING_HEADER */

enum { PAYLOAD = 2048, HEADER = 12, CAPACITY = PAYLOAD+HEADER,
       WINDOW = STREAM_STAGING_SLOTS*PAYLOAD+STREAM_STAGING_LOOKAHEAD };
static uint8_t expected[WINDOW], incoming[WINDOW], observed[WINDOW];
static atomic_bool reclaim_done;
static void *reclaim(void *opaque) {
    while (!atomic_load(&reclaim_done)) adaptive_input_release_one(opaque);
    return NULL;
}
static void compare(stream_staging_t *s, size_t bytes) {
    assert(stream_staging_size(s)==bytes);
    assert(stream_staging_read(s,0,observed,bytes));
    assert(!memcmp(observed,expected,bytes));
    assert(!stream_staging_read(s,bytes+1,observed,0));
    assert(!stream_staging_read(s,bytes,observed,1));
    assert(!stream_staging_erase(s,bytes,1));
}
static void corpus(const char *path) {
    FILE *file=fopen(path,"rb");assert(file);
    assert(!fseek(file,0,SEEK_END));long length=ftell(file);rewind(file);
    assert(length>0);uint8_t *data=malloc(length);assert(data);
    assert(fread(data,1,length,file)==(size_t)length);fclose(file);
    const size_t chunks[]={1,7,2048};
    for (unsigned i=0;i<3;++i) {
        adaptive_input_t *q=adaptive_input_create(4*CAPACITY,4*CAPACITY,CAPACITY);assert(q);
        stream_staging_t s={0};assert(stream_staging_init(&s,q,HEADER,PAYLOAD));
        atomic_store(&fail_after,0);
        size_t position=0,discarded=0,budget=4096;
        stream_confirm_info_t info;stream_confirm_result_t result;
        while (true) {
            size_t bytes=stream_staging_size(&s);
            result=stream_confirm_window(stream_staging_read,&s,bytes,
                position==(size_t)length,budget,STREAM_ID3_RUN_BYTES,&info);
            assert(info.discard<=budget);
            assert(stream_staging_erase(&s,0,info.discard));
            discarded+=info.discard;budget-=info.discard;
            if (result!=STREAM_CONFIRM_MORE) break;
            bytes=stream_staging_size(&s);assert(info.needed>bytes);
            size_t count=info.needed-bytes;
            if (count>chunks[i]) count=chunks[i];
            if (count>(size_t)length-position) count=(size_t)length-position;
            assert(count && stream_staging_append(&s,data+position,count)==count);
            position+=count;
        }
        assert(result==STREAM_CONFIRM_READY);
        size_t retained=stream_staging_size(&s);
        assert(retained==position-discarded && retained<=WINDOW);
        assert(stream_staging_read(&s,0,observed,retained));
        assert(!memcmp(observed,data+discarded,retained));
        printf("READY chunk=%zu codec=%u discard=%zu retained=%zu frame=%u single=%u\n",
            chunks[i],info.codec,discarded,retained,info.first_frame_bytes,info.single_frame_eof);
        stream_staging_cancel(&s);assert(!adaptive_input_stats(q).occupied);
        adaptive_input_destroy(q);assert(!atomic_load(&live_allocations));
        atomic_store(&fail_after,-1);
    }
    free(data);
}
int main(int argc,char **argv) {
    if (argc==2) {corpus(argv[1]);return 0;}
    assert(argc==1);
    for (size_t i=0; i<WINDOW; ++i) incoming[i]=(uint8_t)(i*17+i/251);
    adaptive_input_t *q=adaptive_input_create(4*CAPACITY,4*CAPACITY,CAPACITY);
    assert(q);
    stream_staging_t s={0};
    assert(!stream_staging_init(&s,q,HEADER,PAYLOAD+1));
    assert(stream_staging_init(&s,q,HEADER,PAYLOAD));
    // Startup window never allocates, including during all random operations.
    atomic_store(&fail_after,0);
    assert(stream_staging_append(&s,incoming,WINDOW)==WINDOW);
    assert(!stream_staging_append(&s,incoming,1));
    memcpy(expected,incoming,WINDOW);compare(&s,WINDOW);
    assert(adaptive_input_stats(q).occupied==4 && !adaptive_input_release_one(q));
    size_t n;assert(!adaptive_input_receive(q,&n,0)); // Unconfirmed bytes invisible.
    // Erase a tag-like range straddling packet boundaries, including lookahead.
    assert(stream_staging_erase(&s,2040,4099));
    memmove(expected+2040,expected+6139,WINDOW-6139);
    compare(&s,WINDOW-4099);
    stream_staging_cancel(&s);stream_staging_cancel(&s);
    assert(!adaptive_input_stats(q).occupied);
    // Maximum ADTS frame + following header uses four leases and lookahead.
    memset(incoming,0x55,WINDOW);
    const uint8_t aac[]={0xff,0xf1,0x4c,0x83,0xff,0xff,0xfc};
    memcpy(incoming,aac,7);memcpy(incoming+8191,aac,7);
    assert(stream_staging_append(&s,incoming,8198)==8198);
    stream_confirm_info_t info;
    assert(stream_confirm_window(stream_staging_read,&s,8198,false,4096,
        STREAM_ID3_RUN_BYTES,&info)==STREAM_CONFIRM_READY);
    assert(info.codec==STREAM_PROBE_AAC && info.first_frame_bytes==8191);
    // Commit the exact original leases; consumer sees their original addresses.
    size_t total=0;
    while (s.count) {
        void *original=s.packet[0];
        void *p=stream_staging_take(&s,&n);assert(p==original && n==PAYLOAD);
        assert(!memcmp((uint8_t *)p+HEADER,incoming+total,n));
        total+=n;
        assert(adaptive_input_commit(q,p));
        size_t packet_bytes;void *received=adaptive_input_receive(q,&packet_bytes,0);
        assert(received==p && packet_bytes==CAPACITY);
        assert(adaptive_input_return(q,received));
    }
    assert(total==8192 && stream_staging_size(&s)==6);
    assert(stream_staging_append(&s,incoming,100)==100);
    assert(s.count==1 && s.length[0]==106 && !s.look_used);
    assert(stream_staging_read(&s,0,observed,106));
    assert(!memcmp(observed,incoming+8192,6) && !memcmp(observed+6,incoming,100));
    stream_staging_cancel(&s);
    // Occupied queue: do not wait or allocate, and preserve the unaccepted input.
    for (unsigned i=0;i<4;++i) {
        void *p;assert(adaptive_input_acquire(q,&p,CAPACITY,0));assert(adaptive_input_commit(q,p));
    }
    assert(!stream_staging_append(&s,incoming,1) && !s.count);
    for (unsigned i=0;i<4;++i) {void *p=adaptive_input_receive(q,&n,0);assert(p);assert(adaptive_input_return(q,p));}
    // Random append/remove/transfer/cancel against an independent flat oracle,
    // overlapping real queue reclamation. Each acquired lease is terminated.
    pthread_t worker;assert(!pthread_create(&worker,NULL,reclaim,q));
    uint32_t random=0x584519;
    size_t bytes=0;
    for (unsigned trial=0;trial<20000;++trial) {
        random=random*1664525U+1013904223U;
        unsigned op=(random>>24)%4;
        if (op==0) {
            size_t wanted=(random%WINDOW)+1;
            size_t accepted=stream_staging_append(&s,incoming,wanted);
            assert(accepted<=wanted && accepted<=WINDOW-bytes);
            memcpy(expected+bytes,incoming,accepted);bytes+=accepted;
        } else if (op==1 && bytes) {
            size_t offset=random%bytes;
            size_t count=(random>>8)%(bytes-offset+1);
            assert(stream_staging_erase(&s,offset,count));
            memmove(expected+offset,expected+offset+count,bytes-offset-count);bytes-=count;
        } else if (op==2) {
            void *p=stream_staging_take(&s,&n);
            if (p) {
                assert(n<=bytes && !memcmp((uint8_t *)p+HEADER,expected,n));
                assert(adaptive_input_commit(q,p));
                size_t size;assert(adaptive_input_receive(q,&size,0)==p);
                assert(adaptive_input_return(q,p));
                memmove(expected,expected+n,bytes-n);bytes-=n;
            }
        } else {stream_staging_cancel(&s);bytes=0;}
        compare(&s,bytes);
    }
    atomic_store(&reclaim_done,true);assert(!pthread_join(worker,NULL));
    stream_staging_cancel(&s);
    assert(!adaptive_input_stats(q).occupied);
    adaptive_input_destroy(q);assert(!atomic_load(&live_allocations));
    atomic_store(&fail_after,-1);
    q=adaptive_input_create(3*CAPACITY,3*CAPACITY,CAPACITY);assert(q);
    assert(!stream_staging_init(&s,q,HEADER,PAYLOAD));adaptive_input_destroy(q);
    // TLS can reclaim spare slots, but cannot reclaim the held candidate.
    q=adaptive_input_create(8*CAPACITY,4*CAPACITY,CAPACITY);assert(q);
    assert(stream_staging_init(&s,q,HEADER,PAYLOAD));
    assert(stream_staging_append(&s,incoming,WINDOW)==WINDOW);
    unsigned released=0;while(adaptive_input_release_one(q))++released;
    assert(released==4 && adaptive_input_stats(q).resident==4);
    memcpy(expected,incoming,WINDOW);compare(&s,WINDOW);
    stream_staging_cancel(&s);adaptive_input_destroy(q);
    assert(!atomic_load(&live_allocations));
    puts("PASS staging: actual adaptive queue, max ADTS, exact lease transfer, compaction, backpressure, cancellation, TLS reclamation, 20000 randomized operations; ASan/UBSan");
}
