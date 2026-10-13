#include "stream_confirm.h"
stream_confirm_result_t target_confirm(stream_confirm_read_fn read,void *context,size_t bytes,bool eof,size_t search_left,uint32_t tag_budget,stream_confirm_info_t *out) {
    return stream_confirm_window(read,context,bytes,eof,search_left,tag_budget,out);
}
