// Exercise the actual vendor FIR with guarded 5-entry pointer tables, including
// smoothing enabled even when corpus encoders always emit the default off mode.
#include "esp_log.h"
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

void envelope_application(int32_t *,int32_t *,int32_t *,int32_t *,int32_t *,int32_t *,
    int32_t *,int32_t *,int32_t **,int32_t **,int32_t **,int32_t **,const int32_t *,
    int32_t *,int32_t *,int,int,int,int,int,int,int);
typedef struct {uint32_t before;int32_t *row[5];uint32_t after;} compact_table_t;
typedef struct {
    int32_t qmf[2][32*48];
    int32_t values[6][64];
    int32_t history[4][5][64];
    int32_t harm,phase;
} state_t;

void qemu_aac_smoothing_fir_test(void) {
    state_t *ref=malloc(sizeof(*ref)),*compact=malloc(sizeof(*compact));
    assert(ref && compact);
    const unsigned bands[]={1,32,48};
    unsigned cases=0;
    for(unsigned mode=0;mode<2;++mode)for(unsigned tone=0;tone<2;++tone)
    for(unsigned no_noise=0;no_noise<2;++no_noise)for(unsigned b=0;b<3;++b) {
        memset(ref,0,sizeof(*ref));
        for(unsigned i=0;i<32*48;++i){ref->qmf[0][i]=(int)(i%17)-8;ref->qmf[1][i]=(int)(i%13)-6;}
        for(unsigned k=0;k<64;++k) {
            ref->values[0][k]=1<<25;ref->values[1][k]=0;
            ref->values[2][k]=1<<20;ref->values[3][k]=0;
            ref->values[4][k]=(tone && k%7==0)?1<<18:0;ref->values[5][k]=0;
            for(unsigned row=0;row<5;++row) {
                ref->history[0][row][k]=(1<<24)+(int)(row*1000+k);
                ref->history[1][row][k]=0;
                ref->history[2][row][k]=(1<<19)+(int)(row*100+k);
                ref->history[3][row][k]=0;
            }
        }
        memcpy(compact,ref,sizeof(*ref));
        int32_t *table[4][64]={{0}};
        compact_table_t small[4];
        for(unsigned t=0;t<4;++t) {
            small[t].before=0x12345678;small[t].after=0x87654321;
            for(unsigned i=0;i<5;++i){table[t][i]=ref->history[t][i];small[t].row[i]=compact->history[t][i];}
        }
        const int32_t frame_info[]={1,0,16,0,0,0,0,0};
        for(unsigned frame=0;frame<3;++frame)for(unsigned leg=0;leg<2;++leg) {
            state_t *s=leg?compact:ref;
            envelope_application(s->qmf[0],s->qmf[1],s->values[0],s->values[1],s->values[2],s->values[3],
                s->values[4],s->values[5],leg?small[0].row:table[0],leg?small[1].row:table[1],
                leg?small[2].row:table[2],leg?small[3].row:table[3],frame_info,&s->harm,&s->phase,
                0,64-bands[b],bands[b],no_noise,tone,4,(mode^(frame==1))?4:0);
            if(leg)assert(!memcmp(ref,compact,sizeof(*ref)));
        }
        assert(!memcmp(ref,compact,sizeof(*ref)));
        for(unsigned t=0;t<4;++t) {
            assert(small[t].before==0x12345678 && small[t].after==0x87654321);
            for(unsigned i=0;i<5;++i) {
                assert((uintptr_t)table[t][i]-(uintptr_t)ref==(uintptr_t)small[t].row[i]-(uintptr_t)compact);
                assert((uintptr_t)small[t].row[i]>=(uintptr_t)compact->history[t][0] &&
                       (uintptr_t)small[t].row[i]<=(uintptr_t)compact->history[t][4]);
            }
            for(unsigned i=5;i<64;++i)assert(!table[t][i]);
        }
        ++cases;
    }
    free(ref);free(compact);
    assert(cases==24);
    ESP_LOGI("sbr_compact5","SBRLAYOUT_FIR_PASS cases=%u slots=32 frames=3 max_index=4 qmf_equal=1",cases);
}
