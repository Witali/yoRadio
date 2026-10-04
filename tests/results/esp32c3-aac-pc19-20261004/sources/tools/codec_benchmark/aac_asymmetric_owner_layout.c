// Target-compiled addresses for unequal channel extents, without native DSP changes.
#include "aac_low_workspace_layout.c"
// The reset loop advances twice by the left extent. Its sentinel is only
// compared, never dereferenced; it no longer aliases the PS detection word.
const uint32_t aac_abi_frame_cursor_end[2]={
    offsetof(aac_sbr_owner_abi_t,embedded_ps),
    AAC_SBR_CHANNELS*sizeof(aac_high_channel_view_t)+offsetof(aac_high_channel_view_t,frame)};
const uint32_t aac_abi_frame_table_upper[2]={
    (offsetof(aac_sbr_channel_abi_t,smoothing)-offsetof(aac_sbr_channel_abi_t,frame)+0x800)>>12,0};
_Static_assert(offsetof(aac_high_owner_t,right)==sizeof(aac_high_channel_view_t),
               "The native reset-loop stride must reach the right frame exactly");
_Static_assert(AAC_SBR_CHANNELS*sizeof(aac_high_channel_view_t)+offsetof(aac_high_channel_view_t,frame)
               <sizeof(aac_high_owner_t),"Comparison-only sentinel stays inside the owner");
#if defined(AAC_HIGH_HISTORY_PC19) && !defined(AAC_HIGH_HISTORY_PC19_SIDECAR)
_Static_assert(sizeof(aac_high_owner_t)==32840,"PC19 owner boundary requires separate qualification");
#else
_Static_assert(sizeof(aac_high_owner_t)==32744,"Qualify a different allocator boundary separately");
#endif
_Static_assert(offsetof(aac_high_channel_t,frame)-offsetof(aac_high_channel_t,smoothing)<=2048,
               "Smoothing prefix addresses must fit a signed RV32 immediate");
