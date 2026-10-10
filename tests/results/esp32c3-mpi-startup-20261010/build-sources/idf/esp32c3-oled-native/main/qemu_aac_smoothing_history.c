// Direct A/B execution of the pinned FIR, including short envelopes and all
// four persistent rows. This exercises enabled smoothing absent in the corpus.
#include "aac_smoothing_history.h"
#include "esp_log.h"
#include <stdlib.h>

void envelope_application(int32_t *,int32_t *,int32_t *,int32_t *,int32_t *,int32_t *,
    int32_t *,int32_t *,int32_t **,int32_t **,int32_t **,int32_t **,const int32_t *,
    int32_t *,int32_t *,int,int,int,int,int,int,int);
typedef struct {
    uint32_t before;
    int32_t rows[AAC_SMOOTHING_PAST_ROWS][AAC_SBR_BANDS];
    uint32_t after;
} guarded_matrix_t;
typedef struct {
    int32_t qmf[2][32*48],values[6][AAC_SBR_BANDS],harm,phase;
} signal_t;
typedef struct {
    signal_t signal[2];
    int32_t reference[4][AAC_SBR_ROWS][AAC_SBR_BANDS];
    guarded_matrix_t candidate[4];
} fixture_t;

void qemu_aac_smoothing_history_test(void) {
    fixture_t *f=malloc(sizeof(*f));assert(f);
    const unsigned bands[]={1,32,48}, lengths[]={2,4,6,8,10,32};
    unsigned cases=0,compared=0;
    for(unsigned mode=0;mode<2;++mode)for(unsigned tone=0;tone<2;++tone)
    for(unsigned no_noise=0;no_noise<2;++no_noise)for(unsigned b=0;b<3;++b)
    for(unsigned n=0;n<6;++n) {
        memset(f,0,sizeof(*f));
        int32_t *reference[4][5],*candidate[4][5];
        int32_t **tables[4]={candidate[0],candidate[1],candidate[2],candidate[3]};
        for(unsigned t=0;t<4;++t) {
            f->candidate[t].before=0x12345678;f->candidate[t].after=0x87654321;
            for(unsigned row=0;row<5;++row) {
                reference[t][row]=f->reference[t][row];
                for(unsigned band=0;band<64;++band)
                    reference[t][row][band]=(t&1)?-(int)(band%3):
                        (1<<24)+(int)(row*113+band*701);
                if(row<4) {
                    candidate[t][row]=f->candidate[t].rows[row];
                    memcpy(candidate[t][row],reference[t][row],sizeof(f->candidate[t].rows[row]));
                } else candidate[t][row]=NULL;
            }
        }
        for(unsigned frame=0;frame<7;++frame) {
            signal_t *seed=&f->signal[0];
            for(unsigned i=0;i<32*48;++i) {
                seed->qmf[0][i]=(int)((i+frame)%17)-8;
                seed->qmf[1][i]=(int)((i+frame)%13)-6;
            }
            for(unsigned k=0;k<64;++k) {
                seed->values[0][k]=(1<<25)+(int)(frame*1701+k);
                seed->values[1][k]=-(int)(k%3);
                seed->values[2][k]=(1<<20)+(int)(frame*113+k*57);
                seed->values[3][k]=-(int)(k%2);
                seed->values[4][k]=(tone && k%7==0)?1<<18:0;
                seed->values[5][k]=0;
            }
            memcpy(&f->signal[1],seed,sizeof(*seed));
            const int32_t info[]={1,0,(int32_t)(lengths[n]/2),0,0,0,0,0};
            for(unsigned leg=0;leg<2;++leg) {
                signal_t *s=&f->signal[leg];
                int32_t **r=leg?candidate[0]:reference[0];
                int32_t **re=leg?candidate[1]:reference[1];
                int32_t **q=leg?candidate[2]:reference[2];
                int32_t **qe=leg?candidate[3]:reference[3];
                aac_smoothing_scratch_t scratch;
                if(leg)aac_smoothing_begin(tables,&scratch);
                envelope_application(s->qmf[0],s->qmf[1],s->values[0],s->values[1],
                    s->values[2],s->values[3],s->values[4],s->values[5],r,re,q,qe,
                    info,&s->harm,&s->phase,0,64-bands[b],bands[b],no_noise,tone,
                    AAC_SMOOTHING_PAST_ROWS,(mode^(frame%3==1))?4:0);
                if(leg)aac_smoothing_end(tables,&scratch);
            }
            assert(!memcmp(&f->signal[0],&f->signal[1],sizeof(signal_t)));
            compared+=2*lengths[n]*bands[b];
            for(unsigned t=0;t<4;++t) {
                assert(f->candidate[t].before==0x12345678 && f->candidate[t].after==0x87654321);
                assert(!candidate[t][4]);
                for(unsigned row=0;row<4;++row) {
                    assert(!memcmp(reference[t][row],candidate[t][row],bands[b]*sizeof(int32_t)));
                    assert(candidate[t][row]>=f->candidate[t].rows[0] &&
                           candidate[t][row]<=f->candidate[t].rows[3]);
                    for(unsigned other=0;other<row;++other)assert(candidate[t][row]!=candidate[t][other]);
                }
            }
        }
        ++cases;
    }
    free(f);
    ESP_LOGI("sbr_four","SMOOTHING_HISTORY_FIR_PASS cases=%u frames=7 qmf_values=%u scratch_bytes=%u retained_rows=4 taps=5 guards=pass",
             cases,compared,(unsigned)sizeof(aac_smoothing_scratch_t));
}
