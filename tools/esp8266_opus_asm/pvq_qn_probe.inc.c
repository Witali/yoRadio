/* Host-only census: observe the original compute_qn result; never replace it.
 * The non-stereo clone is the narrow target in the accepted frozen ASM.
 * This instrumentation and its counters are NOT linked into firmware. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
typedef struct { uint64_t total, low, qb[61]; } y_qn_group;
static y_qn_group y_qn_counts[2];
static void y_qn_check(int ok) {
   if (!ok) { fputs("PVQ qn observer assertion\n", stderr); abort(); }
}
static void y_qn_save(void) {
   const char *name = getenv("YORADIO_QN_COUNTS");
   y_qn_check(name != NULL);
   FILE *f = fopen(name, "wb"); y_qn_check(f != NULL);
   fputs("{", f);
   for (int group=0; group<2; group++) {
      const y_qn_group *c = &y_qn_counts[group];
      fprintf(f, "%s\"%s\":{\"total\":%" PRIu64 ",\"low\":%" PRIu64 ",\"qb\":[",
         group ? "," : "", group ? "stereo" : "nonstereo", c->total, c->low);
      for (int i=0; i<61; i++) fprintf(f, "%s%" PRIu64, i ? "," : "", c->qb[i]);
      fputs("]}", f);
   }
   fputs("}\n", f); y_qn_check(fclose(f) == 0);
}
__attribute__((constructor)) static void y_qn_init(void) {
   y_qn_check(atexit(y_qn_save) == 0);
}
static void y_qn_observe(int qb, int qn, int stereo) {
   static const int exp2[8] = {16384,17866,19483,21247,23170,25267,27554,30048};
   y_qn_check((stereo == 0 || stereo == 1) && qb <= 64);
   y_qn_group *c = &y_qn_counts[stereo]; c->total++;
   if (qb < 4) { y_qn_check(qn == 1); c->low++; }
   else {
      int expected = exp2[qb & 7] >> (14-(qb >> 3));
      expected = ((expected+1) >> 1) << 1;
      y_qn_check(qn == expected && qn >= 2 && qn <= 256);
      c->qb[qb-4]++;
   }
}
