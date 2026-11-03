#ifndef DISPATCH_WORD_ALLOCATOR_H
#define DISPATCH_WORD_ALLOCATOR_H

/* Tracked HOST malloc seam, not ESP capability/IRAM evidence. Every live word
 * block and old/replacement candidate has an independent guarded allocation. */
#ifdef DISPATCH_WORD_STORAGE
typedef struct {void *pointer;uint32_t *base;size_t bytes;} dispatch_word_block;
static struct {
    dispatch_word_block block[16];
    unsigned calls,refuse,misalign,live,frees;
} dispatch_words;
static unsigned word_peak_live,word_allocation_attempts;
static void dispatch_word_guards(const dispatch_word_block *block) {
    assert(block->base[0]==UINT32_C(0x52ac9d17) && block->base[block->bytes/4u+1u]==UINT32_C(0xe3406b8f));
}
static void *dispatch_word_alloc(size_t bytes) {
    assert(bytes && !(bytes&3u) && bytes<=11520u);
    ++dispatch_words.calls;++word_allocation_attempts;
    if(dispatch_words.calls==dispatch_words.refuse)return NULL;
    unsigned index=0;while(index<16 && dispatch_words.block[index].pointer)++index;assert(index<16);
    uint32_t *base=malloc(bytes+8u);assert(base);
    for(size_t word=0;word<bytes/4u+2u;++word)base[word]=UINT32_C(0x6b9182a4);
    base[0]=UINT32_C(0x52ac9d17);base[bytes/4u+1u]=UINT32_C(0xe3406b8f);
    void *pointer=(uint8_t *)(base+1)+(dispatch_words.calls==dispatch_words.misalign?1u:0u);
    dispatch_words.block[index]=(dispatch_word_block){pointer,base,bytes};
    ++dispatch_words.live;if(dispatch_words.live>word_peak_live)word_peak_live=dispatch_words.live;
    return pointer;
}
static void dispatch_word_free(void *pointer) {
    assert(pointer);unsigned index=0;while(index<16 && dispatch_words.block[index].pointer!=pointer)++index;assert(index<16);
    dispatch_word_guards(dispatch_words.block+index);free(dispatch_words.block[index].base);
    dispatch_words.block[index]=(dispatch_word_block){0};assert(dispatch_words.live);--dispatch_words.live;++dispatch_words.frees;
}
static void dispatch_word_reset(void) {assert(!dispatch_words.live);memset(&dispatch_words,0,sizeof(dispatch_words));}
static bool dispatch_word_empty(void) {return !dispatch_words.live;}
static unsigned dispatch_word_enabled(void) {return 1;}
static unsigned dispatch_word_peak(void) {return word_peak_live;}
static unsigned dispatch_word_attempts(void) {return word_allocation_attempts;}
static uint64_t dispatch_word_digest(const opus_family1_playback *s) {
    uint64_t value=UINT64_C(14695981039346656037);
    for(unsigned plane=0;plane<s->plane_count;++plane)for(size_t word=0;word<s->word_capacity/4u;++word) {
        value^=s->word_planes[plane][word];value*=UINT64_C(1099511628211);
    }
    return value;
}
#else
static void dispatch_word_reset(void) {}
static bool dispatch_word_empty(void) {return true;}
static unsigned dispatch_word_enabled(void) {return 0;}
static unsigned dispatch_word_peak(void) {return 0;}
static unsigned dispatch_word_attempts(void) {return 0;}
#endif
static bool dispatch_planes_present(const opus_family1_playback *s) {
#ifdef DISPATCH_WORD_STORAGE
    if(s->word_mode) {
        assert(s->plane_count && s->word_capacity && !s->planes);
        for(unsigned plane=0;plane<s->plane_count;++plane) {
            assert(s->word_planes[plane]);unsigned index=0;
            while(index<16 && dispatch_words.block[index].pointer!=(void *)s->word_planes[plane])++index;
            assert(index<16);dispatch_word_guards(dispatch_words.block+index);
        }
        return true;
    }
#endif
    return s->planes!=NULL;
}
typedef struct {
    uint8_t *bytes;size_t capacity;
#ifdef DISPATCH_WORD_STORAGE
    volatile uint32_t *words[8];size_t word_capacity;bool word_mode;uint64_t digest;
#endif
} dispatch_plane_snapshot;
static dispatch_plane_snapshot dispatch_snapshot(const opus_family1_playback *s) {
    dispatch_plane_snapshot result={.bytes=s->planes,.capacity=s->capacity};
#ifdef DISPATCH_WORD_STORAGE
    result.word_mode=s->word_mode;result.word_capacity=s->word_capacity;
    for(unsigned plane=0;plane<8;++plane)result.words[plane]=s->word_planes[plane];
    if(s->word_mode)result.digest=dispatch_word_digest(s);
#endif
    return result;
}
static void dispatch_snapshot_equal(const opus_family1_playback *s,const dispatch_plane_snapshot *saved) {
    assert(s->planes==saved->bytes && s->capacity==saved->capacity);
#ifdef DISPATCH_WORD_STORAGE
    assert(s->word_mode==saved->word_mode && s->word_capacity==saved->word_capacity);
    for(unsigned plane=0;plane<8;++plane)assert(s->word_planes[plane]==saved->words[plane]);
    if(s->word_mode)assert(dispatch_word_digest(s)==saved->digest);
#endif
}
#endif
