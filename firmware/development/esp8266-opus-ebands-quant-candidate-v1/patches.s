# quant_all_bands: reuse the accepted signed eBands pair leaf, not new storage.
# Input a8=eBands+2*i, 0<=i<21. Outputs a2=p[0], a3=p[1].
# a5 is dead until MOVI a5,1 at0x40250ace; a0 is dead until CALL0
# ec_tell_frac at0x40250afa. All other GPRs and SAR remain unchanged.
# Retain all three independent stack loads, including LM and end-1.
# OR deliberately takes3B so the replacement occupies exactly15B.
# No extra stack/RAM/table/helper; C fallback remains unchanged.
.section .text.patch0,"ax",@progbits
.begin no-transform
 or a5, a8, a8
 call0 ebands_init
 l32i a10, a1, 116
 l32i a9, a1, 428
 l32i a11, a1, 200
.end no-transform
