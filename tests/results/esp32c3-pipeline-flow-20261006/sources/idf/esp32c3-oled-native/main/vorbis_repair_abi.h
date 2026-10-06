// Private RV32 ABI of esp_audio_codec 2.6.2, checked against the pinned objects.
// Tremor type definitions adapted from Xiph.Org's BSD-licensed low-memory
// decoder; see vorbis_repair/COPYING and README.md for provenance.
#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef int32_t ogg_int32_t;
typedef uint32_t ogg_uint32_t;
typedef uint16_t ogg_uint16_t;
typedef struct ogg_buffer {
    unsigned char *data;
    long size;
    int refcount;
    void *owner;
} ogg_buffer;
typedef struct ogg_reference {
    ogg_buffer *buffer;
    long begin, length;
    struct ogg_reference *next;
} ogg_reference;
typedef struct oggpack_buffer {
    int headbit;
    unsigned char *headptr;
    long headend;
    ogg_reference *head, *tail;
    long count;
} oggpack_buffer;
typedef struct ogg_packet {
    ogg_reference *packet;
    long bytes, b_o_s, e_o_s;
    int64_t granulepos, packetno;
} ogg_packet;
typedef struct vorbis_info {
    int version, channels;
    long rate, bitrate_upper, bitrate_nominal, bitrate_lower, bitrate_window;
    struct codec_setup_info *codec_setup;
} vorbis_info;
typedef struct vorbis_dsp_state {
    vorbis_info *vi;
    oggpack_buffer opb;
    int32_t **work, **mdctright;
    int out_begin, out_end;
    long lW, W;
    int64_t granulepos, sequence, sample_count;
} vorbis_dsp_state;
typedef struct codebook {
    long dim, entries, used_entries;
    int dec_maxlength;
    void *dec_table;
    int dec_nodeb, dec_leafw, dec_type;
    int32_t q_min;
    int q_minp;
    int32_t q_del;
    int q_delp, q_seq, q_bits, q_pack;
    void *q_val;
} codebook;
typedef void vorbis_info_floor;
typedef struct {
    int order;
    long rate, barkmap;
    int ampbits, ampdB, numbooks;
    unsigned char books[16];
} vorbis_info_floor0;
typedef struct {
    char class_dim, class_subs;
    unsigned char class_book, class_subbook[8];
} floor1class;
typedef struct {
    floor1class *class;
    char *partitionclass;
    uint16_t *postlist;
    char *forward_index, *hineighbor, *loneighbor;
    int partitions, posts, mult;
} vorbis_info_floor1;
typedef struct {
    int type;
    unsigned char *stagemasks, *stagebooks;
    long begin, end;
    int grouping;
    char partitions;
    unsigned char groupbook;
    char stages;
} vorbis_info_residue;
typedef struct { unsigned char blockflag, mapping; } vorbis_info_mode;
typedef struct { unsigned char mag, ang; } coupling_step;
typedef struct { unsigned char floor, residue; } submap;
typedef struct {
    int submaps;
    unsigned char *chmuxlist;
    submap *submaplist;
    int coupling_steps;
    coupling_step *coupling;
} vorbis_info_mapping;
typedef struct codec_setup_info {
    long blocksizes[2];
    int modes, maps, floors, residues, books;
    vorbis_info_mode *mode_param;
    vorbis_info_mapping *map_param;
    char *floor_type;
    vorbis_info_floor **floor_param;
    vorbis_info_residue *residue_param;
    codebook *book_param;
} codec_setup_info;
typedef struct {
    vorbis_dsp_state *dsp;
    ogg_packet packet;
    bool sent_info;
} vorbis_wrapper;

#define VORBIS_ABI_SIZE(type, bytes) _Static_assert(sizeof(type) == bytes, #type " size")
#define VORBIS_ABI_FIELD(type, field, offset) \
    _Static_assert(offsetof(type, field) == offset, #type "." #field)
VORBIS_ABI_SIZE(ogg_buffer, 16);
VORBIS_ABI_SIZE(ogg_reference, 16);
VORBIS_ABI_SIZE(oggpack_buffer, 24);
VORBIS_ABI_SIZE(ogg_packet, 32);
VORBIS_ABI_SIZE(vorbis_info, 32);
VORBIS_ABI_FIELD(vorbis_info, codec_setup, 28);
VORBIS_ABI_SIZE(vorbis_dsp_state, 80);
VORBIS_ABI_FIELD(vorbis_dsp_state, work, 28);
VORBIS_ABI_FIELD(vorbis_dsp_state, mdctright, 32);
VORBIS_ABI_FIELD(vorbis_dsp_state, out_begin, 36);
VORBIS_ABI_FIELD(vorbis_dsp_state, granulepos, 56);
VORBIS_ABI_SIZE(codebook, 64);
VORBIS_ABI_FIELD(codebook, dec_table, 16);
VORBIS_ABI_FIELD(codebook, q_val, 60);
VORBIS_ABI_SIZE(vorbis_info_floor0, 40);
VORBIS_ABI_SIZE(floor1class, 11);
VORBIS_ABI_SIZE(vorbis_info_floor1, 36);
VORBIS_ABI_FIELD(vorbis_info_floor1, hineighbor, 16);
VORBIS_ABI_SIZE(vorbis_info_residue, 28);
VORBIS_ABI_SIZE(vorbis_info_mapping, 20);
VORBIS_ABI_SIZE(codec_setup_info, 52);
VORBIS_ABI_FIELD(codec_setup_info, mode_param, 28);
VORBIS_ABI_FIELD(codec_setup_info, floor_param, 40);
VORBIS_ABI_FIELD(codec_setup_info, book_param, 48);
VORBIS_ABI_SIZE(vorbis_wrapper, 48);
VORBIS_ABI_FIELD(vorbis_wrapper, packet, 8);
VORBIS_ABI_FIELD(vorbis_wrapper, sent_info, 40);

long tremor_oggpack_read(oggpack_buffer *, int);
int tremor_oggpack_eop(oggpack_buffer *);
