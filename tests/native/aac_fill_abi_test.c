// Cross-check each consumed field with the independent extended decoder view.
#include "aac_analysis_core.h"
#include "aac_fill_parser.h"
#define SAME_FIELD(a,b,field) \
    _Static_assert(offsetof(a,field)==offsetof(b,field), #field " offset"); \
    _Static_assert(sizeof(((a *)0)->field)==sizeof(((b *)0)->field), #field " size")
SAME_FIELD(aac_fill_bits_t,aac_analysis_bits_t,buffer);
SAME_FIELD(aac_fill_bits_t,aac_analysis_bits_t,used_bits);
SAME_FIELD(aac_fill_bits_t,aac_analysis_bits_t,available_bits);
SAME_FIELD(aac_fill_bits_t,aac_analysis_bits_t,input_length);
SAME_FIELD(aac_fill_bits_t,aac_analysis_bits_t,alignment_offset);
SAME_FIELD(aac_fill_stream_t,aac_analysis_sbr_stream_t,elements);
SAME_FIELD(aac_fill_stream_t,aac_analysis_sbr_stream_t,core_elements);
SAME_FIELD(aac_fill_stream_t,aac_analysis_sbr_stream_t,element);
SAME_FIELD(aac_fill_element_t,aac_analysis_sbr_element_t,element_id);
SAME_FIELD(aac_fill_element_t,aac_analysis_sbr_element_t,extension_type);
SAME_FIELD(aac_fill_element_t,aac_analysis_sbr_element_t,payload_bytes);
SAME_FIELD(aac_fill_element_t,aac_analysis_sbr_element_t,payload);
_Static_assert(sizeof(aac_fill_bits_t)==sizeof(aac_analysis_bits_t), "BITS size");
_Static_assert(sizeof(aac_fill_stream_t)==sizeof(aac_analysis_sbr_stream_t), "SBR stream size");
