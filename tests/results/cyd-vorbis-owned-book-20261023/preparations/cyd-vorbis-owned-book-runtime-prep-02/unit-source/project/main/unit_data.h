/* Generated raw source-fixture descriptors; no codec execution. */
#pragma once
#include <stdint.h>
#define UNIT_CASE_COUNT 16U
#define UNIT_PROBE_COUNT 61U
#define UNIT_CONTRACT_SHA256 "593ba30afb3ab43bbefd79751c9641c98539913c9726445b4e55b5fba5fac4a8"
typedef struct { unsigned original; uint32_t wire; unsigned bits; uint32_t leaf; int32_t expected[16]; } unit_probe_t;
typedef struct { const char *id; const uint8_t *setup; unsigned setup_bytes,book_first_bit,book_end_bit;
 int dim,entries,used_entries,max_length,node_bytes,leaf_words,dec_type,sequence,q_pack;
 unsigned table_bytes,qval_bytes; const uint8_t *qval; const unit_probe_t *probes; unsigned probe_count; } unit_case_t;
static const uint8_t setup_0[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,129,32,52,100,37,0,80,0,0,16,4,140,0,0,64,241,0,0,64,177,128,0,0,0,16,0,0,32,32,0,0,0,0,0,2,0,224,1,0,32,0,136,8,8,0,0,0,0,0,0,32,0,0,0,0,0,16,0,0,0,0,32};
static const unit_probe_t probes_0[] = {
 {0,0U,1,0U,{-1,-1}},
 {1,1U,3,2U,{1,-1}},
 {2,5U,3,8U,{-1,1}},
 {3,3U,3,10U,{1,1}},
 {4,7U,3,0U,{-1,-1}},
};
static const uint8_t setup_1[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,0,0,66,67,86,2,0,5,0,0,8,32,132,136,0,0,64,241,0,0,64,177,128,0,0,0,16,0,0,32,32,0,0,0,0,0,2,0,224,1,0,32,0,136,8,8,0,0,0,0,0,0,32,0,0,0,0,0,16,0,0,0,0,32};
static const unit_probe_t probes_1[] = {
 {0,0U,3,0U,{-1,-1}},
 {1,1U,1,2U,{1,-1}},
 {2,4U,3,8U,{-1,1}},
 {3,2U,3,10U,{1,1}},
 {4,6U,3,0U,{-1,-1}},
};
static const uint8_t setup_2[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,0,0,66,67,86,2,0,6,0,0,6,134,66,17,1,0,128,226,1,0,128,98,1,1,0,0,32,0,0,64,64,0,0,0,0,0,4,0,192,3,0,64,0,16,17,16,0,0,0,0,0,0,64,0,0,0,0,0,32,0,0,0,0,64};
static const unit_probe_t probes_2[] = {
 {0,0U,1,0U,{-1,-1}},
 {2,1U,2,8U,{-1,1}},
 {3,3U,3,10U,{1,1}},
 {5,7U,3,2U,{1,-1}},
};
static const uint8_t setup_3[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,129,32,52,100,37,0,80,0,0,16,4,140,0,0,64,241,0,0,64,177,136,0,0,0,16,0,0,32,32,0,0,0,0,0,2,0,224,1,0,32,0,136,8,8,0,0,0,0,0,0,32,0,0,0,0,0,16,0,0,0,0,32};
static const unit_probe_t probes_3[] = {
 {0,0U,1,0U,{-1,-2}},
 {1,1U,3,2U,{1,0}},
 {2,5U,3,8U,{-1,0}},
 {3,3U,3,10U,{1,2}},
 {4,7U,3,0U,{-1,-2}},
};
static const uint8_t setup_4[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,129,32,52,100,37,0,80,0,0,16,4,148,0,0,64,241,0,0,64,177,0,130,10,0,0,0,16,0,0,32,32,0,0,0,0,0,2,0,224,1,0,32,0,136,8,8,0,0,0,0,0,0,32,0,0,0,0,0,16,0,0,0,0,32};
static const unit_probe_t probes_4[] = {
 {0,0U,1,0U,{-1,-1}},
 {1,1U,3,2U,{1,-1}},
 {2,5U,3,8U,{-1,1}},
 {3,3U,3,10U,{1,1}},
 {4,7U,3,0U,{-1,-1}},
};
static const uint8_t setup_5[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,0,0,66,67,86,2,0,5,0,0,8,32,132,144,0,0,64,241,0,0,64,177,8,130,10,0,0,0,16,0,0,32,32,0,0,0,0,0,2,0,224,1,0,32,0,136,8,8,0,0,0,0,0,0,32,0,0,0,0,0,16,0,0,0,0,32};
static const unit_probe_t probes_5[] = {
 {0,0U,3,0U,{-1,-2}},
 {1,1U,1,2U,{1,0}},
 {2,4U,3,8U,{-1,0}},
 {3,2U,3,10U,{1,2}},
 {4,6U,3,0U,{-1,-2}},
};
static const uint8_t setup_6[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,0,0,66,67,86,4,0,6,0,0,6,134,66,33,1,0,128,226,1,0,128,98,1,0,69,4,81,80,21,0,0,0,2,0,0,4,4,0,0,0,0,64,0,0,60,0,0,4,0,17,1,1,0,0,0,0,0,0,4,0,0,0,0,0,2,0,0,0,0,4};
static const unit_probe_t probes_6[] = {
 {0,0U,1,0U,{-1,-1,-1,-1}},
 {2,1U,2,34U,{1,-1,1,-1}},
 {3,3U,3,136U,{-1,1,-1,1}},
 {5,7U,3,170U,{1,1,1,1}},
};
static const uint8_t setup_7[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,0,0,66,67,86,4,0,6,0,0,6,134,66,33,1,0,128,226,1,0,128,98,17,0,69,4,81,80,21,0,0,0,2,0,0,4,4,0,0,0,0,64,0,0,60,0,0,4,0,17,1,1,0,0,0,0,0,0,4,0,0,0,0,0,2,0,0,0,0,4};
static const unit_probe_t probes_7[] = {
 {0,0U,1,0U,{-1,-2,-3,-4}},
 {2,1U,2,34U,{1,0,1,0}},
 {3,3U,3,136U,{-1,0,-1,0}},
 {5,7U,3,170U,{1,2,3,4}},
};
static const uint8_t setup_8[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,0,0,66,67,86,16,0,6,0,0,6,134,66,33,1,0,128,226,1,0,128,98,65,68,68,68,100,114,114,114,18,17,17,17,81,65,65,65,161,165,165,165,5,20,20,20,20,0,0,0,2,0,0,10,4,0,0,0,0,64,0,0,60,0,0,4,0,17,1,1,0,0,0,0,0,0,4,0,0,0,0,0,2,0,0,0,0,4};
static const uint8_t qval_8[] = {2,0,2,0,2,0,2,0,2,0,2,0,2,0,2,0,0,2,0,2,0,2,0,2,0,2,0,2,0,2,0,2,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2};
static const unit_probe_t probes_8[] = {
 {0,0U,1,0U,{1,-1,1,-1,1,-1,1,-1,1,-1,1,-1,1,-1,1,-1}},
 {2,1U,2,1U,{-1,1,-1,1,-1,1,-1,1,-1,1,-1,1,-1,1,-1,1}},
 {3,3U,3,2U,{1,1,-1,-1,1,1,-1,-1,1,1,-1,-1,1,1,-1,-1}},
 {5,7U,3,3U,{-1,-1,1,1,-1,-1,1,1,-1,-1,1,1,-1,-1,1,1}},
};
static const uint8_t setup_9[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,0,0,66,67,86,16,0,4,0,0,65,82,2,0,0,197,3,0,0,197,130,136,136,136,8,34,34,34,162,130,130,130,2,40,40,40,40,0,0,0,4,0,0,20,8,0,0,0,0,128,0,0,120,0,0,8,0,34,2,2,0,0,0,0,0,0,8,0,0,0,0,0,4,0,0,0,0,8};
static const uint8_t qval_9[] = {2,0,2,0,2,0,2,0,2,0,2,0,2,0,2,0,0,2,0,2,0,2,0,2,0,2,0,2,0,2,0,2,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2};
static const unit_probe_t probes_9[] = {
 {0,0U,1,0U,{1,-1,1,-1,1,-1,1,-1,1,-1,1,-1,1,-1,1,-1}},
 {1,1U,2,1U,{-1,1,-1,1,-1,1,-1,1,-1,1,-1,1,-1,1,-1,1}},
 {2,3U,3,2U,{1,1,-1,-1,1,1,-1,-1,1,1,-1,-1,1,1,-1,-1}},
 {3,7U,3,3U,{-1,-1,1,1,-1,-1,1,1,-1,-1,1,1,-1,-1,1,1}},
};
static const uint8_t setup_10[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,0,0,66,67,86,16,0,6,0,0,6,134,66,33,1,0,128,226,1,0,128,98,81,68,68,68,100,114,114,114,18,17,17,17,81,65,65,65,161,165,165,165,5,20,20,20,20,0,0,0,2,0,0,10,4,0,0,0,0,64,0,0,60,0,0,4,0,17,1,1,0,0,0,0,0,0,4,0,0,0,0,0,2,0,0,0,0,4};
static const uint8_t qval_10[] = {2,0,2,0,2,0,2,0,2,0,2,0,2,0,2,0,0,2,0,2,0,2,0,2,0,2,0,2,0,2,0,2,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2};
static const unit_probe_t probes_10[] = {
 {0,0U,1,0U,{1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0}},
 {2,1U,2,1U,{-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0}},
 {3,3U,3,2U,{1,2,1,0,1,2,1,0,1,2,1,0,1,2,1,0}},
 {5,7U,3,3U,{-1,-2,-1,0,-1,-2,-1,0,-1,-2,-1,0,-1,-2,-1,0}},
};
static const uint8_t setup_11[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,0,0,66,67,86,16,0,4,0,0,65,82,2,0,0,197,3,0,0,197,162,136,136,136,8,34,34,34,162,130,130,130,2,40,40,40,40,0,0,0,4,0,0,20,8,0,0,0,0,128,0,0,120,0,0,8,0,34,2,2,0,0,0,0,0,0,8,0,0,0,0,0,4,0,0,0,0,8};
static const uint8_t qval_11[] = {2,0,2,0,2,0,2,0,2,0,2,0,2,0,2,0,0,2,0,2,0,2,0,2,0,2,0,2,0,2,0,2,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2};
static const unit_probe_t probes_11[] = {
 {0,0U,1,0U,{1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0}},
 {1,1U,2,1U,{-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0}},
 {2,3U,3,2U,{1,2,1,0,1,2,1,0,1,2,1,0,1,2,1,0}},
 {3,7U,3,3U,{-1,-2,-1,0,-1,-2,-1,0,-1,-2,-1,0,-1,-2,-1,0}},
};
static const uint8_t setup_12[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,0,0,66,67,86,2,0,1,0,0,0,9,0,0,20,15,0,0,20,11,2,0,0,0,1,0,0,5,2,0,0,0,0,32,0,0,30,0,0,2,128,136,128,0,0,0,0,0,0,0,2,0,0,0,0,0,1,0,0,0,0,2};
static const unit_probe_t probes_12[] = {
 {0,0U,1,2U,{1,-1}},
 {0,1U,1,2U,{1,-1}},
};
static const uint8_t setup_13[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,0,0,66,67,86,2,0,2,0,0,0,32,1,0,128,226,1,0,128,98,65,4,0,0,0,2,0,0,10,4,0,0,0,0,64,0,0,60,0,0,4,0,17,1,1,0,0,0,0,0,0,4,0,0,0,0,0,2,0,0,0,0,4};
static const unit_probe_t probes_13[] = {
 {0,0U,1,2U,{1,-1}},
 {1,1U,1,2U,{1,-1}},
};
static const uint8_t setup_14[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,0,0,66,67,86,2,0,1,0,0,0,9,0,0,20,15,0,0,20,139,2,0,0,0,1,0,0,5,2,0,0,0,0,32,0,0,30,0,0,2,128,136,128,0,0,0,0,0,0,0,2,0,0,0,0,0,1,0,0,0,0,2};
static const unit_probe_t probes_14[] = {
 {0,0U,1,2U,{1,0}},
 {0,1U,1,2U,{1,0}},
};
static const uint8_t setup_15[] = {5,118,111,114,98,105,115,1,66,67,86,1,0,2,0,0,0,0,66,67,86,2,0,2,0,0,0,32,1,0,128,226,1,0,128,98,81,4,0,0,0,2,0,0,10,4,0,0,0,0,64,0,0,60,0,0,4,0,17,1,1,0,0,0,0,0,0,4,0,0,0,0,0,2,0,0,0,0,4};
static const unit_probe_t probes_15[] = {
 {0,0U,1,2U,{1,0}},
 {1,1U,1,2U,{1,0}},
};
static const unit_case_t unit_cases[] = {
 {.id="ordered_lattice_d2_seq0",.setup=setup_0,.setup_bytes=78,.book_first_bit=140,.book_end_bit=296,.dim=2,.entries=5,.used_entries=5,.max_length=3,.node_bytes=1,.leaf_words=1,.dec_type=1,.sequence=0,.q_pack=0,.table_bytes=8,.qval_bytes=0,.qval=NULL,.probes=probes_0,.probe_count=5},
 {.id="unordered_lattice_d2_seq0",.setup=setup_1,.setup_bytes=80,.book_first_bit=144,.book_end_bit=312,.dim=2,.entries=5,.used_entries=5,.max_length=3,.node_bytes=1,.leaf_words=1,.dec_type=1,.sequence=0,.q_pack=0,.table_bytes=8,.qval_bytes=0,.qval=NULL,.probes=probes_1,.probe_count=5},
 {.id="sparse_lattice_d2_seq0",.setup=setup_2,.setup_bytes=80,.book_first_bit=144,.book_end_bit=313,.dim=2,.entries=6,.used_entries=4,.max_length=3,.node_bytes=1,.leaf_words=1,.dec_type=1,.sequence=0,.q_pack=0,.table_bytes=6,.qval_bytes=0,.qval=NULL,.probes=probes_2,.probe_count=4},
 {.id="ordered_lattice_d2_seq1",.setup=setup_3,.setup_bytes=78,.book_first_bit=140,.book_end_bit=296,.dim=2,.entries=5,.used_entries=5,.max_length=3,.node_bytes=1,.leaf_words=1,.dec_type=1,.sequence=1,.q_pack=0,.table_bytes=8,.qval_bytes=0,.qval=NULL,.probes=probes_3,.probe_count=5},
 {.id="ordered_explicit_d2_seq0",.setup=setup_4,.setup_bytes=80,.book_first_bit=140,.book_end_bit=312,.dim=2,.entries=5,.used_entries=5,.max_length=3,.node_bytes=1,.leaf_words=1,.dec_type=1,.sequence=0,.q_pack=0,.table_bytes=8,.qval_bytes=0,.qval=NULL,.probes=probes_4,.probe_count=5},
 {.id="unordered_explicit_d2_seq1",.setup=setup_5,.setup_bytes=82,.book_first_bit=144,.book_end_bit=328,.dim=2,.entries=5,.used_entries=5,.max_length=3,.node_bytes=1,.leaf_words=1,.dec_type=1,.sequence=1,.q_pack=0,.table_bytes=8,.qval_bytes=0,.qval=NULL,.probes=probes_5,.probe_count=5},
 {.id="sparse_explicit_d4_seq0",.setup=setup_6,.setup_bytes=86,.book_first_bit=144,.book_end_bit=357,.dim=4,.entries=6,.used_entries=4,.max_length=3,.node_bytes=1,.leaf_words=2,.dec_type=1,.sequence=0,.q_pack=0,.table_bytes=10,.qval_bytes=0,.qval=NULL,.probes=probes_6,.probe_count=4},
 {.id="sparse_explicit_d4_seq1",.setup=setup_7,.setup_bytes=86,.book_first_bit=144,.book_end_bit=357,.dim=4,.entries=6,.used_entries=4,.max_length=3,.node_bytes=1,.leaf_words=2,.dec_type=1,.sequence=1,.q_pack=0,.table_bytes=10,.qval_bytes=0,.qval=NULL,.probes=probes_7,.probe_count=4},
 {.id="sparse_explicit_d16_seq0",.setup=setup_8,.setup_bytes=104,.book_first_bit=144,.book_end_bit=501,.dim=16,.entries=6,.used_entries=4,.max_length=3,.node_bytes=1,.leaf_words=1,.dec_type=3,.sequence=0,.q_pack=16,.table_bytes=6,.qval_bytes=64,.qval=qval_8,.probes=probes_8,.probe_count=4},
 {.id="dense_active_d16_seq0",.setup=setup_9,.setup_bytes=94,.book_first_bit=144,.book_end_bit=422,.dim=16,.entries=4,.used_entries=4,.max_length=3,.node_bytes=1,.leaf_words=1,.dec_type=3,.sequence=0,.q_pack=16,.table_bytes=6,.qval_bytes=64,.qval=qval_9,.probes=probes_9,.probe_count=4},
 {.id="sparse_explicit_d16_seq1",.setup=setup_10,.setup_bytes=104,.book_first_bit=144,.book_end_bit=501,.dim=16,.entries=6,.used_entries=4,.max_length=3,.node_bytes=1,.leaf_words=1,.dec_type=3,.sequence=1,.q_pack=16,.table_bytes=6,.qval_bytes=64,.qval=qval_10,.probes=probes_10,.probe_count=4},
 {.id="dense_active_d16_seq1",.setup=setup_11,.setup_bytes=94,.book_first_bit=144,.book_end_bit=422,.dim=16,.entries=4,.used_entries=4,.max_length=3,.node_bytes=1,.leaf_words=1,.dec_type=3,.sequence=1,.q_pack=16,.table_bytes=6,.qval_bytes=64,.qval=qval_11,.probes=probes_11,.probe_count=4},
 {.id="single_explicit_d2_seq0",.setup=setup_12,.setup_bytes=78,.book_first_bit=144,.book_end_bit=292,.dim=2,.entries=1,.used_entries=1,.max_length=1,.node_bytes=4,.leaf_words=1,.dec_type=1,.sequence=0,.q_pack=0,.table_bytes=12,.qval_bytes=0,.qval=NULL,.probes=probes_12,.probe_count=2},
 {.id="dense_twin_d2_seq0",.setup=setup_13,.setup_bytes=79,.book_first_bit=144,.book_end_bit=301,.dim=2,.entries=2,.used_entries=2,.max_length=1,.node_bytes=1,.leaf_words=1,.dec_type=1,.sequence=0,.q_pack=0,.table_bytes=2,.qval_bytes=0,.qval=NULL,.probes=probes_13,.probe_count=2},
 {.id="single_explicit_d2_seq1",.setup=setup_14,.setup_bytes=78,.book_first_bit=144,.book_end_bit=292,.dim=2,.entries=1,.used_entries=1,.max_length=1,.node_bytes=4,.leaf_words=1,.dec_type=1,.sequence=1,.q_pack=0,.table_bytes=12,.qval_bytes=0,.qval=NULL,.probes=probes_14,.probe_count=2},
 {.id="dense_twin_d2_seq1",.setup=setup_15,.setup_bytes=79,.book_first_bit=144,.book_end_bit=301,.dim=2,.entries=2,.used_entries=2,.max_length=1,.node_bytes=1,.leaf_words=1,.dec_type=1,.sequence=1,.q_pack=0,.table_bytes=2,.qval_bytes=0,.qval=NULL,.probes=probes_15,.probe_count=2},
};
_Static_assert(sizeof(unit_cases)/sizeof(unit_cases[0]) == UNIT_CASE_COUNT, "Exact sixteen books");
