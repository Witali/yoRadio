/* Exact own setup publication only. No vendor decoder, curve or PCM. */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "pinned/production/vorbis_repair/setup.c"
#define P "CYD_VORBIS_OWNED_FLOOR0_"
#include "unit_support.h"
#include "unit_data.h"

static vorbis_info_floor0 published[UNIT_CASE_COUNT];
static void run_case(unsigned index) {
    current_case=index;current_probe=0;
    const floor_unit_case_t *c=unit_cases+index;
    require_unit(!live_allocations && !failed && xPortGetCoreID()==0,"fresh_owned_case_core0");
    struct { uint32_t first; codec_setup_info ci; uint32_t last; } context={0},before_context;
    struct { uint32_t first; vorbis_info vi; uint32_t last; } info={0},before_info;
    context.first=0x1937a51b;context.last=0x71c6b523;
    info.first=0x1ea61d49;info.last=0x436ac751;
    context.ci.books=c->total_books;
    context.ci.blocksizes[0]=c->short_samples;context.ci.blocksizes[1]=c->long_samples;
    info.vi.channels=c->channels;info.vi.rate=c->rate;info.vi.codec_setup=&context.ci;
    memcpy(&before_context,&context,sizeof(context));memcpy(&before_info,&info,sizeof(info));
    oggpack_buffer bits;
    begin_bits(&bits,c->setup,c->setup_bytes,c->first_bit,c->end_bit);
    vorbis_info_floor *raw=repair_floor0_info_unpack(&info.vi,&bits); /* Exact real external-linkage parser. */
    require_unit(raw && !view.eop && view.position==c->end_bit,"actual_floor_parser_exact_success");
    require_unit(!memcmp(&context,&before_context,sizeof(context)) && !memcmp(&info,&before_info,sizeof(info)),"owned_vi_ci_unchanged");
    require_unit(live_allocations==1 && owned_size(raw)==sizeof(vorbis_info_floor0) && sizeof(vorbis_info_floor0)==40,
                 "actual_single_owned_publication40");
    vorbis_info_floor0 *floor=(vorbis_info_floor0 *)raw;
    require_unit(floor->order==c->order && floor->rate==c->rate && floor->barkmap==c->barkmap &&
                 floor->ampbits==c->ampbits && floor->ampdB==c->ampdB && floor->numbooks==c->numbooks,
                 "actual_published_floor_fields");
    for (int i=0;i<floor->numbooks;++i)
        require_unit(floor->books[i]==c->books[i] && floor->books[i]<context.ci.books,"actual_published_book_list_bounds");
    for (int i=floor->numbooks;i<16;++i) require_unit(floor->books[i]==0,"normal_zeroed_allocator_unused_tail");
    all_guards();
    memcpy(published+index,floor,sizeof(*floor));
    printf(P "FIELDS case=%u id=%s group=%s first=%u end=%u consumed=%u total_books=%d order=%d rate=%ld barkmap=%ld"
           " ampbits=%d ampdb=%d numbooks=%d books=",index,c->id,c->group,c->first_bit,c->end_bit,
           (unsigned)(view.position-c->first_bit),context.ci.books,floor->order,floor->rate,floor->barkmap,
           floor->ampbits,floor->ampdB,floor->numbooks);
    for (int i=0;i<floor->numbooks;++i) printf("%s%u",i?",":"",(unsigned)floor->books[i]);
    printf(" allocated=40 live=1 vi_unchanged=1 ci_unchanged=1 guards=1 core=%d\n",xPortGetCoreID());
    repair_floor0_free_info(raw); /* Exact real static normal free. */
    require_unit(!live_allocations,"normal_floor_free_releases_owned_info");
    all_guards();
    printf(P "CASE case=%u id=%s live=0 guards=1 core=%d\n",index,c->id,xPortGetCoreID());
    vTaskDelay(1);
}

void app_main(void) {
    require_unit(xPortGetCoreID()==0,"coordinator_core0");
    printf(P "BEGIN contract=%s cases=%u pairs=%u core=%d\n",UNIT_CONTRACT_SHA256,UNIT_CASE_COUNT,UNIT_PAIR_COUNT,xPortGetCoreID());
    for (unsigned i=0;i<UNIT_CASE_COUNT;++i) run_case(i);
    for (unsigned i=0;i<UNIT_PAIR_COUNT;++i) {
        unsigned next=i+UNIT_PAIR_COUNT;
        require_unit(!memcmp(published+i,published+next,sizeof(*published)) &&
                     unit_cases[i].first_bit==unit_cases[next].first_bit && unit_cases[i].end_bit==unit_cases[next].end_bit,
                     "actual_original_minp1_publication_equal");
        printf(P "PAIR first=%u second=%u publication_equal=1 span_equal=1 bytes=40 core=%d\n",i,next,xPortGetCoreID());
    }
    require_unit(!failed && !live_allocations,"complete_owned_floor_publication_accounting");
    printf(P "COMPLETE cases=%u pairs=%u live=0 core=%d\n",UNIT_CASE_COUNT,UNIT_PAIR_COUNT,xPortGetCoreID());
    fflush(stdout);
    /* Return into SDK idle; root-owned QMP must prove actual EOF/quit/exit0. */
}
