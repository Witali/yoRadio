# Experimental decoder-only quant_all_bands, accepted GCC ASM.
# LX106 call0 ABI; original384-byte frame, callee saves and all integer arithmetic.
# encode=0 follows the checked private native decoder contract, not bitrate.
# C and original saved GCC remain unchanged. RAM/stack/layout do not grow.
# Removed encoder instructions remain documented at their original labels.
.section .text.patch0,"ax",@progbits
.begin no-transform
pc402507d8:
movi a9, 0x180 # original0x402507d8
pc402507db:
sub a1, a1, a9 # original0x402507db
pc402507de:
movi.n a8, 0 # original0x402507de
pc402507e0:
l32i.n a9, a3, 24 # original0x402507e0
pc402507e2:
s32i a13, a1, 0x174 # original0x402507e2
pc402507e5:
s32i a14, a1, 0x170 # original0x402507e5
pc402507e8:
mov.n a13, a2 # original0x402507e8
pc402507ea:
movi.n a14, 1 # original0x402507ea
pc402507ec:
mov.n a2, a8 # original0x402507ec
pc402507ee:
moveqz a2, a14, a13 # original0x402507ee
pc402507f1:
s32i a4, a1, 224 # original0x402507f1
pc402507f4:
s32i a0, a1, 0x17c # original0x402507f4
pc402507f7:
s32i a12, a1, 0x178 # original0x402507f7
pc402507fa:
s32i a15, a1, 0x16c # original0x402507fa
pc402507fd:
s32i a3, a1, 232 # original0x402507fd
pc40250800:
s32i a7, a1, 176 # original0x40250800
pc40250803:
s32i a5, a1, 244 # original0x40250803
pc40250806:
s32i a6, a1, 0x124 # original0x40250806
pc40250809:
s32i a9, a1, 0x118 # original0x40250809
pc4025080c:
extui a4, a2, 0, 8 # original0x4025080c
pc4025080f:
bne a7, a8, pc40250815 # original0x4025080f
pc40250812:
j pc40252a09 # original0x40250812
pc40250815:
# decoder-unreachable/check: beq a13, a8, 4025083c <quant_all_bands+100>
pc40250818:
# decoder-unreachable/check: l32i a10, a1, 404
pc4025081b:
# decoder-unreachable/check: l32i a11, a1, 440
pc4025081e:
# decoder-unreachable/check: mov a2, a8
pc40250820:
# decoder-unreachable/check: moveqz a2, a14, a10
pc40250823:
# decoder-unreachable/check: bgei a11, 8, 40250828 <quant_all_bands+80>
pc40250826:
# decoder-unreachable/check: mov a14, a8
pc40250828:
# decoder-unreachable/check: and a14, a2, a14
pc4025082b:
# decoder-unreachable/check: or a12, a14, a4
pc4025082e:
# decoder-unreachable/check: movi a8, 2
pc40250830:
# decoder-unreachable/check: s32i a12, a1, 220
pc40250833:
# decoder-unreachable/check: s32i a8, a1, 204
pc40250836:
# decoder-unreachable/check: movi a12, 1
pc40250838:
# decoder-unreachable/check: j 40250848 <quant_all_bands+112>
pc4025083c:
movi.n a9, 2 # original0x4025083c
pc4025083e:
s32i a4, a1, 220 # original0x4025083e
pc40250841:
mov.n a14, a13 # original0x40250841
pc40250843:
s32i a9, a1, 204 # original0x40250843
pc40250846:
mov.n a12, a13 # original0x40250846
pc40250848:
s32i a4, a1, 0x15c # original0x40250848
pc4025084b:
call0 fixed_402428c4 # original0x4025084b
pc4025084e:
l32i a10, a1, 0x18c # original0x4025084e
pc40250851:
s32i a2, a1, 100 # original0x40250851
pc40250854:
s32i a3, a1, 104 # original0x40250854
pc40250857:
l32i a4, a1, 0x15c # original0x40250857
pc4025085a:
beqz.n a10, pc4025087c # original0x4025085a
pc4025085c:
l32i a11, a1, 0x1ac # original0x4025085c
pc4025085f:
movi.n a2, 1 # original0x4025085f
pc40250861:
ssl a11 # original0x40250861
pc40250864:
sll a11, a2 # original0x40250864
pc40250867:
s32i a11, a1, 180 # original0x40250867
pc4025086a:
bgei a11, 2, pc40250870 # original0x4025086a
pc4025086d:
movi a2, 0 # original0x4025086d
pc40250870:
extui a2, a2, 0, 8 # original0x40250870
pc40250873:
s32i a2, a1, 0x128 # original0x40250873
pc40250876:
s32i a2, a1, 0x18c # original0x40250876
pc40250879:
j pc40250884 # original0x40250879
pc4025087c:
movi.n a8, 1 # original0x4025087c
pc4025087e:
s32i a10, a1, 0x128 # original0x4025087e
pc40250881:
s32i a8, a1, 180 # original0x40250881
pc40250884:
l32i a9, a1, 232 # original0x40250884
pc40250887:
l32i a10, a1, 224 # original0x40250887
pc4025088a:
l32i.n a2, a9, 8 # original0x4025088a
pc4025088c:
l32r a11, fixed_4024f0d0 # original0x4025088c
pc4025088f:
l32i a8, a1, 0x118 # original0x4025088f
pc40250892:
slli a10, a10, 1 # original0x40250892
pc40250895:
add.n a2, a2, a11 # original0x40250895
pc40250897:
l32i a9, a1, 0x118 # original0x40250897
pc4025089a:
add.n a8, a8, a10 # original0x4025089a
pc4025089c:
slli a2, a2, 1 # original0x4025089c
pc4025089f:
s32i a10, a1, 0x134 # original0x4025089f
pc402508a2:
add.n a2, a9, a2 # original0x402508a2
pc402508a4:
l32i a10, a1, 0x1ac # original0x402508a4
pc402508a7:
l16si a3, a8, 0 # original0x402508a7
pc402508aa:
l16si a5, a2, 0 # original0x402508aa
pc402508ad:
ssl a10 # original0x402508ad
pc402508b0:
sll a3, a3 # original0x402508b0
pc402508b3:
ssl a10 # original0x402508b3
pc402508b6:
sll a5, a5 # original0x402508b6
pc402508b9:
s32i a8, a1, 0x120 # original0x402508b9
pc402508bc:
s32i a3, a1, 212 # original0x402508bc
pc402508bf:
sub a15, a5, a3 # original0x402508bf
pc402508c2:
beqz.n a4, pc402508e5 # original0x402508c2
pc402508c4:
srai a2, a15, 31 # original0x402508c4
pc402508c7:
l32i a11, a1, 0x1c8 # original0x402508c7
pc402508ca:
sub a2, a2, a15 # original0x402508ca
pc402508cd:
extui a2, a2, 31, 1 # original0x402508cd
pc402508d0:
movi.n a3, 1 # original0x402508d0
pc402508d2:
bge a11, a15, pc402508d8 # original0x402508d2
pc402508d5:
movi a3, 0 # original0x402508d5
pc402508d8:
bnone a2, a3, pc402508e0 # original0x402508d8
pc402508db:
l32i a8, a1, 0x1c4 # original0x402508db
pc402508de:
bnez.n a8, pc4025090d # original0x402508de
pc402508e0:
movi.n a2, 2 # original0x402508e0
pc402508e2:
j pc402508e8 # original0x402508e2
pc402508e5:
l32i a2, a1, 204 # original0x402508e5
pc402508e8:
mull a2, a15, a2 # original0x402508e8
pc402508eb:
movi a4, 0 # original0x402508eb
pc402508ee:
movi a3, 2 # original0x402508ee
pc402508f1:
call0 fixed_402428ec # original0x402508f1
pc402508f4:
slli a5, a15, 1 # original0x402508f4
pc402508f7:
add a5, a2, a5 # original0x402508f7
pc402508fa:
s32i a2, a1, 184 # original0x402508fa
pc402508fd:
s32i a5, a1, 0x1c4 # original0x402508fd
pc40250900:
beqz.n a12, pc4025091c # original0x40250900
pc40250902:
l32i a9, a1, 220 # original0x40250902
pc40250905:
j pc40250958 # original0x40250905
pc40250908:
# decoder-unreachable/check: j 4025091c <quant_all_bands+324>
pc4025090d:
movi a4, 0 # original0x4025090d
pc40250910:
movi a3, 2 # original0x40250910
pc40250913:
or a2, a15, a15 # original0x40250913
pc40250916:
call0 fixed_402428ec # original0x40250916
pc40250919:
s32i a2, a1, 184 # original0x40250919
pc4025091c:
movi a4, 0 # original0x4025091c
pc4025091f:
movi a3, 2 # original0x4025091f
pc40250922:
or a2, a4, a4 # original0x40250922
pc40250925:
call0 fixed_402428ec # original0x40250925
pc40250928:
l32i a10, a1, 232 # original0x40250928
pc4025092b:
l32r a11, fixed_4024f0d0 # original0x4025092b
pc4025092e:
l32i.n a2, a10, 12 # original0x4025092e
pc40250930:
l32i a8, a1, 0x118 # original0x40250930
pc40250933:
add.n a2, a2, a11 # original0x40250933
pc40250935:
slli a2, a2, 1 # original0x40250935
pc40250938:
add.n a2, a8, a2 # original0x40250938
pc4025093a:
l16si a2, a2, 0 # original0x4025093a
pc4025093d:
l32i a9, a1, 0x1ac # original0x4025093d
pc40250940:
l32i a10, a1, 0x124 # original0x40250940
pc40250943:
ssl a9 # original0x40250943
pc40250946:
sll a2, a2 # original0x40250946
pc40250949:
slli a2, a2, 1 # original0x40250949
pc4025094c:
add.n a2, a10, a2 # original0x4025094c
pc4025094e:
movi.n a12, 0 # original0x4025094e
pc40250950:
s32i a2, a1, 168 # original0x40250950
pc40250953:
j pc40250987 # original0x40250953
pc40250958:
l32i a11, a1, 232 # original0x40250958
pc4025095b:
l32i a12, a1, 0x118 # original0x4025095b
pc4025095e:
l32i.n a2, a11, 8 # original0x4025095e
pc40250960:
l32i a8, a1, 0x1ac # original0x40250960
pc40250963:
slli a2, a2, 1 # original0x40250963
pc40250966:
add.n a2, a12, a2 # original0x40250966
pc40250968:
addi a3, a2, -2 # original0x40250968
pc4025096b:
l16si a12, a2, 0 # original0x4025096b
pc4025096e:
l16si a2, a3, 0 # original0x4025096e
pc40250971:
movi.n a4, 0 # original0x40250971
pc40250973:
sub a12, a12, a2 # original0x40250973
pc40250976:
ssl a8 # original0x40250976
pc40250979:
sll a12, a12 # original0x40250979
pc4025097c:
movi.n a3, 2 # original0x4025097c
pc4025097e:
or a2, a12, a12 # original0x4025097e
pc40250981:
call0 fixed_402428ec # original0x40250981
pc40250984:
s32i a2, a1, 168 # original0x40250984
pc40250987:
movi.n a4, 0 # original0x40250987
pc40250989:
movi.n a3, 2 # original0x40250989
pc4025098b:
mov.n a2, a12 # original0x4025098b
pc4025098d:
call0 fixed_402428ec # original0x4025098d
pc40250990:
movi.n a4, 0 # original0x40250990
pc40250992:
movi.n a3, 2 # original0x40250992
pc40250994:
mov.n a2, a12 # original0x40250994
pc40250996:
call0 fixed_402428ec # original0x40250996
pc40250999:
movi.n a4, 0 # original0x40250999
pc4025099b:
movi.n a3, 2 # original0x4025099b
pc4025099d:
mov.n a2, a12 # original0x4025099d
pc4025099f:
call0 fixed_402428ec # original0x4025099f
pc402509a2:
movi.n a4, 0 # original0x402509a2
pc402509a4:
movi.n a3, 2 # original0x402509a4
pc402509a6:
mov.n a2, a12 # original0x402509a6
pc402509a8:
call0 fixed_402428ec # original0x402509a8
pc402509ab:
movi.n a4, 0 # original0x402509ab
pc402509ad:
movi.n a3, 2 # original0x402509ad
pc402509af:
mov.n a2, a12 # original0x402509af
pc402509b1:
call0 fixed_402428ec # original0x402509b1
pc402509b4:
l32i a3, a1, 0x184 # original0x402509b4
pc402509b7:
l32i a9, a1, 0x1b4 # original0x402509b7
pc402509ba:
s32i a3, a1, 68 # original0x402509ba
pc402509bd:
l32i a3, a1, 0x1bc # original0x402509bd
pc402509c0:
l32i a10, a1, 0x1a8 # original0x402509c0
pc402509c3:
l32i a11, a1, 0x198 # original0x402509c3
pc402509c6:
l32i.n a4, a9, 0 # original0x402509c6
pc402509c8:
l32i a12, a1, 232 # original0x402509c8
pc402509cb:
l32i a5, a1, 0x190 # original0x402509cb
pc402509ce:
s32i a3, a1, 76 # original0x402509ce
pc402509d1:
l32i a8, a1, 220 # original0x402509d1
pc402509d4:
l32i a3, a1, 0x1c0 # original0x402509d4
pc402509d7:
l32i a9, a1, 0x18c # original0x402509d7
pc402509da:
movi.n a2, 0 # original0x402509da
pc402509dc:
s32i.n a10, a1, 60 # original0x402509dc
pc402509de:
s32i.n a11, a1, 48 # original0x402509de
pc402509e0:
l32i a10, a1, 224 # original0x402509e0
pc402509e3:
l32i a11, a1, 244 # original0x402509e3
pc402509e6:
s32i.n a13, a1, 32 # original0x402509e6
pc402509e8:
s32i.n a12, a1, 40 # original0x402509e8
pc402509ea:
s32i a4, a1, 72 # original0x402509ea
pc402509ed:
s32i.n a5, a1, 52 # original0x402509ed
pc402509ef:
s32i a3, a1, 84 # original0x402509ef
pc402509f2:
s32i.n a8, a1, 36 # original0x402509f2
pc402509f4:
s32i a2, a1, 80 # original0x402509f4
pc402509f7:
s32i a9, a1, 88 # original0x402509f7
pc402509fa:
blt a10, a11, pc40250a00 # original0x402509fa
pc402509fd:
j pc40252844 # original0x402509fd
pc40250a00:
l32i a8, a1, 180 # original0x40250a00
pc40250a03:
movi.n a4, 1 # original0x40250a03
pc40250a05:
l32i a12, a1, 204 # original0x40250a05
pc40250a08:
ssl a8 # original0x40250a08
pc40250a0b:
sll a3, a4 # original0x40250a0b
pc40250a0e:
mull a12, a10, a12 # original0x40250a0e
pc40250a11:
l32i a9, a1, 204 # original0x40250a11
pc40250a14:
addi.n a3, a3, -1 # original0x40250a14
pc40250a16:
l32i a11, a1, 0x134 # original0x40250a16
pc40250a19:
s32i a3, a1, 208 # original0x40250a19
pc40250a1c:
s32i a12, a1, 248 # original0x40250a1c
pc40250a1f:
add.n a6, a9, a12 # original0x40250a1f
pc40250a21:
mov.n a15, a10 # original0x40250a21
pc40250a23:
slli a3, a10, 2 # original0x40250a23
pc40250a26:
addi.n a11, a11, 2 # original0x40250a26
pc40250a28:
l32i a10, a1, 180 # original0x40250a28
pc40250a2b:
l32i a12, a1, 0x134 # original0x40250a2b
pc40250a2e:
l32i a9, a1, 208 # original0x40250a2e
pc40250a31:
s32i a2, a1, 192 # original0x40250a31
pc40250a34:
s32i a11, a1, 0x148 # original0x40250a34
pc40250a37:
addi.n a2, a8, -1 # original0x40250a37
pc40250a39:
l32i a11, a1, 244 # original0x40250a39
pc40250a3c:
l32i a8, a1, 0x1ac # original0x40250a3c
pc40250a3f:
mov.n a7, a4 # original0x40250a3f
pc40250a41:
ssl a10 # original0x40250a41
pc40250a44:
sll a9, a9 # original0x40250a44
pc40250a47:
xor a4, a14, a4 # original0x40250a47
pc40250a4a:
addi.n a12, a12, 4 # original0x40250a4a
pc40250a4c:
s32i a12, a1, 0x14c # original0x40250a4c
pc40250a4f:
slli a8, a8, 3 # original0x40250a4f
pc40250a52:
s32i a9, a1, 0x150 # original0x40250a52
pc40250a55:
addi.n a11, a11, -1 # original0x40250a55
pc40250a57:
l32i a12, a1, 0x1b0 # original0x40250a57
pc40250a5a:
s32i a4, a1, 0x11c # original0x40250a5a
pc40250a5d:
l32i a14, a1, 224 # original0x40250a5d
pc40250a60:
l32i a9, a1, 0x180 # original0x40250a60
pc40250a63:
l32i a10, a1, 248 # original0x40250a63
pc40250a66:
l32i a4, a1, 0x188 # original0x40250a66
pc40250a69:
s32i a8, a1, 0x140 # original0x40250a69
pc40250a6c:
s32i a11, a1, 200 # original0x40250a6c
pc40250a6f:
l32i a8, a1, 0x120 # original0x40250a6f
pc40250a72:
l32i a11, a1, 184 # original0x40250a72
pc40250a75:
addi.n a12, a12, -1 # original0x40250a75
pc40250a77:
add.n a14, a14, a7 # original0x40250a77
pc40250a79:
add.n a9, a9, a10 # original0x40250a79
pc40250a7b:
add a3, a4, a3 # original0x40250a7b
pc40250a7e:
addi.n a6, a6, -1 # original0x40250a7e
pc40250a80:
s32i a14, a1, 0x104 # original0x40250a80
pc40250a83:
s32i a12, a1, 0x108 # original0x40250a83
pc40250a86:
s32i a8, a1, 144 # original0x40250a86
pc40250a89:
s32i a9, a1, 156 # original0x40250a89
pc40250a8c:
s32i a3, a1, 164 # original0x40250a8c
pc40250a8f:
s32i a6, a1, 0x10c # original0x40250a8f
pc40250a92:
s32i a11, a1, 0x12c # original0x40250a92
pc40250a95:
l32i a12, a1, 192 # original0x40250a95
pc40250a98:
l32i a14, a1, 192 # original0x40250a98
pc40250a9b:
addi a5, a5, -3 # original0x40250a9b
pc40250a9e:
moveqz a14, a7, a2 # original0x40250a9e
pc40250aa1:
movnez a12, a7, a5 # original0x40250aa1
pc40250aa4:
s32i a14, a1, 0x144 # original0x40250aa4
pc40250aa7:
s32i a12, a1, 0x130 # original0x40250aa7
pc40250aaa:
or a14, a7, a7 # original0x40250aaa
pc40250aad:
s32i a15, a1, 116 # original0x40250aad
pc40250ab0:
l32i a8, a1, 144 # original0x40250ab0
pc40250ab3:
l32i a10, a1, 116 # original0x40250ab3
pc40250ab6:
l16si a2, a8, 0 # original0x40250ab6
pc40250ab9:
l32i a9, a1, 0x1ac # original0x40250ab9
pc40250abc:
l32i a11, a1, 200 # original0x40250abc
pc40250abf:
l16si a3, a8, 2 # original0x40250abf
pc40250ac2:
sub a12, a10, a11 # original0x40250ac2
pc40250ac5:
l32i a8, a1, 176 # original0x40250ac5
pc40250ac8:
ssl a9 # original0x40250ac8
pc40250acb:
sll a13, a2 # original0x40250acb
pc40250ace:
movi a5, 1 # original0x40250ace
pc40250ad1:
movi a4, 0 # original0x40250ad1
pc40250ad4:
moveqz a4, a5, a12 # original0x40250ad4
pc40250ad7:
s32i a10, a1, 44 # original0x40250ad7
pc40250ada:
slli a13, a13, 1 # original0x40250ada
pc40250add:
l32i a10, a1, 0x1ac # original0x40250add
pc40250ae0:
mov.n a12, a4 # original0x40250ae0
pc40250ae2:
sub a3, a3, a2 # original0x40250ae2
pc40250ae5:
add.n a4, a8, a13 # original0x40250ae5
pc40250ae7:
l32i a2, a1, 0x1a8 # original0x40250ae7
pc40250aea:
movi.n a9, 0 # original0x40250aea
pc40250aec:
movnez a9, a4, a8 # original0x40250aec
pc40250aef:
ssl a10 # original0x40250aef
pc40250af2:
sll a3, a3 # original0x40250af2
pc40250af5:
mov.n a15, a9 # original0x40250af5
pc40250af7:
s32i a3, a1, 128 # original0x40250af7
pc40250afa:
call0 fixed_40246830 # original0x40250afa
pc40250afd:
l32i a11, a1, 224 # original0x40250afd
pc40250b00:
l32i a8, a1, 116 # original0x40250b00
pc40250b03:
s32i a2, a1, 160 # original0x40250b03
pc40250b06:
extui a12, a12, 0, 8 # original0x40250b06
pc40250b09:
beq a11, a8, pc40250b15 # original0x40250b09
pc40250b0c:
l32i a9, a1, 0x1a4 # original0x40250b0c
pc40250b0f:
sub a9, a9, a2 # original0x40250b0f
pc40250b12:
s32i a9, a1, 0x1a4 # original0x40250b12
pc40250b15:
l32i a10, a1, 0x1a0 # original0x40250b15
pc40250b18:
l32i a11, a1, 160 # original0x40250b18
pc40250b1b:
movi.n a8, 0 # original0x40250b1b
pc40250b1d:
sub a4, a10, a11 # original0x40250b1d
pc40250b20:
addi.n a2, a4, -1 # original0x40250b20
pc40250b22:
l32i a9, a1, 0x108 # original0x40250b22
pc40250b25:
l32i a10, a1, 116 # original0x40250b25
pc40250b28:
s32i a2, a1, 64 # original0x40250b28
pc40250b2b:
s32i a8, a1, 136 # original0x40250b2b
pc40250b2e:
blt a9, a10, pc40250b70 # original0x40250b2e
pc40250b31:
l32i a11, a1, 0x1b0 # original0x40250b31
pc40250b34:
sub a3, a11, a10 # original0x40250b34
pc40250b37:
blti a3, 4, pc40250b3d # original0x40250b37
pc40250b3a:
movi a3, 3 # original0x40250b3a
pc40250b3d:
l32i a2, a1, 0x1a4 # original0x40250b3d
pc40250b40:
s32i a4, a1, 0x15c # original0x40250b40
pc40250b43:
l32r a0, fixed_4024f100 # original0x40250b43
pc40250b46:
callx0 a0 # original0x40250b46
pc40250b49:
l32i a8, a1, 164 # original0x40250b49
pc40250b4c:
l32r a5, fixed_40250794 # original0x40250b4c
pc40250b4f:
l32i.n a3, a8, 0 # original0x40250b4f
pc40250b51:
l32i a4, a1, 0x15c # original0x40250b51
pc40250b54:
add.n a2, a2, a3 # original0x40250b54
pc40250b56:
bge a5, a4, pc40250b5c # original0x40250b56
pc40250b59:
or a4, a5, a5 # original0x40250b59
pc40250b5c:
s32i a2, a1, 136 # original0x40250b5c
pc40250b5f:
bge a4, a2, pc40250b65 # original0x40250b5f
pc40250b62:
s32i a4, a1, 136 # original0x40250b62
pc40250b65:
l32i a10, a1, 136 # original0x40250b65
pc40250b68:
movi.n a9, 0 # original0x40250b68
pc40250b6a:
movgez a9, a10, a10 # original0x40250b6a
pc40250b6d:
s32i a9, a1, 136 # original0x40250b6d
pc40250b70:
l32i a11, a1, 220 # original0x40250b70
pc40250b73:
# decoder-unreachable/check: beqz a11, 40250bb7 <quant_all_bands+991>
pc40250b76:
l32i a8, a1, 144 # original0x40250b76
pc40250b79:
l32i a9, a1, 0x120 # original0x40250b79
pc40250b7c:
l32i a10, a1, 0x1ac # original0x40250b7c
pc40250b7f:
l16si a2, a8, 0 # original0x40250b7f
pc40250b82:
l16si a3, a9, 0 # original0x40250b82
pc40250b85:
l32i a11, a1, 128 # original0x40250b85
pc40250b88:
ssl a10 # original0x40250b88
pc40250b8b:
sll a2, a2 # original0x40250b8b
pc40250b8e:
sub a2, a2, a11 # original0x40250b8e
pc40250b91:
ssl a10 # original0x40250b91
pc40250b94:
sll a3, a3 # original0x40250b94
pc40250b97:
bge a2, a3, pc40250ba9 # original0x40250b97
pc40250b9a:
l32i a8, a1, 116 # original0x40250b9a
pc40250b9d:
l32i a9, a1, 0x104 # original0x40250b9d
pc40250ba0:
beq a8, a9, pc40250ba6 # original0x40250ba0
pc40250ba3:
j pc40250c2d # original0x40250ba3
pc40250ba6:
j pc40252acf # original0x40250ba6
pc40250ba9:
l32i a10, a1, 192 # original0x40250ba9
pc40250bac:
beqz.n a10, pc40250bb1 # original0x40250bac
pc40250bae:
bbci a14, 0, pc40250bb7 # original0x40250bae
pc40250bb1:
l32i a11, a1, 116 # original0x40250bb1
pc40250bb4:
s32i a11, a1, 192 # original0x40250bb4
pc40250bb7:
l32i a14, a1, 116 # original0x40250bb7
pc40250bba:
l32i a8, a1, 0x104 # original0x40250bba
pc40250bbd:
bne a14, a8, pc40250c2d # original0x40250bbd
pc40250bc0:
l32i a9, a1, 232 # original0x40250bc0
pc40250bc3:
l32i a10, a1, 0x148 # original0x40250bc3
pc40250bc6:
l32i a3, a9, 24 # original0x40250bc6
pc40250bc9:
l32i a11, a1, 0x134 # original0x40250bc9
pc40250bcc:
l32i a8, a1, 0x14c # original0x40250bcc
pc40250bcf:
add a2, a3, a11 # original0x40250bcf
pc40250bd2:
add.n a4, a3, a10 # original0x40250bd2
pc40250bd4:
l16si a4, a4, 0 # original0x40250bd4
pc40250bd7:
l16si a14, a2, 0 # original0x40250bd7
pc40250bda:
add.n a3, a3, a8 # original0x40250bda
pc40250bdc:
l16si a2, a3, 0 # original0x40250bdc
pc40250bdf:
l32i a9, a1, 0x1ac # original0x40250bdf
pc40250be2:
sub a14, a4, a14 # original0x40250be2
pc40250be5:
ssl a9 # original0x40250be5
pc40250be8:
sll a14, a14 # original0x40250be8
pc40250beb:
sub a2, a2, a4 # original0x40250beb
pc40250bee:
slli a7, a14, 1 # original0x40250bee
pc40250bf1:
ssl a9 # original0x40250bf1
pc40250bf4:
sll a2, a2 # original0x40250bf4
pc40250bf7:
sub a6, a7, a2 # original0x40250bf7
pc40250bfa:
l32i a10, a1, 184 # original0x40250bfa
pc40250bfd:
slli a6, a6, 1 # original0x40250bfd
pc40250c00:
sub a14, a2, a14 # original0x40250c00
pc40250c03:
add.n a3, a10, a6 # original0x40250c03
pc40250c05:
add.n a2, a10, a7 # original0x40250c05
pc40250c07:
movi.n a5, 2 # original0x40250c07
pc40250c09:
mov.n a4, a14 # original0x40250c09
pc40250c0b:
s32i a6, a1, 0x158 # original0x40250c0b
pc40250c0e:
s32i a7, a1, 0x154 # original0x40250c0e
pc40250c11:
call0 fixed_402429b0 # original0x40250c11
pc40250c14:
l32i a11, a1, 0x194 # original0x40250c14
pc40250c17:
l32i a6, a1, 0x158 # original0x40250c17
pc40250c1a:
l32i a7, a1, 0x154 # original0x40250c1a
pc40250c1d:
beqz.n a11, pc40250c2d # original0x40250c1d
pc40250c1f:
mov.n a4, a14 # original0x40250c1f
pc40250c21:
l32i a14, a1, 0x1c4 # original0x40250c21
pc40250c24:
movi.n a5, 2 # original0x40250c24
pc40250c26:
add.n a3, a14, a6 # original0x40250c26
pc40250c28:
add.n a2, a14, a7 # original0x40250c28
pc40250c2a:
call0 fixed_402429b0 # original0x40250c2a
pc40250c2d:
l32i a8, a1, 116 # original0x40250c2d
pc40250c30:
l32i a9, a1, 0x19c # original0x40250c30
pc40250c33:
slli a2, a8, 2 # original0x40250c33
pc40250c36:
add.n a2, a9, a2 # original0x40250c36
pc40250c38:
l32i a10, a1, 232 # original0x40250c38
pc40250c3b:
l32i.n a2, a2, 0 # original0x40250c3b
pc40250c3d:
l32i.n a3, a10, 12 # original0x40250c3d
pc40250c3f:
s32i.n a2, a1, 56 # original0x40250c3f
pc40250c41:
bge a8, a3, pc40250c50 # original0x40250c41
pc40250c44:
l32i a11, a1, 0x124 # original0x40250c44
pc40250c47:
add.n a13, a11, a13 # original0x40250c47
pc40250c49:
s32i a13, a1, 172 # original0x40250c49
pc40250c4c:
j pc40250c64 # original0x40250c4c
pc40250c50:
l32i a14, a1, 176 # original0x40250c50
pc40250c53:
l32i a8, a1, 184 # original0x40250c53
pc40250c56:
l32i a9, a1, 0x12c # original0x40250c56
pc40250c59:
movi.n a10, 0 # original0x40250c59
pc40250c5b:
movnez a15, a8, a14 # original0x40250c5b
pc40250c5e:
s32i a9, a1, 172 # original0x40250c5e
pc40250c61:
s32i a10, a1, 168 # original0x40250c61
pc40250c64:
beqz.n a12, pc40250c74 # original0x40250c64
pc40250c66:
l32i a14, a1, 168 # original0x40250c66
pc40250c69:
l32i a12, a1, 0x11c # original0x40250c69
pc40250c6c:
movi.n a11, 0 # original0x40250c6c
pc40250c6e:
moveqz a11, a14, a12 # original0x40250c6e
pc40250c71:
s32i a11, a1, 168 # original0x40250c71
pc40250c74:
l32i a8, a1, 192 # original0x40250c74
pc40250c77:
beqz a8, pc40250d1c # original0x40250c77
pc40250c7a:
l32i a9, a1, 0x128 # original0x40250c7a
pc40250c7d:
l32i a10, a1, 0x130 # original0x40250c7d
pc40250c80:
or a3, a9, a10 # original0x40250c80
pc40250c83:
bnez.n a3, pc40250c88 # original0x40250c83
pc40250c85:
bgez a2, pc40250d1c # original0x40250c85
pc40250c88:
l32i a11, a1, 192 # original0x40250c88
pc40250c8b:
l32i a12, a1, 0x118 # original0x40250c8b
pc40250c8e:
slli a5, a11, 1 # original0x40250c8e
pc40250c91:
add.n a5, a12, a5 # original0x40250c91
pc40250c93:
l32i a14, a1, 212 # original0x40250c93
pc40250c96:
l32i a8, a1, 128 # original0x40250c96
pc40250c99:
l32i a9, a1, 0x1ac # original0x40250c99
pc40250c9c:
l16si a7, a5, 0 # original0x40250c9c
pc40250c9f:
add.n a13, a14, a8 # original0x40250c9f
pc40250ca1:
ssl a9 # original0x40250ca1
pc40250ca4:
sll a7, a7 # original0x40250ca4
pc40250ca7:
sub a13, a7, a13 # original0x40250ca7
pc40250caa:
addi.n a3, a11, -1 # original0x40250caa
pc40250cac:
movi.n a10, 0 # original0x40250cac
pc40250cae:
movltz a13, a10, a13 # original0x40250cae
pc40250cb1:
slli a7, a3, 1 # original0x40250cb1
pc40250cb4:
add.n a6, a14, a13 # original0x40250cb4
pc40250cb6:
add.n a7, a12, a7 # original0x40250cb6
pc40250cb8:
mov.n a2, a11 # original0x40250cb8
pc40250cba:
or a8, a9, a9 # original0x40250cba
pc40250cbd:
l16si a4, a7, 0 # original0x40250cbd
pc40250cc0:
addi.n a2, a2, -1 # original0x40250cc0
pc40250cc2:
ssl a8 # original0x40250cc2
pc40250cc5:
sll a4, a4 # original0x40250cc5
pc40250cc8:
addi a7, a7, -2 # original0x40250cc8
pc40250ccb:
blt a6, a4, pc40250cbd # original0x40250ccb
pc40250cce:
l32i a11, a1, 128 # original0x40250cce
pc40250cd1:
l32i a7, a1, 116 # original0x40250cd1
pc40250cd4:
l32i a8, a1, 0x1ac # original0x40250cd4
pc40250cd7:
add.n a6, a11, a6 # original0x40250cd7
pc40250cd9:
addi.n a3, a3, 1 # original0x40250cd9
pc40250cdb:
bge a3, a7, pc40250cec # original0x40250cdb
pc40250cde:
l16si a4, a5, 0 # original0x40250cde
pc40250ce1:
addi.n a5, a5, 2 # original0x40250ce1
pc40250ce3:
ssl a8 # original0x40250ce3
pc40250ce6:
sll a4, a4 # original0x40250ce6
pc40250ce9:
blt a4, a6, pc40250cd9 # original0x40250ce9
pc40250cec:
l32i a12, a1, 204 # original0x40250cec
pc40250cef:
l32i a10, a1, 0x180 # original0x40250cef
pc40250cf2:
mull a9, a2, a12 # original0x40250cf2
pc40250cf5:
movi.n a14, 0 # original0x40250cf5
pc40250cf7:
add.n a8, a12, a9 # original0x40250cf7
pc40250cf9:
add.n a4, a10, a9 # original0x40250cf9
pc40250cfb:
mov.n a6, a14 # original0x40250cfb
pc40250cfd:
addi.n a8, a8, -1 # original0x40250cfd
pc40250cff:
mov.n a10, a12 # original0x40250cff
pc40250d01:
sub a5, a4, a9 # original0x40250d01
pc40250d04:
add.n a5, a5, a8 # original0x40250d04
pc40250d06:
l8ui a7, a4, 0 # original0x40250d06
pc40250d09:
l8ui a5, a5, 0 # original0x40250d09
pc40250d0c:
addi.n a2, a2, 1 # original0x40250d0c
pc40250d0e:
or a6, a6, a7 # original0x40250d0e
pc40250d11:
or a14, a14, a5 # original0x40250d11
pc40250d14:
add.n a4, a4, a10 # original0x40250d14
pc40250d16:
blt a2, a3, pc40250d01 # original0x40250d16
pc40250d19:
j pc40250d23 # original0x40250d19
pc40250d1c:
l32i a14, a1, 208 # original0x40250d1c
pc40250d1f:
movi.n a13, -1 # original0x40250d1f
pc40250d21:
mov.n a6, a14 # original0x40250d21
pc40250d23:
l32i a11, a1, 0x194 # original0x40250d23
pc40250d26:
beqz a11, pc40250d88 # original0x40250d26
pc40250d29:
l32i a12, a1, 0x198 # original0x40250d29
pc40250d2c:
l32i a8, a1, 116 # original0x40250d2c
pc40250d2f:
bne a12, a8, pc40250d88 # original0x40250d2f
pc40250d32:
l32i a9, a1, 220 # original0x40250d32
pc40250d35:
# decoder-unreachable/check: beqz a9, 40250e49 <quant_all_bands+1649>
pc40250d38:
l32i a10, a1, 144 # original0x40250d38
pc40250d3b:
l32i a11, a1, 0x1ac # original0x40250d3b
pc40250d3e:
l16si a2, a10, 0 # original0x40250d3e
pc40250d41:
l32i a12, a1, 212 # original0x40250d41
pc40250d44:
ssl a11 # original0x40250d44
pc40250d47:
sll a2, a2 # original0x40250d47
pc40250d4a:
sub a2, a2, a12 # original0x40250d4a
pc40250d4d:
bgei a2, 1, pc40250d53 # original0x40250d4d
pc40250d50:
j pc40250e49 # original0x40250d50
pc40250d53:
l32i a3, a1, 184 # original0x40250d53
pc40250d56:
l32i a5, a1, 0x1c4 # original0x40250d56
pc40250d59:
movi.n a4, 0 # original0x40250d59
pc40250d5b:
mov.n a7, a12 # original0x40250d5b
pc40250d5d:
mov.n a8, a10 # original0x40250d5d
pc40250d5f:
mov.n a9, a11 # original0x40250d5f
pc40250d61:
l16si a2, a3, 0 # original0x40250d61
pc40250d64:
l16si a10, a5, 0 # original0x40250d64
pc40250d67:
addi.n a4, a4, 1 # original0x40250d67
pc40250d69:
add.n a2, a2, a10 # original0x40250d69
pc40250d6b:
srai a2, a2, 1 # original0x40250d6b
pc40250d6e:
s16i a2, a3, 0 # original0x40250d6e
pc40250d71:
l16si a2, a8, 0 # original0x40250d71
pc40250d74:
addi.n a3, a3, 2 # original0x40250d74
pc40250d76:
ssl a9 # original0x40250d76
pc40250d79:
sll a2, a2 # original0x40250d79
pc40250d7c:
sub a2, a2, a7 # original0x40250d7c
pc40250d7f:
addi.n a5, a5, 2 # original0x40250d7f
pc40250d81:
blt a4, a2, pc40250d61 # original0x40250d81
pc40250d84:
j pc40250e49 # original0x40250d84
pc40250d88:
l32i a8, a1, 0x194 # original0x40250d88
pc40250d8b:
beqz a8, pc40250e49 # original0x40250d8b
pc40250d8e:
l32i a9, a1, 136 # original0x40250d8e
pc40250d91:
srai a8, a9, 1 # original0x40250d91
pc40250d94:
bnei a13, -1, pc40250d9a # original0x40250d94
pc40250d97:
j pc40252bec # original0x40250d97
pc40250d9a:
l32i a10, a1, 184 # original0x40250d9a
pc40250d9d:
l32i a11, a1, 116 # original0x40250d9d
pc40250da0:
l32i a12, a1, 200 # original0x40250da0
pc40250da3:
slli a13, a13, 1 # original0x40250da3
pc40250da6:
add.n a7, a10, a13 # original0x40250da6
pc40250da8:
bne a11, a12, pc40250dae # original0x40250da8
pc40250dab:
j pc40252c15 # original0x40250dab
pc40250dae:
l32r a9, fixed_4024f0bc # original0x40250dae
pc40250db1:
l32i a10, a1, 168 # original0x40250db1
pc40250db4:
l32i a11, a1, 144 # original0x40250db4
pc40250db7:
s32i.n a6, a1, 16 # original0x40250db7
pc40250db9:
s32i.n a10, a1, 12 # original0x40250db9
pc40250dbb:
s32i.n a9, a1, 8 # original0x40250dbb
pc40250dbd:
l16si a2, a11, 0 # original0x40250dbd
pc40250dc0:
s32i a9, a1, 140 # original0x40250dc0
pc40250dc3:
l32i a9, a1, 0x1ac # original0x40250dc3
pc40250dc6:
l32i a10, a1, 212 # original0x40250dc6
pc40250dc9:
ssl a9 # original0x40250dc9
pc40250dcc:
sll a2, a2 # original0x40250dcc
pc40250dcf:
sub a2, a2, a10 # original0x40250dcf
pc40250dd2:
l32i a11, a1, 184 # original0x40250dd2
pc40250dd5:
slli a2, a2, 1 # original0x40250dd5
pc40250dd8:
addi a12, a1, 32 # original0x40250dd8
pc40250ddb:
add.n a2, a11, a2 # original0x40250ddb
pc40250ddd:
l32i a6, a1, 180 # original0x40250ddd
pc40250de0:
l32i a4, a1, 128 # original0x40250de0
pc40250de3:
l32i a3, a1, 172 # original0x40250de3
pc40250de6:
s32i.n a2, a1, 4 # original0x40250de6
pc40250de8:
s32i.n a9, a1, 0 # original0x40250de8
pc40250dea:
mov.n a5, a8 # original0x40250dea
pc40250dec:
mov.n a2, a12 # original0x40250dec
pc40250dee:
s32i a12, a1, 132 # original0x40250dee
pc40250df1:
s32i a8, a1, 0x154 # original0x40250df1
pc40250df4:
call0 fixed_4024e44c # original0x40250df4
pc40250df7:
l32i a9, a1, 0x1c4 # original0x40250df7
pc40250dfa:
l32i a8, a1, 0x154 # original0x40250dfa
pc40250dfd:
mov.n a12, a2 # original0x40250dfd
pc40250dff:
add.n a7, a9, a13 # original0x40250dff
pc40250e01:
l32i a10, a1, 144 # original0x40250e01
pc40250e04:
l32i a11, a1, 0x1ac # original0x40250e04
pc40250e07:
l16si a2, a10, 0 # original0x40250e07
pc40250e0a:
l32i a9, a1, 212 # original0x40250e0a
pc40250e0d:
ssl a11 # original0x40250e0d
pc40250e10:
sll a2, a2 # original0x40250e10
pc40250e13:
sub a2, a2, a9 # original0x40250e13
pc40250e16:
l32i a10, a1, 0x1c4 # original0x40250e16
pc40250e19:
slli a2, a2, 1 # original0x40250e19
pc40250e1c:
add.n a2, a10, a2 # original0x40250e1c
pc40250e1e:
mov.n a9, a11 # original0x40250e1e
pc40250e20:
s32i.n a14, a1, 16 # original0x40250e20
pc40250e22:
l32i a11, a1, 168 # original0x40250e22
pc40250e25:
l32i a14, a1, 140 # original0x40250e25
pc40250e28:
s32i.n a2, a1, 4 # original0x40250e28
pc40250e2a:
l32i a6, a1, 180 # original0x40250e2a
pc40250e2d:
l32i a4, a1, 128 # original0x40250e2d
pc40250e30:
l32i a2, a1, 132 # original0x40250e30
pc40250e33:
s32i.n a11, a1, 12 # original0x40250e33
pc40250e35:
s32i.n a14, a1, 8 # original0x40250e35
pc40250e37:
s32i.n a9, a1, 0 # original0x40250e37
pc40250e39:
mov.n a5, a8 # original0x40250e39
pc40250e3b:
mov.n a3, a15 # original0x40250e3b
pc40250e3d:
call0 fixed_4024e44c # original0x40250e3d
pc40250e40:
extui a12, a12, 0, 8 # original0x40250e40
pc40250e43:
extui a2, a2, 0, 8 # original0x40250e43
pc40250e46:
j pc402527d6 # original0x40250e46
pc40250e49:
bnez.n a15, pc40250e4e # original0x40250e49
pc40250e4b:
j pc40252770 # original0x40250e4b
pc40250e4e:
movi.n a10, 0 # original0x40250e4e
pc40250e50:
s32i a10, a1, 80 # original0x40250e50
pc40250e53:
s32i a10, a1, 152 # original0x40250e53
pc40250e56:
beqi a13, -1, pc40250e64 # original0x40250e56
pc40250e59:
l32i a12, a1, 184 # original0x40250e59
pc40250e5c:
slli a13, a13, 1 # original0x40250e5c
pc40250e5f:
add.n a13, a12, a13 # original0x40250e5f
pc40250e61:
s32i a13, a1, 152 # original0x40250e61
pc40250e64:
movi.n a8, 0 # original0x40250e64
pc40250e66:
l32i a9, a1, 116 # original0x40250e66
pc40250e69:
l32i a10, a1, 200 # original0x40250e69
pc40250e6c:
s32i a8, a1, 236 # original0x40250e6c
pc40250e6f:
beq a9, a10, pc40250e92 # original0x40250e6f
pc40250e72:
l32i a11, a1, 144 # original0x40250e72
pc40250e75:
l32i a12, a1, 0x1ac # original0x40250e75
pc40250e78:
l16si a2, a11, 0 # original0x40250e78
pc40250e7b:
l32i a8, a1, 212 # original0x40250e7b
pc40250e7e:
ssl a12 # original0x40250e7e
pc40250e81:
sll a2, a2 # original0x40250e81
pc40250e84:
sub a2, a2, a8 # original0x40250e84
pc40250e87:
l32i a9, a1, 184 # original0x40250e87
pc40250e8a:
slli a2, a2, 1 # original0x40250e8a
pc40250e8d:
add.n a2, a9, a2 # original0x40250e8d
pc40250e8f:
s32i a2, a1, 236 # original0x40250e8f
pc40250e92:
l32i.n a10, a1, 32 # original0x40250e92
pc40250e94:
or a14, a6, a14 # original0x40250e94
pc40250e97:
l32i a11, a1, 128 # original0x40250e97
pc40250e9a:
s32i a14, a1, 112 # original0x40250e9a
pc40250e9d:
s32i a10, a1, 240 # original0x40250e9d
pc40250ea0:
l32i.n a14, a1, 60 # original0x40250ea0
pc40250ea2:
beqi a11, 1, pc40250ea8 # original0x40250ea2
pc40250ea5:
j pc40250f66 # original0x40250ea5
pc40250ea8:
l32i a12, a1, 172 # original0x40250ea8
pc40250eab:
movi.n a13, 2 # original0x40250eab
pc40250ead:
l32i a3, a1, 64 # original0x40250ead
pc40250eb0:
# decoder-unreachable/check: bnez a10, 40250f00 <quant_all_bands+1832>
pc40250eb3:
j pc40250eb8 # original0x40250eb3
pc40250eb6:
movi.n a13, 1 # original0x40250eb6
pc40250eb8:
bgei a3, 8, pc40250ed2 # original0x40250eb8
pc40250ebb:
j pc40250ef3 # original0x40250ebb
pc40250ec0:
s16i a4, a12, 0 # original0x40250ec0
pc40250ec3:
j pc40250ef8 # original0x40250ec3
pc40250ec6:
l32r a4, fixed_40250790 # original0x40250ec6
pc40250ec9:
bnez a2, pc40250ec0 # original0x40250ec9
pc40250ecc:
j pc40250eed # original0x40250ecc
pc40250ed2:
movi a3, 1 # original0x40250ed2
pc40250ed5:
or a2, a14, a14 # original0x40250ed5
pc40250ed8:
call0 fixed_40298548 # original0x40250ed8
pc40250edb:
l32i a3, a1, 64 # original0x40250edb
pc40250ede:
l32i a4, a1, 36 # original0x40250ede
pc40250ee1:
addi a3, a3, -8 # original0x40250ee1
pc40250ee4:
s32i a3, a1, 64 # original0x40250ee4
pc40250ee7:
j pc40250ec6 # original0x40250ee7
pc40250eea:
# decoder-unreachable/check: j 40250ef8 <quant_all_bands+1824>
pc40250eed:
l32r a4, fixed_4024f0f4 # original0x40250eed
pc40250ef0:
j pc40250ec0 # original0x40250ef0
pc40250ef3:
l32i.n a2, a1, 36 # original0x40250ef3
pc40250ef5:
j pc40250eed # original0x40250ef5
pc40250ef8:
mov.n a12, a15 # original0x40250ef8
pc40250efa:
bnei a13, 1, pc40250eb6 # original0x40250efa
pc40250efd:
j pc40250f47 # original0x40250efd
pc40250f00:
# decoder-unreachable/check: mov a5, a14
pc40250f02:
# decoder-unreachable/check: j 40250f07 <quant_all_bands+1839>
pc40250f05:
# decoder-unreachable/check: movi a13, 1
pc40250f07:
# decoder-unreachable/check: movi a4, 1
pc40250f09:
# decoder-unreachable/check: or a2, a5, a5
pc40250f0c:
# decoder-unreachable/check: bgei a3, 8, 40250f1d <quant_all_bands+1861>
pc40250f0f:
# decoder-unreachable/check: l32i a2, a1, 36
pc40250f12:
# decoder-unreachable/check: beqz a2, 40250f42 <quant_all_bands+1898>
pc40250f14:
# decoder-unreachable/check: l32r a2, 4024f0f4 <anti_collapse+996>
pc40250f17:
# decoder-unreachable/check: j 40250f3f <quant_all_bands+1895>
pc40250f1d:
# decoder-unreachable/check: l16si a14, a12, 0
pc40250f20:
# decoder-unreachable/check: s32i a5, a1, 344
pc40250f23:
# decoder-unreachable/check: extui a3, a14, 31, 1
pc40250f26:
# decoder-unreachable/check: call0 40298c90 <ec_enc_bits>
pc40250f29:
# decoder-unreachable/check: l32i a3, a1, 64
pc40250f2c:
# decoder-unreachable/check: l32i a2, a1, 36
pc40250f2e:
# decoder-unreachable/check: addi a3, a3, -8
pc40250f31:
# decoder-unreachable/check: s32i a3, a1, 64
pc40250f34:
# decoder-unreachable/check: l32i a5, a1, 344
pc40250f37:
# decoder-unreachable/check: beqz a2, 40250f42 <quant_all_bands+1898>
pc40250f39:
# decoder-unreachable/check: bgez a14, 40250f14 <quant_all_bands+1852>
pc40250f3c:
# decoder-unreachable/check: l32r a2, 40250790 <anti_collapse+6784>
pc40250f3f:
# decoder-unreachable/check: s16i a2, a12, 0
pc40250f42:
# decoder-unreachable/check: mov a12, a15
pc40250f44:
# decoder-unreachable/check: bnei a13, 1, 40250f05 <quant_all_bands+1837>
pc40250f47:
l32i a14, a1, 236 # original0x40250f47
pc40250f4a:
movi.n a12, 1 # original0x40250f4a
pc40250f4c:
bnez.n a14, pc40250f51 # original0x40250f4c
pc40250f4e:
j pc40252766 # original0x40250f4e
pc40250f51:
l32i a8, a1, 172 # original0x40250f51
pc40250f54:
l16ui a2, a8, 0 # original0x40250f54
pc40250f57:
slli a2, a2, 16 # original0x40250f57
pc40250f5a:
srai a2, a2, 20 # original0x40250f5a
pc40250f5d:
s16i a2, a14, 0 # original0x40250f5d
pc40250f60:
j pc40252766 # original0x40250f60
pc40250f66:
l32i.n a9, a1, 40 # original0x40250f66
pc40250f68:
l32i.n a10, a1, 44 # original0x40250f68
pc40250f6a:
l32i.n a2, a9, 48 # original0x40250f6a
pc40250f6c:
slli a3, a10, 1 # original0x40250f6c
pc40250f6f:
add.n a2, a2, a3 # original0x40250f6f
pc40250f71:
l16si a12, a2, 0 # original0x40250f71
pc40250f74:
l32i a11, a1, 0x140 # original0x40250f74
pc40250f77:
l32i a8, a1, 68 # original0x40250f77
pc40250f7a:
s32i a9, a1, 124 # original0x40250f7a
pc40250f7d:
l32i a9, a1, 128 # original0x40250f7d
pc40250f80:
add.n a12, a12, a11 # original0x40250f80
pc40250f82:
s32i a10, a1, 120 # original0x40250f82
pc40250f85:
s32i a8, a1, 140 # original0x40250f85
pc40250f88:
l32i.n a4, a1, 48 # original0x40250f88
pc40250f8a:
srai a2, a12, 1 # original0x40250f8a
pc40250f8d:
bnei a9, 2, pc40250f93 # original0x40250f8d
pc40250f90:
j pc40252abc # original0x40250f90
pc40250f93:
j pc40252ac4 # original0x40250f93
pc40250f97:
mull a2, a3, a2 # original0x40250f97
pc40250f9a:
l32i a10, a1, 136 # original0x40250f9a
pc40250f9d:
s32i a4, a1, 0x15c # original0x40250f9d
pc40250fa0:
add.n a2, a2, a10 # original0x40250fa0
pc40250fa2:
l32r a0, fixed_4024f100 # original0x40250fa2
pc40250fa5:
callx0 a0 # original0x40250fa5
pc40250fa8:
l32i a11, a1, 136 # original0x40250fa8
pc40250fab:
l32i a4, a1, 0x15c # original0x40250fab
pc40250fae:
sub a12, a11, a12 # original0x40250fae
pc40250fb1:
addi a12, a12, -32 # original0x40250fb1
pc40250fb4:
bge a12, a2, pc40250fb9 # original0x40250fb4
pc40250fb7:
mov.n a2, a12 # original0x40250fb7
pc40250fb9:
bgei a2, 4, pc40250fd1 # original0x40250fb9
pc40250fbc:
l32i a12, a1, 120 # original0x40250fbc
pc40250fbf:
blt a12, a4, pc40250fc5 # original0x40250fbf
pc40250fc2:
j pc402529f4 # original0x40250fc2
pc40250fc5:
l32i a8, a1, 240 # original0x40250fc5
pc40250fc8:
# decoder-unreachable/check: beqz a8, 40250fcd <quant_all_bands+2037>
pc40250fca:
# decoder-unreachable/check: j 40252b75 <quant_all_bands+9117>
pc40250fcd:
j pc402529fa # original0x40250fcd
pc40250fd1:
movi.n a3, 64 # original0x40250fd1
pc40250fd3:
bge a3, a2, pc40250fd8 # original0x40250fd3
pc40250fd6:
mov.n a2, a3 # original0x40250fd6
pc40250fd8:
extui a3, a2, 0, 3 # original0x40250fd8
pc40250fdb:
slli a5, a3, 1 # original0x40250fdb
pc40250fde:
l32r a3, fixed_40250798 # original0x40250fde
pc40250fe1:
srai a2, a2, 3 # original0x40250fe1
pc40250fe4:
add a3, a3, a5 # original0x40250fe4
pc40250fe7:
l16si a12, a3, 0 # original0x40250fe7
pc40250fea:
movi a3, 14 # original0x40250fea
pc40250fed:
sub a2, a3, a2 # original0x40250fed
pc40250ff0:
ssr a2 # original0x40250ff0
pc40250ff3:
sra a12, a12 # original0x40250ff3
pc40250ff6:
l32i a9, a1, 120 # original0x40250ff6
pc40250ff9:
addi a12, a12, 1 # original0x40250ff9
pc40250ffc:
movi.n a13, -2 # original0x40250ffc
pc40250ffe:
and a13, a12, a13 # original0x40250ffe
pc40251001:
blt a9, a4, pc40251007 # original0x40251001
pc40251004:
j pc402529f4 # original0x40251004
pc40251007:
l32i a10, a1, 240 # original0x40251007
pc4025100a:
# decoder-unreachable/check: beqz a10, 4025100f <quant_all_bands+2103>
pc4025100c:
# decoder-unreachable/check: j 40252b45 <quant_all_bands+9069>
pc4025100f:
mov.n a2, a14 # original0x4025100f
pc40251011:
call0 fixed_40246830 # original0x40251011
pc40251014:
l32i a11, a1, 128 # original0x40251014
pc40251017:
s32i a2, a1, 120 # original0x40251017
pc4025101a:
bgei a11, 3, pc40251020 # original0x4025101a
pc4025101d:
j pc40252aac # original0x4025101d
pc40251020:
j pc402529a5 # original0x40251020
pc40251024:
# decoder-unreachable/check: addmi a6, a6, 8192
pc40251027:
# decoder-unreachable/check: srai a6, a6, 14
pc4025102a:
# decoder-unreachable/check: j 402529eb <quant_all_bands+8723>
pc4025102d:
# decoder-unreachable/check: l32r a2, 4024f620 <anti_collapse+2320>
pc40251030:
# decoder-unreachable/check: bge a2, a3, 4025104d <quant_all_bands+2165>
pc40251033:
# decoder-unreachable/check: l32r a2, 4024f0bc <anti_collapse+940>
pc40251036:
# decoder-unreachable/check: mov a3, a13
pc40251038:
# decoder-unreachable/check: s32i a4, a1, 348
pc4025103b:
# decoder-unreachable/check: s32i a6, a1, 344
pc4025103e:
# decoder-unreachable/check: l32r a0, 4024f100 <anti_collapse+1008>
pc40251041:
# decoder-unreachable/check: callx0 a0
pc40251044:
# decoder-unreachable/check: l32i a4, a1, 348
pc40251047:
# decoder-unreachable/check: l32i a6, a1, 344
pc4025104a:
# decoder-unreachable/check: j 40251064 <quant_all_bands+2188>
pc4025104d:
# decoder-unreachable/check: l32r a2, 4024f1a8 <anti_collapse+1176>
pc40251050:
# decoder-unreachable/check: mov a3, a13
pc40251052:
# decoder-unreachable/check: s32i a4, a1, 348
pc40251055:
# decoder-unreachable/check: s32i a6, a1, 344
pc40251058:
# decoder-unreachable/check: l32r a0, 4024f100 <anti_collapse+1008>
pc4025105b:
# decoder-unreachable/check: callx0 a0
pc4025105e:
# decoder-unreachable/check: l32i a6, a1, 344
pc40251061:
# decoder-unreachable/check: l32i a4, a1, 348
pc40251064:
# decoder-unreachable/check: add a6, a2, a6
pc40251066:
# decoder-unreachable/check: srai a6, a6, 14
pc40251069:
# decoder-unreachable/check: movi a2, 0
pc4025106b:
# decoder-unreachable/check: movltz a6, a2, a6
pc4025106e:
# decoder-unreachable/check: addi a2, a13, -1
pc40251070:
# decoder-unreachable/check: bge a2, a6, 40251075 <quant_all_bands+2205>
pc40251073:
# decoder-unreachable/check: mov a6, a2
pc40251075:
# decoder-unreachable/check: movi a2, -1
pc40251077:
# decoder-unreachable/check: xor a4, a2, a4
pc4025107a:
# decoder-unreachable/check: extui a4, a4, 31, 1
pc4025107d:
# decoder-unreachable/check: add a6, a6, a4
pc4025107f:
# decoder-unreachable/check: j 402529eb <quant_all_bands+8723>
pc40251084:
# decoder-unreachable/check: slli a3, a6, 1
pc40251087:
# decoder-unreachable/check: add a3, a3, a6
pc40251089:
# decoder-unreachable/check: addi a4, a3, 3
pc4025108b:
# decoder-unreachable/check: j 40251097 <quant_all_bands+2239>
pc4025108e:
# decoder-unreachable/check: sub a4, a2, a4
pc40251091:
# decoder-unreachable/check: add a4, a4, a6
pc40251094:
# decoder-unreachable/check: addi a3, a4, -1
pc40251097:
# decoder-unreachable/check: or a2, a14, a14
pc4025109a:
# decoder-unreachable/check: s32i a6, a1, 344
pc4025109d:
# decoder-unreachable/check: call0 4025359c <ec_encode>
pc402510a0:
# decoder-unreachable/check: l32i a6, a1, 344
pc402510a3:
# decoder-unreachable/check: mov a3, a13
pc402510a5:
# decoder-unreachable/check: slli a2, a6, 14
pc402510a8:
# decoder-unreachable/check: l32r a0, 40250738 <anti_collapse+6696>
pc402510ab:
# decoder-unreachable/check: callx0 a0
pc402510ae:
# decoder-unreachable/check: s32i a2, a1, 196
pc402510b1:
# decoder-unreachable/check: bnez a2, 40251140 <quant_all_bands+2408>
pc402510b4:
# decoder-unreachable/check: j 40251108 <quant_all_bands+2352>
pc402510b8:
movi.n a3, 3 # original0x402510b8
pc402510ba:
s32i a4, a1, 0x15c # original0x402510ba
pc402510bd:
s32i a5, a1, 0x158 # original0x402510bd
pc402510c0:
s32i a7, a1, 0x154 # original0x402510c0
pc402510c3:
l32r a0, fixed_4024f100 # original0x402510c3
pc402510c6:
callx0 a0 # original0x402510c6
pc402510c9:
mov.n a12, a2 # original0x402510c9
pc402510cb:
l32i a4, a1, 0x15c # original0x402510cb
pc402510ce:
l32i a5, a1, 0x158 # original0x402510ce
pc402510d1:
l32i a7, a1, 0x154 # original0x402510d1
pc402510d4:
j pc402510e5 # original0x402510d4
pc402510d7:
movi.n a6, -1 # original0x402510d7
pc402510d9:
xor a6, a6, a5 # original0x402510d9
pc402510dc:
slli a3, a6, 1 # original0x402510dc
pc402510df:
add.n a3, a3, a6 # original0x402510df
pc402510e1:
add.n a12, a3, a12 # original0x402510e1
pc402510e3:
add.n a12, a12, a2 # original0x402510e3
pc402510e5:
blt a5, a12, pc402510f4 # original0x402510e5
pc402510e8:
slli a3, a12, 1 # original0x402510e8
pc402510eb:
add.n a3, a3, a12 # original0x402510eb
pc402510ed:
addi.n a4, a3, 3 # original0x402510ed
pc402510ef:
j pc402510fd # original0x402510ef
pc402510f4:
sub a4, a4, a5 # original0x402510f4
pc402510f7:
add a4, a4, a12 # original0x402510f7
pc402510fa:
addi a3, a4, -1 # original0x402510fa
pc402510fd:
or a5, a7, a7 # original0x402510fd
pc40251100:
mov.n a2, a14 # original0x40251100
pc40251102:
call0 fixed_402469dc # original0x40251102
pc40251105:
j pc40252966 # original0x40251105
pc40251108:
# decoder-unreachable/check: l32i a8, a1, 124
pc4025110b:
# decoder-unreachable/check: l32i a7, a1, 128
pc4025110e:
# decoder-unreachable/check: l32i a2, a8, 8
pc40251111:
# decoder-unreachable/check: l32i a6, a1, 120
pc40251114:
# decoder-unreachable/check: l32i a5, a1, 140
pc40251117:
# decoder-unreachable/check: l32i a3, a1, 172
pc4025111a:
# decoder-unreachable/check: or a4, a15, a15
pc4025111d:
# decoder-unreachable/check: call0 4024da14 <intensity_stereo$isra$1>
pc40251120:
# decoder-unreachable/check: mov a2, a14
pc40251122:
# decoder-unreachable/check: call0 40246830 <ec_tell_frac>
pc40251125:
# decoder-unreachable/check: l32i a9, a1, 132
pc40251128:
# decoder-unreachable/check: l32i a10, a1, 136
pc4025112b:
# decoder-unreachable/check: sub a2, a2, a9
pc4025112e:
# decoder-unreachable/check: sub a10, a10, a2
pc40251131:
# decoder-unreachable/check: movi a11, 0
pc40251133:
# decoder-unreachable/check: s32i a2, a1, 228
pc40251136:
# decoder-unreachable/check: s32i a10, a1, 188
pc40251139:
# decoder-unreachable/check: s32i a11, a1, 240
pc4025113c:
# decoder-unreachable/check: j 4025124a <quant_all_bands+2674>
pc40251140:
# decoder-unreachable/check: l32i a12, a1, 128
pc40251143:
# decoder-unreachable/check: l32r a8, 4024f0d8 <anti_collapse+968>
pc40251146:
# decoder-unreachable/check: l32i a3, a1, 172
pc40251149:
# decoder-unreachable/check: slli a7, a12, 1
pc4025114c:
# decoder-unreachable/check: mov a5, a15
pc4025114e:
# decoder-unreachable/check: add a7, a7, a3
pc40251151:
# decoder-unreachable/check: or a9, a8, a8
pc40251154:
# decoder-unreachable/check: l16ui a2, a3, 0
pc40251157:
# decoder-unreachable/check: l16ui a4, a5, 0
pc4025115a:
# decoder-unreachable/check: mul16s a6, a2, a8
pc4025115d:
# decoder-unreachable/check: mul16s a2, a4, a9
pc40251160:
# decoder-unreachable/check: add a4, a6, a2
pc40251162:
# decoder-unreachable/check: srai a4, a4, 15
pc40251165:
# decoder-unreachable/check: sub a2, a2, a6
pc40251168:
# decoder-unreachable/check: s16i a4, a3, 0
pc4025116b:
# decoder-unreachable/check: srai a2, a2, 15
pc4025116e:
# decoder-unreachable/check: s16i a2, a5, 0
pc40251171:
# decoder-unreachable/check: addi a3, a3, 2
pc40251173:
# decoder-unreachable/check: addi a5, a5, 2
pc40251175:
# decoder-unreachable/check: bne a7, a3, 40251154 <quant_all_bands+2428>
pc40251178:
# decoder-unreachable/check: j 4025294c <quant_all_bands+8564>
pc4025117b:
# decoder-unreachable/check: l32r a2, 4024f620 <anti_collapse+2320>
pc4025117e:
# decoder-unreachable/check: bge a2, a13, 402511ad <quant_all_bands+2517>
pc40251181:
# decoder-unreachable/check: l32i a2, a1, 84
pc40251184:
# decoder-unreachable/check: movi a13, 0
pc40251186:
# decoder-unreachable/check: bne a2, a13, 402511b0 <quant_all_bands+2520>
pc40251189:
# decoder-unreachable/check: l32i a8, a1, 128
pc4025118c:
# decoder-unreachable/check: mov a2, a15
pc4025118e:
# decoder-unreachable/check: slli a4, a8, 1
pc40251191:
# decoder-unreachable/check: add a4, a4, a15
pc40251193:
# decoder-unreachable/check: bgei a8, 1, 4025119c <quant_all_bands+2500>
pc40251196:
# decoder-unreachable/check: movi a13, 1
pc40251198:
# decoder-unreachable/check: j 402511b0 <quant_all_bands+2520>
pc4025119c:
# decoder-unreachable/check: l16ui a3, a2, 0
pc4025119f:
# decoder-unreachable/check: neg a3, a3
pc402511a2:
# decoder-unreachable/check: s16i a3, a2, 0
pc402511a5:
# decoder-unreachable/check: addi a2, a2, 2
pc402511a7:
# decoder-unreachable/check: bne a4, a2, 4025119c <quant_all_bands+2500>
pc402511aa:
# decoder-unreachable/check: j 40251196 <quant_all_bands+2494>
pc402511ad:
# decoder-unreachable/check: movi a13, 0
pc402511b0:
# decoder-unreachable/check: l32i a9, a1, 124
pc402511b3:
# decoder-unreachable/check: l32i a7, a1, 128
pc402511b6:
# decoder-unreachable/check: l32i a2, a9, 8
pc402511b9:
# decoder-unreachable/check: l32i a6, a1, 120
pc402511bc:
# decoder-unreachable/check: l32i a5, a1, 140
pc402511bf:
# decoder-unreachable/check: l32i a3, a1, 172
pc402511c2:
# decoder-unreachable/check: or a4, a15, a15
pc402511c5:
# decoder-unreachable/check: call0 4024da14 <intensity_stereo$isra$1>
pc402511c8:
l32i a10, a1, 136 # original0x402511c8
pc402511cb:
movi.n a2, 16 # original0x402511cb
pc402511cd:
bge a2, a10, pc402511fa # original0x402511cd
pc402511d0:
l32i a3, a1, 64 # original0x402511d0
pc402511d3:
bge a2, a3, pc40251202 # original0x402511d3
pc402511d6:
l32i a11, a1, 240 # original0x402511d6
pc402511d9:
# decoder-unreachable/check: beqz a11, 402511ea <quant_all_bands+2578>
pc402511db:
# decoder-unreachable/check: movi a4, 2
pc402511dd:
# decoder-unreachable/check: mov a3, a13
pc402511df:
# decoder-unreachable/check: mov a2, a14
pc402511e1:
# decoder-unreachable/check: call0 402536a0 <ec_enc_bit_logp>
pc402511e4:
# decoder-unreachable/check: s32i a13, a1, 240
pc402511e7:
# decoder-unreachable/check: j 40251208 <quant_all_bands+2608>
pc402511ea:
movi.n a3, 2 # original0x402511ea
pc402511ec:
mov.n a2, a14 # original0x402511ec
pc402511ee:
call0 fixed_40246a88 # original0x402511ee
pc402511f1:
s32i a2, a1, 240 # original0x402511f1
pc402511f4:
j pc40251208 # original0x402511f4
pc402511fa:
movi.n a8, 0 # original0x402511fa
pc402511fc:
s32i a8, a1, 240 # original0x402511fc
pc402511ff:
j pc40251208 # original0x402511ff
pc40251202:
movi a9, 0 # original0x40251202
pc40251205:
s32i a9, a1, 240 # original0x40251205
pc40251208:
l32i a2, a1, 84 # original0x40251208
pc4025120b:
bnez a2, pc40251226 # original0x4025120b
pc4025120e:
or a2, a14, a14 # original0x4025120e
pc40251211:
call0 fixed_40246830 # original0x40251211
pc40251214:
l32i a10, a1, 136 # original0x40251214
pc40251217:
sub a12, a2, a12 # original0x40251217
pc4025121a:
sub a10, a10, a12 # original0x4025121a
pc4025121d:
s32i a12, a1, 228 # original0x4025121d
pc40251220:
s32i a10, a1, 188 # original0x40251220
pc40251223:
j pc4025124a # original0x40251223
pc40251226:
mov.n a2, a14 # original0x40251226
pc40251228:
call0 fixed_40246830 # original0x40251228
pc4025122b:
l32i a11, a1, 136 # original0x4025122b
pc4025122e:
sub a12, a2, a12 # original0x4025122e
pc40251231:
sub a11, a11, a12 # original0x40251231
pc40251234:
s32i a12, a1, 228 # original0x40251234
pc40251237:
movi.n a12, 0 # original0x40251237
pc40251239:
s32i a11, a1, 188 # original0x40251239
pc4025123c:
s32i a12, a1, 240 # original0x4025123c
pc4025123f:
j pc4025124a # original0x4025123f
pc40251245:
movi.n a14, 0 # original0x40251245
pc40251247:
s32i a14, a1, 240 # original0x40251247
pc4025124a:
l32i a9, a1, 208 # original0x4025124a
pc4025124d:
l32i a10, a1, 112 # original0x4025124d
pc40251250:
l32r a8, fixed_4024f0bc # original0x40251250
pc40251253:
movi.n a11, 0 # original0x40251253
pc40251255:
and a9, a9, a10 # original0x40251255
pc40251258:
s32i a8, a1, 140 # original0x40251258
pc4025125b:
s32i a9, a1, 0x114 # original0x4025125b
pc4025125e:
s32i a8, a1, 0x13c # original0x4025125e
pc40251261:
s32i a11, a1, 196 # original0x40251261
pc40251264:
s32i a11, a1, 216 # original0x40251264
pc40251267:
s32i a8, a1, 0x110 # original0x40251267
pc4025126a:
l32r a2, fixed_40250790 # original0x4025126a
pc4025126d:
j pc40252b28 # original0x4025126d
pc40251270:
l32r a2, fixed_4024f0f4 # original0x40251270
pc40251273:
l32i a8, a1, 196 # original0x40251273
pc40251276:
bne a8, a2, pc402512a0 # original0x40251276
pc40251279:
l32i a11, a1, 112 # original0x40251279
pc4025127c:
l32i a12, a1, 0x150 # original0x4025127c
pc4025127f:
l32r a9, fixed_4024f0bc # original0x4025127f
pc40251282:
movi.n a10, 0 # original0x40251282
pc40251284:
and a11, a11, a12 # original0x40251284
pc40251287:
s32i a9, a1, 140 # original0x40251287
pc4025128a:
s32i a10, a1, 0x13c # original0x4025128a
pc4025128d:
s32i a11, a1, 0x114 # original0x4025128d
pc40251290:
mov.n a2, a8 # original0x40251290
pc40251292:
s32i a10, a1, 240 # original0x40251292
pc40251295:
s32i a9, a1, 216 # original0x40251295
pc40251298:
s32i a10, a1, 0x110 # original0x40251298
pc4025129b:
j pc40252b28 # original0x4025129b
pc402512a0:
slli a3, a8, 16 # original0x402512a0
pc402512a3:
srai a3, a3, 16 # original0x402512a3
pc402512a6:
sub a2, a2, a3 # original0x402512a6
pc402512a9:
mul16s a2, a2, a2 # original0x402512a9
pc402512ac:
mull a4, a3, a3 # original0x402512ac
pc402512af:
addmi a3, a2, 0x1000 # original0x402512af
pc402512b2:
addmi a4, a4, 0x1000 # original0x402512b2
pc402512b5:
slli a3, a3, 3 # original0x402512b5
pc402512b8:
srai a3, a3, 16 # original0x402512b8
pc402512bb:
movi a2, 0xfffffd8e # original0x402512bb
pc402512be:
slli a4, a4, 3 # original0x402512be
pc402512c1:
srai a4, a4, 16 # original0x402512c1
pc402512c4:
mul16s a5, a2, a3 # original0x402512c4
pc402512c7:
mul16s a2, a2, a4 # original0x402512c7
pc402512ca:
l32r a6, fixed_4025079c # original0x402512ca
pc402512cd:
addmi a5, a5, 0x4000 # original0x402512cd
pc402512d0:
addmi a2, a2, 0x4000 # original0x402512d0
pc402512d3:
srai a5, a5, 15 # original0x402512d3
pc402512d6:
add.n a5, a5, a6 # original0x402512d6
pc402512d8:
srai a2, a2, 15 # original0x402512d8
pc402512db:
add.n a2, a2, a6 # original0x402512db
pc402512dd:
mul16s a5, a5, a3 # original0x402512dd
pc402512e0:
mul16s a2, a2, a4 # original0x402512e0
pc402512e3:
l32r a6, fixed_402507a0 # original0x402512e3
pc402512e6:
addmi a5, a5, 0x4000 # original0x402512e6
pc402512e9:
addmi a2, a2, 0x4000 # original0x402512e9
pc402512ec:
srai a5, a5, 15 # original0x402512ec
pc402512ef:
add.n a5, a5, a6 # original0x402512ef
pc402512f1:
srai a2, a2, 15 # original0x402512f1
pc402512f4:
add.n a2, a2, a6 # original0x402512f4
pc402512f6:
mul16s a5, a5, a3 # original0x402512f6
pc402512f9:
l32r a6, fixed_4024f110 # original0x402512f9
pc402512fc:
mul16s a2, a2, a4 # original0x402512fc
pc402512ff:
addmi a5, a5, 0x4000 # original0x402512ff
pc40251302:
srai a5, a5, 15 # original0x40251302
pc40251305:
sub a3, a6, a3 # original0x40251305
pc40251308:
addmi a2, a2, 0x4000 # original0x40251308
pc4025130b:
sub a4, a6, a4 # original0x4025130b
pc4025130e:
add.n a3, a5, a3 # original0x4025130e
pc40251310:
srai a2, a2, 15 # original0x40251310
pc40251313:
add.n a2, a2, a4 # original0x40251313
pc40251315:
slli a3, a3, 16 # original0x40251315
pc40251318:
srai a3, a3, 16 # original0x40251318
pc4025131b:
slli a2, a2, 16 # original0x4025131b
pc4025131e:
srai a2, a2, 16 # original0x4025131e
pc40251321:
nsau a7, a3 # original0x40251321
pc40251324:
nsau a6, a2 # original0x40251324
pc40251327:
addi a5, a7, -17 # original0x40251327
pc4025132a:
ssl a5 # original0x4025132a
pc4025132d:
sll a5, a3 # original0x4025132d
pc40251330:
addi a4, a6, -17 # original0x40251330
pc40251333:
s32i a2, a1, 0x110 # original0x40251333
pc40251336:
ssl a4 # original0x40251336
pc40251339:
sll a4, a2 # original0x40251339
pc4025133c:
slli a5, a5, 16 # original0x4025133c
pc4025133f:
l32r a2, fixed_402507a4 # original0x4025133f
pc40251342:
srai a5, a5, 16 # original0x40251342
pc40251345:
slli a4, a4, 16 # original0x40251345
pc40251348:
srai a4, a4, 16 # original0x40251348
pc4025134b:
s32i a3, a1, 216 # original0x4025134b
pc4025134e:
mov.n a3, a2 # original0x4025134e
pc40251350:
mul16s a2, a5, a2 # original0x40251350
pc40251353:
mul16s a3, a4, a3 # original0x40251353
pc40251356:
l32r a8, fixed_402507a8 # original0x40251356
pc40251359:
addmi a2, a2, 0x4000 # original0x40251359
pc4025135c:
srai a2, a2, 15 # original0x4025135c
pc4025135f:
addmi a3, a3, 0x4000 # original0x4025135f
pc40251362:
add.n a2, a2, a8 # original0x40251362
pc40251364:
srai a3, a3, 15 # original0x40251364
pc40251367:
add.n a3, a3, a8 # original0x40251367
pc40251369:
mul16s a2, a2, a5 # original0x40251369
pc4025136c:
mul16s a4, a3, a4 # original0x4025136c
pc4025136f:
addmi a2, a2, 0x4000 # original0x4025136f
pc40251372:
sub a6, a6, a7 # original0x40251372
pc40251375:
l32i a9, a1, 128 # original0x40251375
pc40251378:
srai a2, a2, 15 # original0x40251378
pc4025137b:
slli a6, a6, 11 # original0x4025137b
pc4025137e:
addmi a4, a4, 0x4000 # original0x4025137e
pc40251381:
add.n a2, a2, a6 # original0x40251381
pc40251383:
srai a4, a4, 15 # original0x40251383
pc40251386:
addi.n a3, a9, -1 # original0x40251386
pc40251388:
sub a2, a2, a4 # original0x40251388
pc4025138b:
slli a3, a3, 7 # original0x4025138b
pc4025138e:
l32i a12, a1, 0x144 # original0x4025138e
pc40251391:
mul16s a2, a2, a3 # original0x40251391
pc40251394:
l32i a10, a1, 0x110 # original0x40251394
pc40251397:
l32i a11, a1, 64 # original0x40251397
pc4025139a:
extui a12, a12, 0, 8 # original0x4025139a
pc4025139d:
addmi a2, a2, 0x4000 # original0x4025139d
pc402513a0:
s32i a10, a1, 0x13c # original0x402513a0
pc402513a3:
s32i a11, a1, 252 # original0x402513a3
pc402513a6:
s32i a12, a1, 0x138 # original0x402513a6
pc402513a9:
srai a2, a2, 15 # original0x402513a9
pc402513ac:
beqi a9, 2, pc402513b2 # original0x402513ac
pc402513af:
j pc40251cd1 # original0x402513af
pc402513b2:
l32r a2, fixed_4025055c # original0x402513b2
pc402513b5:
l32i a8, a1, 196 # original0x402513b5
pc402513b8:
bnone a8, a2, pc402513be # original0x402513b8
pc402513bb:
j pc40252a2c # original0x402513bb
pc402513be:
movi.n a9, 0 # original0x402513be
pc402513c0:
s32i a9, a1, 240 # original0x402513c0
pc402513c3:
mov.n a14, a11 # original0x402513c3
pc402513c5:
j pc40252a58 # original0x402513c5
pc402513c9:
l32i a10, a1, 172 # original0x402513c9
pc402513cc:
s32i a15, a1, 228 # original0x402513cc
pc402513cf:
s32i a10, a1, 132 # original0x402513cf
pc402513d2:
l32i a11, a1, 240 # original0x402513d2
pc402513d5:
# decoder-unreachable/check: beqz a11, 4025141e <quant_all_bands+3142>
pc402513d8:
# decoder-unreachable/check: l32i a8, a1, 132
pc402513db:
# decoder-unreachable/check: l32i a9, a1, 228
pc402513de:
# decoder-unreachable/check: l16ui a12, a8, 0
pc402513e1:
# decoder-unreachable/check: l16ui a4, a9, 2
pc402513e4:
# decoder-unreachable/check: l16ui a3, a9, 0
pc402513e7:
# decoder-unreachable/check: l16ui a2, a8, 2
pc402513ea:
# decoder-unreachable/check: mul16s a12, a12, a4
pc402513ed:
# decoder-unreachable/check: mul16s a2, a2, a3
pc402513f0:
# decoder-unreachable/check: movi a4, 1
pc402513f3:
# decoder-unreachable/check: sub a12, a12, a2
pc402513f6:
# decoder-unreachable/check: extui a3, a12, 31, 1
pc402513f9:
# decoder-unreachable/check: or a2, a14, a14
pc402513fc:
# decoder-unreachable/check: call0 40298c90 <ec_enc_bits>
pc402513ff:
# decoder-unreachable/check: movi a2, -2
pc40251402:
# decoder-unreachable/check: movi a10, 0
pc40251404:
# decoder-unreachable/check: movltz a10, a2, a12
pc40251407:
# decoder-unreachable/check: movi a2, -1
pc40251409:
# decoder-unreachable/check: xor a2, a2, a10
pc4025140c:
# decoder-unreachable/check: addi a12, a10, 1
pc4025140e:
# decoder-unreachable/check: movi a11, 0
pc40251410:
# decoder-unreachable/check: s32i a2, a1, 252
pc40251413:
# decoder-unreachable/check: s32i a12, a1, 256
pc40251416:
# decoder-unreachable/check: s32i a11, a1, 240
pc40251419:
# decoder-unreachable/check: j 4025145c <quant_all_bands+3204>
pc4025141e:
movi a3, 1 # original0x4025141e
pc40251421:
or a2, a14, a14 # original0x40251421
pc40251424:
call0 fixed_40298548 # original0x40251424
pc40251427:
slli a2, a2, 1 # original0x40251427
pc4025142a:
neg a3, a2 # original0x4025142a
pc4025142d:
addi a3, a3, 1 # original0x4025142d
pc40251430:
addi.n a2, a2, -1 # original0x40251430
pc40251432:
slli a2, a2, 16 # original0x40251432
pc40251435:
slli a3, a3, 16 # original0x40251435
pc40251438:
srai a2, a2, 16 # original0x40251438
pc4025143b:
srai a3, a3, 16 # original0x4025143b
pc4025143e:
s32i a2, a1, 252 # original0x4025143e
pc40251441:
s32i a3, a1, 0x100 # original0x40251441
pc40251444:
j pc4025145c # original0x40251444
pc40251449:
l32i a12, a1, 172 # original0x40251449
pc4025144c:
movi.n a14, 1 # original0x4025144c
pc4025144e:
movi.n a8, -1 # original0x4025144e
pc40251450:
s32i a12, a1, 132 # original0x40251450
pc40251453:
s32i a15, a1, 228 # original0x40251453
pc40251456:
s32i a14, a1, 0x100 # original0x40251456
pc40251459:
s32i a8, a1, 252 # original0x40251459
pc4025145c:
l32i a3, a1, 180 # original0x4025145c
pc4025145f:
l32i.n a9, a1, 56 # original0x4025145f
pc40251461:
movi.n a2, 2 # original0x40251461
pc40251463:
s32i a9, a1, 124 # original0x40251463
pc40251466:
l32r a0, fixed_40250738 # original0x40251466
pc40251469:
callx0 a0 # original0x40251469
pc4025146c:
l32i.n a10, a1, 32 # original0x4025146c
pc4025146e:
l32i a11, a1, 168 # original0x4025146e
pc40251471:
l32i a14, a1, 152 # original0x40251471
pc40251474:
movi.n a12, 1 # original0x40251474
pc40251476:
s32i a2, a1, 148 # original0x40251476
pc40251479:
movi.n a3, 0 # original0x40251479
pc4025147b:
movi.n a2, 0 # original0x4025147b
pc4025147d:
l32i a8, a1, 124 # original0x4025147d
pc40251480:
movnez a2, a12, a11 # original0x40251480
pc40251483:
movnez a3, a12, a14 # original0x40251483
pc40251486:
s32i a10, a1, 140 # original0x40251486
pc40251489:
and a2, a2, a3 # original0x40251489
pc4025148c:
bge a8, a12, pc402514a2 # original0x4025148c
pc4025148f:
l32i a9, a1, 148 # original0x4025148f
pc40251492:
movi.n a12, -1 # original0x40251492
pc40251494:
xor a12, a12, a9 # original0x40251494
pc40251497:
extui a3, a8, 31, 1 # original0x40251497
pc4025149a:
and a12, a12, a3 # original0x4025149a
pc4025149d:
bnez.n a2, pc402514aa # original0x4025149d
pc4025149f:
j pc4025166b # original0x4025149f
pc402514a2:
bnez a2, pc402514f2 # original0x402514a2
pc402514a5:
mov.n a11, a14 # original0x402514a5
pc402514a7:
j pc40251508 # original0x402514a7
pc402514aa:
bnez.n a12, pc402514da # original0x402514aa
pc402514ac:
l32i a10, a1, 180 # original0x402514ac
pc402514af:
bgei a10, 2, pc402514b5 # original0x402514af
pc402514b2:
j pc40251776 # original0x402514b2
pc402514b5:
movi.n a5, 2 # original0x402514b5
pc402514b7:
mov.n a2, a11 # original0x402514b7
pc402514b9:
mov.n a3, a14 # original0x402514b9
pc402514bb:
mov.n a4, a5 # original0x402514bb
pc402514bd:
call0 fixed_402429b0 # original0x402514bd
pc402514c0:
l32i a11, a1, 140 # original0x402514c0
pc402514c3:
# decoder-unreachable/check: bnez a11, 40251789 <quant_all_bands+4017>
pc402514c6:
l32i a12, a1, 168 # original0x402514c6
pc402514c9:
s32i a11, a1, 120 # original0x402514c9
pc402514cc:
s32i a11, a1, 124 # original0x402514cc
pc402514cf:
s32i a12, a1, 152 # original0x402514cf
pc402514d2:
l32i a13, a1, 180 # original0x402514d2
pc402514d5:
j pc402517c0 # original0x402514d5
pc402514da:
movi a5, 2 # original0x402514da
pc402514dd:
or a3, a14, a14 # original0x402514dd
pc402514e0:
or a2, a11, a11 # original0x402514e0
pc402514e3:
mov.n a4, a5 # original0x402514e3
pc402514e5:
call0 fixed_402429b0 # original0x402514e5
pc402514e8:
l32i a14, a1, 168 # original0x402514e8
pc402514eb:
s32i a14, a1, 152 # original0x402514eb
pc402514ee:
j pc4025166e # original0x402514ee
pc402514f2:
movi a5, 2 # original0x402514f2
pc402514f5:
or a2, a11, a11 # original0x402514f5
pc402514f8:
or a3, a14, a14 # original0x402514f8
pc402514fb:
mov.n a4, a5 # original0x402514fb
pc402514fd:
call0 fixed_402429b0 # original0x402514fd
pc40251500:
l32i a8, a1, 168 # original0x40251500
pc40251503:
s32i a8, a1, 152 # original0x40251503
pc40251506:
mov.n a11, a8 # original0x40251506
pc40251508:
l32r a10, fixed_402507ac # original0x40251508
pc4025150b:
l32r a9, fixed_4024f0d8 # original0x4025150b
pc4025150e:
s32i a10, a1, 120 # original0x4025150e
pc40251511:
movi.n a5, 0 # original0x40251511
pc40251513:
mov.n a10, a9 # original0x40251513
pc40251515:
s32i a15, a1, 0x114 # original0x40251515
pc40251518:
l32i a12, a1, 140 # original0x40251518
pc4025151b:
# decoder-unreachable/check: beqz a12, 402515a5 <quant_all_bands+3533>
pc4025151e:
# decoder-unreachable/check: movi a2, 1
pc40251520:
# decoder-unreachable/check: movi a14, 2
pc40251522:
# decoder-unreachable/check: ssr a5
pc40251525:
# decoder-unreachable/check: sra a7, a14
pc40251528:
# decoder-unreachable/check: ssl a5
pc4025152b:
# decoder-unreachable/check: sll a8, a2
pc4025152e:
# decoder-unreachable/check: ssr a2
pc40251531:
# decoder-unreachable/check: sra a7, a7
pc40251534:
# decoder-unreachable/check: bge a8, a2, 4025153a <quant_all_bands+3426>
pc40251537:
# decoder-unreachable/check: j 40251621 <quant_all_bands+3657>
pc4025153a:
# decoder-unreachable/check: movi a6, 0
pc4025153c:
# decoder-unreachable/check: bge a7, a2, 40251598 <quant_all_bands+3520>
pc4025153f:
# decoder-unreachable/check: j 40251621 <quant_all_bands+3657>
pc40251544:
# decoder-unreachable/check: ssl a5
pc40251547:
# decoder-unreachable/check: sll a2, a11
pc4025154a:
# decoder-unreachable/check: slli a2, a2, 1
pc4025154d:
# decoder-unreachable/check: ssl a5
pc40251550:
# decoder-unreachable/check: sll a4, a13
pc40251553:
# decoder-unreachable/check: add a2, a2, a6
pc40251555:
# decoder-unreachable/check: slli a2, a2, 1
pc40251558:
# decoder-unreachable/check: add a4, a4, a6
pc4025155a:
# decoder-unreachable/check: add a3, a15, a2
pc4025155c:
# decoder-unreachable/check: slli a4, a4, 1
pc4025155f:
# decoder-unreachable/check: l16ui a12, a3, 0
pc40251562:
# decoder-unreachable/check: add a4, a15, a4
pc40251564:
# decoder-unreachable/check: l16ui a14, a4, 0
pc40251567:
# decoder-unreachable/check: l32r a2, 4024f0d8 <anti_collapse+968>
pc4025156a:
# decoder-unreachable/check: mul16s a12, a12, a10
pc4025156d:
# decoder-unreachable/check: mul16s a14, a14, a2
pc40251570:
# decoder-unreachable/check: addmi a2, a12, 16384
pc40251573:
# decoder-unreachable/check: add a12, a14, a2
pc40251575:
# decoder-unreachable/check: srai a12, a12, 15
pc40251578:
# decoder-unreachable/check: sub a2, a2, a14
pc4025157b:
# decoder-unreachable/check: s16i a12, a3, 0
pc4025157e:
# decoder-unreachable/check: srai a2, a2, 15
pc40251581:
# decoder-unreachable/check: s16i a2, a4, 0
pc40251584:
# decoder-unreachable/check: addi a11, a11, 1
pc40251586:
# decoder-unreachable/check: addi a13, a13, 2
pc40251588:
# decoder-unreachable/check: bne a7, a11, 40251544 <quant_all_bands+3436>
pc4025158b:
# decoder-unreachable/check: addi a6, a6, 1
pc4025158d:
# decoder-unreachable/check: bne a8, a6, 40251593 <quant_all_bands+3515>
pc40251590:
# decoder-unreachable/check: j 40252b11 <quant_all_bands+9017>
pc40251593:
# decoder-unreachable/check: j 4025159e <quant_all_bands+3526>
pc40251598:
# decoder-unreachable/check: l32i a15, a1, 132
pc4025159b:
# decoder-unreachable/check: s32i a11, a1, 196
pc4025159e:
# decoder-unreachable/check: movi a13, 1
pc402515a0:
# decoder-unreachable/check: movi a11, 0
pc402515a2:
# decoder-unreachable/check: j 40251544 <quant_all_bands+3436>
pc402515a5:
beqz a11, pc40251621 # original0x402515a5
pc402515a8:
movi.n a4, 1 # original0x402515a8
pc402515aa:
movi.n a3, 2 # original0x402515aa
pc402515ac:
ssr a5 # original0x402515ac
pc402515af:
sra a7, a3 # original0x402515af
pc402515b2:
ssl a5 # original0x402515b2
pc402515b5:
sll a8, a4 # original0x402515b5
pc402515b8:
ssr a4 # original0x402515b8
pc402515bb:
sra a7, a7 # original0x402515bb
pc402515be:
bge a8, a4, pc40251615 # original0x402515be
pc402515c1:
j pc40251621 # original0x402515c1
pc402515c4:
ssl a5 # original0x402515c4
pc402515c7:
sll a2, a3 # original0x402515c7
pc402515ca:
slli a2, a2, 1 # original0x402515ca
pc402515cd:
ssl a5 # original0x402515cd
pc402515d0:
sll a13, a4 # original0x402515d0
pc402515d3:
add.n a2, a2, a6 # original0x402515d3
pc402515d5:
slli a2, a2, 1 # original0x402515d5
pc402515d8:
add.n a13, a13, a6 # original0x402515d8
pc402515da:
add.n a12, a11, a2 # original0x402515da
pc402515dc:
slli a13, a13, 1 # original0x402515dc
pc402515df:
l16ui a15, a12, 0 # original0x402515df
pc402515e2:
add.n a13, a11, a13 # original0x402515e2
pc402515e4:
l32r a14, fixed_4024f0d8 # original0x402515e4
pc402515e7:
l16ui a2, a13, 0 # original0x402515e7
pc402515ea:
mul16s a14, a15, a14 # original0x402515ea
pc402515ed:
mul16s a15, a2, a9 # original0x402515ed
pc402515f0:
addmi a2, a14, 0x4000 # original0x402515f0
pc402515f3:
add.n a14, a15, a2 # original0x402515f3
pc402515f5:
srai a14, a14, 15 # original0x402515f5
pc402515f8:
sub a2, a2, a15 # original0x402515f8
pc402515fb:
s16i a14, a12, 0 # original0x402515fb
pc402515fe:
srai a2, a2, 15 # original0x402515fe
pc40251601:
s16i a2, a13, 0 # original0x40251601
pc40251604:
addi.n a3, a3, 1 # original0x40251604
pc40251606:
addi.n a4, a4, 2 # original0x40251606
pc40251608:
bne a3, a7, pc402515c4 # original0x40251608
pc4025160b:
addi.n a6, a6, 1 # original0x4025160b
pc4025160d:
blt a6, a8, pc4025161a # original0x4025160d
pc40251610:
j pc40251621 # original0x40251610
pc40251615:
blti a7, 1, pc40251621 # original0x40251615
pc40251618:
movi.n a6, 0 # original0x40251618
pc4025161a:
movi.n a4, 1 # original0x4025161a
pc4025161c:
movi.n a3, 0 # original0x4025161c
pc4025161e:
j pc402515c4 # original0x4025161e
pc40251621:
l32i a8, a1, 112 # original0x40251621
pc40251624:
l32i a12, a1, 120 # original0x40251624
pc40251627:
srai a2, a8, 4 # original0x40251627
pc4025162a:
extui a3, a8, 0, 4 # original0x4025162a
pc4025162d:
add.n a2, a12, a2 # original0x4025162d
pc4025162f:
add.n a3, a12, a3 # original0x4025162f
pc40251631:
l8ui a2, a2, 0 # original0x40251631
pc40251634:
l8ui a3, a3, 0 # original0x40251634
pc40251637:
slli a2, a2, 2 # original0x40251637
pc4025163a:
or a2, a3, a2 # original0x4025163a
pc4025163d:
l32i a14, a1, 124 # original0x4025163d
pc40251640:
addi.n a5, a5, 1 # original0x40251640
pc40251642:
s32i a2, a1, 112 # original0x40251642
pc40251645:
beq a14, a5, pc4025164b # original0x40251645
pc40251648:
j pc40251518 # original0x40251648
pc4025164b:
l32i a9, a1, 148 # original0x4025164b
pc4025164e:
l32i a8, a1, 180 # original0x4025164e
pc40251651:
ssl a14 # original0x40251651
pc40251654:
sll a9, a9 # original0x40251654
pc40251657:
movi.n a10, 0 # original0x40251657
pc40251659:
l32i a15, a1, 0x114 # original0x40251659
pc4025165c:
ssr a14 # original0x4025165c
pc4025165f:
sra a13, a8 # original0x4025165f
pc40251662:
s32i a9, a1, 148 # original0x40251662
pc40251665:
s32i a10, a1, 120 # original0x40251665
pc40251668:
j pc4025176b # original0x40251668
pc4025166b:
beqz a12, pc40251760 # original0x4025166b
pc4025166e:
l32r a12, fixed_4024f0d8 # original0x4025166e
pc40251671:
movi.n a11, 0 # original0x40251671
pc40251673:
s32i a15, a1, 196 # original0x40251673
pc40251676:
l32i a13, a1, 180 # original0x40251676
pc40251679:
l32i a15, a1, 148 # original0x40251679
pc4025167c:
s32i a11, a1, 120 # original0x4025167c
pc4025167f:
mov.n a14, a12 # original0x4025167f
pc40251681:
l32i a6, a1, 140 # original0x40251681
pc40251684:
srai a15, a15, 1 # original0x40251684
pc40251687:
slli a8, a13, 1 # original0x40251687
pc4025168a:
# decoder-unreachable/check: beqz a6, 402516cc <quant_all_bands+3828>
pc4025168c:
# decoder-unreachable/check: bgei a13, 1, 40251692 <quant_all_bands+3770>
pc4025168f:
# decoder-unreachable/check: j 40251725 <quant_all_bands+3917>
pc40251692:
# decoder-unreachable/check: l32i a3, a1, 132
pc40251695:
# decoder-unreachable/check: add a7, a3, a8
pc40251697:
# decoder-unreachable/check: beqi a15, 1, 4025169d <quant_all_bands+3781>
pc4025169a:
# decoder-unreachable/check: j 40251725 <quant_all_bands+3917>
pc4025169d:
# decoder-unreachable/check: l16ui a4, a3, 0
pc402516a0:
# decoder-unreachable/check: add a6, a8, a3
pc402516a2:
# decoder-unreachable/check: l32r a9, 4024f0d8 <anti_collapse+968>
pc402516a5:
# decoder-unreachable/check: l16ui a2, a6, 0
pc402516a8:
# decoder-unreachable/check: mul16s a4, a4, a9
pc402516ab:
# decoder-unreachable/check: mul16s a5, a2, a14
pc402516ae:
# decoder-unreachable/check: addmi a2, a4, 16384
pc402516b1:
# decoder-unreachable/check: add a4, a5, a2
pc402516b3:
# decoder-unreachable/check: srai a4, a4, 15
pc402516b6:
# decoder-unreachable/check: sub a2, a2, a5
pc402516b9:
# decoder-unreachable/check: s16i a4, a3, 0
pc402516bc:
# decoder-unreachable/check: srai a2, a2, 15
pc402516bf:
# decoder-unreachable/check: s16i a2, a6, 0
pc402516c2:
# decoder-unreachable/check: addi a3, a3, 2
pc402516c4:
# decoder-unreachable/check: bne a7, a3, 4025169d <quant_all_bands+3781>
pc402516c7:
# decoder-unreachable/check: j 40252b1d <quant_all_bands+9029>
pc402516cc:
l32i a10, a1, 152 # original0x402516cc
pc402516cf:
beqz a10, pc40251725 # original0x402516cf
pc402516d2:
bgei a13, 1, pc40251711 # original0x402516d2
pc402516d5:
j pc40251725 # original0x402516d5
pc402516d8:
l16ui a7, a3, 0 # original0x402516d8
pc402516db:
l32r a10, fixed_4024f0d8 # original0x402516db
pc402516de:
l16ui a2, a4, 0 # original0x402516de
pc402516e1:
mul16s a7, a7, a10 # original0x402516e1
pc402516e4:
mul16s a10, a2, a12 # original0x402516e4
pc402516e7:
addmi a2, a7, 0x4000 # original0x402516e7
pc402516ea:
add.n a7, a2, a10 # original0x402516ea
pc402516ec:
srai a7, a7, 15 # original0x402516ec
pc402516ef:
sub a2, a2, a10 # original0x402516ef
pc402516f2:
s16i a7, a3, 0 # original0x402516f2
pc402516f5:
srai a2, a2, 15 # original0x402516f5
pc402516f8:
s16i a2, a4, 0 # original0x402516f8
pc402516fb:
addi.n a6, a6, 1 # original0x402516fb
pc402516fd:
add.n a3, a3, a11 # original0x402516fd
pc402516ff:
add.n a4, a4, a11 # original0x402516ff
pc40251701:
# decoder-unreachable/check: bnei a6, 1, 402516d8 <quant_all_bands+3840>
pc40251704:
addi.n a9, a9, 1 # original0x40251704
pc40251706:
addi.n a5, a5, 2 # original0x40251706
pc40251708:
blt a9, a13, pc4025171c # original0x40251708
pc4025170b:
j pc40251725 # original0x4025170b
pc40251711:
bnei a15, 1, pc40251725 # original0x40251711
pc40251714:
l32i a5, a1, 152 # original0x40251714
pc40251717:
slli a11, a13, 2 # original0x40251717
pc4025171a:
movi.n a9, 0 # original0x4025171a
pc4025171c:
add.n a4, a8, a5 # original0x4025171c
pc4025171e:
mov.n a3, a5 # original0x4025171e
pc40251720:
movi.n a6, 0 # original0x40251720
pc40251722:
j pc402516d8 # original0x40251722
pc40251725:
l32i a10, a1, 112 # original0x40251725
pc40251728:
l32i a11, a1, 120 # original0x40251728
pc4025172b:
l32i a9, a1, 124 # original0x4025172b
pc4025172e:
addi.n a11, a11, 1 # original0x4025172e
pc40251730:
ssl a13 # original0x40251730
pc40251733:
sll a13, a10 # original0x40251733
pc40251736:
add.n a2, a11, a9 # original0x40251736
pc40251738:
or a10, a10, a13 # original0x40251738
pc4025173b:
s32i a11, a1, 120 # original0x4025173b
pc4025173e:
movi.n a11, 1 # original0x4025173e
pc40251740:
xor a3, a15, a11 # original0x40251740
pc40251743:
extui a2, a2, 31, 1 # original0x40251743
pc40251746:
s32i a10, a1, 112 # original0x40251746
pc40251749:
mov.n a13, a8 # original0x40251749
pc4025174b:
bnone a3, a2, pc40251751 # original0x4025174b
pc4025174e:
j pc40251681 # original0x4025174e
pc40251751:
movi.n a12, 0 # original0x40251751
pc40251753:
s32i a15, a1, 148 # original0x40251753
pc40251756:
s32i a12, a1, 124 # original0x40251756
pc40251759:
l32i a15, a1, 196 # original0x40251759
pc4025175c:
j pc4025176b # original0x4025175c
pc40251760:
movi.n a14, 0 # original0x40251760
pc40251762:
l32i a13, a1, 180 # original0x40251762
pc40251765:
s32i a14, a1, 124 # original0x40251765
pc40251768:
s32i a12, a1, 120 # original0x40251768
pc4025176b:
bgei a13, 2, pc40251781 # original0x4025176b
pc4025176e:
l32i.n a6, a1, 32 # original0x4025176e
pc40251770:
s32i a6, a1, 140 # original0x40251770
pc40251773:
j pc402517e0 # original0x40251773
pc40251776:
mov.n a13, a10 # original0x40251776
pc40251778:
s32i a12, a1, 120 # original0x40251778
pc4025177b:
s32i a12, a1, 124 # original0x4025177b
pc4025177e:
j pc402517e0 # original0x4025177e
pc40251781:
l32i a8, a1, 140 # original0x40251781
pc40251784:
# decoder-unreachable/check: beqz a8, 402517b6 <quant_all_bands+4062>
pc40251786:
# decoder-unreachable/check: j 40251798 <quant_all_bands+4032>
pc40251789:
# decoder-unreachable/check: l32i a9, a1, 168
pc4025178c:
# decoder-unreachable/check: l32i a13, a1, 180
pc4025178f:
# decoder-unreachable/check: s32i a12, a1, 120
pc40251792:
# decoder-unreachable/check: s32i a9, a1, 152
pc40251795:
# decoder-unreachable/check: s32i a12, a1, 124
pc40251798:
# decoder-unreachable/check: l32i a10, a1, 124
pc4025179b:
# decoder-unreachable/check: l32i a11, a1, 148
pc4025179e:
# decoder-unreachable/check: l32i a5, a1, 312
pc402517a1:
# decoder-unreachable/check: l32i a2, a1, 132
pc402517a4:
# decoder-unreachable/check: ssl a10
pc402517a7:
# decoder-unreachable/check: sll a4, a13
pc402517aa:
# decoder-unreachable/check: ssr a10
pc402517ad:
# decoder-unreachable/check: sra a3, a11
pc402517b0:
# decoder-unreachable/check: or a1, a1, a1
pc402517b3:
# decoder-unreachable/check: call0 4024d92c <deinterleave_hadamard>
pc402517b6:
l32i.n a12, a1, 32 # original0x402517b6
pc402517b8:
l32i a14, a1, 152 # original0x402517b8
pc402517bb:
s32i a12, a1, 140 # original0x402517bb
pc402517be:
beqz.n a14, pc402517e0 # original0x402517be
pc402517c0:
l32i a8, a1, 124 # original0x402517c0
pc402517c3:
l32i a9, a1, 148 # original0x402517c3
pc402517c6:
l32i a5, a1, 0x138 # original0x402517c6
pc402517c9:
l32i a2, a1, 152 # original0x402517c9
pc402517cc:
ssl a8 # original0x402517cc
pc402517cf:
sll a4, a13 # original0x402517cf
pc402517d2:
ssr a8 # original0x402517d2
pc402517d5:
sra a3, a9 # original0x402517d5
pc402517d8:
call0 fixed_4024d92c # original0x402517d8
pc402517db:
l32i.n a10, a1, 32 # original0x402517db
pc402517dd:
s32i a10, a1, 140 # original0x402517dd
pc402517e0:
l32i.n a3, a1, 40 # original0x402517e0
pc402517e2:
l32i a11, a1, 0x1ac # original0x402517e2
pc402517e5:
l32i.n a4, a3, 8 # original0x402517e5
pc402517e7:
addi.n a2, a11, 1 # original0x402517e7
pc402517e9:
mull a2, a2, a4 # original0x402517e9
pc402517ec:
l32i.n a5, a1, 44 # original0x402517ec
pc402517ee:
l32i a4, a3, 88 # original0x402517ee
pc402517f1:
add.n a2, a2, a5 # original0x402517f1
pc402517f3:
slli a2, a2, 1 # original0x402517f3
pc402517f6:
add.n a2, a4, a2 # original0x402517f6
pc402517f8:
l16si a2, a2, 0 # original0x402517f8
pc402517fb:
l32i a4, a3, 92 # original0x402517fb
pc402517fe:
l32i a12, a1, 188 # original0x402517fe
pc40251801:
add.n a2, a4, a2 # original0x40251801
pc40251803:
l8ui a6, a2, 0 # original0x40251803
pc40251806:
addi.n a3, a12, -1 # original0x40251806
pc40251808:
addi.n a5, a6, 1 # original0x40251808
pc4025180a:
srai a5, a5, 1 # original0x4025180a
pc4025180d:
add.n a4, a2, a5 # original0x4025180d
pc4025180f:
l8ui a4, a4, 0 # original0x4025180f
pc40251812:
l32i.n a11, a1, 52 # original0x40251812
pc40251814:
l32i.n a10, a1, 60 # original0x40251814
pc40251816:
bge a4, a3, pc40251821 # original0x40251816
pc40251819:
mov.n a4, a5 # original0x40251819
pc4025181b:
add.n a5, a6, a5 # original0x4025181b
pc4025181d:
j pc40251825 # original0x4025181d
pc40251821:
mov.n a6, a5 # original0x40251821
pc40251823:
movi.n a4, 0 # original0x40251823
pc40251825:
addi.n a5, a5, 1 # original0x40251825
pc40251827:
srai a5, a5, 1 # original0x40251827
pc4025182a:
add.n a7, a2, a5 # original0x4025182a
pc4025182c:
l8ui a7, a7, 0 # original0x4025182c
pc4025182f:
bge a7, a3, pc40251836 # original0x4025182f
pc40251832:
mov.n a4, a5 # original0x40251832
pc40251834:
mov.n a5, a6 # original0x40251834
pc40251836:
add.n a6, a5, a4 # original0x40251836
pc40251838:
addi.n a6, a6, 1 # original0x40251838
pc4025183a:
srai a6, a6, 1 # original0x4025183a
pc4025183d:
add.n a7, a2, a6 # original0x4025183d
pc4025183f:
l8ui a7, a7, 0 # original0x4025183f
pc40251842:
bge a7, a3, pc40251849 # original0x40251842
pc40251845:
mov.n a4, a6 # original0x40251845
pc40251847:
mov.n a6, a5 # original0x40251847
pc40251849:
add.n a5, a4, a6 # original0x40251849
pc4025184b:
addi.n a5, a5, 1 # original0x4025184b
pc4025184d:
srai a5, a5, 1 # original0x4025184d
pc40251850:
add.n a7, a2, a5 # original0x40251850
pc40251852:
l8ui a7, a7, 0 # original0x40251852
pc40251855:
bge a7, a3, pc4025185d # original0x40251855
pc40251858:
mov.n a4, a5 # original0x40251858
pc4025185a:
or a5, a6, a6 # original0x4025185a
pc4025185d:
add.n a8, a4, a5 # original0x4025185d
pc4025185f:
addi.n a8, a8, 1 # original0x4025185f
pc40251861:
srai a8, a8, 1 # original0x40251861
pc40251864:
add.n a6, a2, a8 # original0x40251864
pc40251866:
l8ui a6, a6, 0 # original0x40251866
pc40251869:
bge a6, a3, pc40251870 # original0x40251869
pc4025186c:
mov.n a4, a8 # original0x4025186c
pc4025186e:
mov.n a8, a5 # original0x4025186e
pc40251870:
add.n a5, a8, a4 # original0x40251870
pc40251872:
addi.n a5, a5, 1 # original0x40251872
pc40251874:
srai a5, a5, 1 # original0x40251874
pc40251877:
add.n a6, a2, a5 # original0x40251877
pc40251879:
l8ui a6, a6, 0 # original0x40251879
pc4025187c:
mov.n a7, a5 # original0x4025187c
pc4025187e:
bge a6, a3, pc4025188c # original0x4025187e
pc40251881:
add.n a4, a2, a8 # original0x40251881
pc40251883:
l8ui a6, a4, 0 # original0x40251883
pc40251886:
mov.n a7, a8 # original0x40251886
pc40251888:
mov.n a4, a5 # original0x40251888
pc4025188a:
mov.n a5, a8 # original0x4025188a
pc4025188c:
sub a6, a6, a3 # original0x4025188c
pc4025188f:
bnez.n a4, pc40251894 # original0x4025188f
pc40251891:
j pc4025286c # original0x40251891
pc40251894:
add.n a8, a2, a4 # original0x40251894
pc40251896:
l8ui a9, a8, 0 # original0x40251896
pc40251899:
mov.n a8, a4 # original0x40251899
pc4025189b:
sub a3, a3, a9 # original0x4025189b
pc4025189e:
blt a6, a3, pc402518a4 # original0x4025189e
pc402518a1:
j pc40252bfc # original0x402518a1
pc402518a4:
beqz.n a5, pc402518a9 # original0x402518a4
pc402518a6:
j pc40252bf8 # original0x402518a6
pc402518a9:
j pc4025191e # original0x402518a9
pc402518ac:
add.n a3, a3, a5 # original0x402518ac
pc402518ae:
addi.n a4, a4, -1 # original0x402518ae
pc402518b0:
s32i a3, a1, 64 # original0x402518b0
pc402518b3:
add.n a5, a2, a4 # original0x402518b3
pc402518b5:
beqz a4, pc4025191e # original0x402518b5
pc402518b8:
l8ui a5, a5, 0 # original0x402518b8
pc402518bb:
addi.n a5, a5, 1 # original0x402518bb
pc402518bd:
sub a3, a3, a5 # original0x402518bd
pc402518c0:
s32i a3, a1, 64 # original0x402518c0
pc402518c3:
bltz a3, pc402518ac # original0x402518c3
pc402518c6:
blti a4, 8, pc402518d9 # original0x402518c6
pc402518c9:
extui a2, a4, 0, 3 # original0x402518c9
pc402518cc:
srai a4, a4, 3 # original0x402518cc
pc402518cf:
addi.n a2, a2, 8 # original0x402518cf
pc402518d1:
addi.n a4, a4, -1 # original0x402518d1
pc402518d3:
ssl a4 # original0x402518d3
pc402518d6:
sll a4, a2 # original0x402518d6
pc402518d9:
l32i a14, a1, 140 # original0x402518d9
pc402518dc:
# decoder-unreachable/check: beqz a14, 40251904 <quant_all_bands+4396>
pc402518df:
# decoder-unreachable/check: l32i a2, a1, 76
pc402518e2:
# decoder-unreachable/check: l32r a8, 4024f0bc <anti_collapse+940>
pc402518e5:
# decoder-unreachable/check: s32i a2, a1, 8
pc402518e8:
# decoder-unreachable/check: l32i a2, a1, 36
pc402518eb:
# decoder-unreachable/check: s32i a8, a1, 0
pc402518ed:
# decoder-unreachable/check: s32i a2, a1, 4
pc402518ef:
# decoder-unreachable/check: l32i a2, a1, 132
pc402518f2:
# decoder-unreachable/check: mov a7, a10
pc402518f4:
# decoder-unreachable/check: mov a6, a13
pc402518f6:
# decoder-unreachable/check: mov a5, a11
pc402518f8:
# decoder-unreachable/check: movi a3, 2
pc402518fa:
# decoder-unreachable/check: call0 40248cb4 <alg_quant>
pc402518fd:
# decoder-unreachable/check: s32i a2, a1, 112
pc40251900:
# decoder-unreachable/check: j 402519b3 <quant_all_bands+4571>
pc40251904:
l32r a9, fixed_4024f0bc # original0x40251904
pc40251907:
l32i a2, a1, 132 # original0x40251907
pc4025190a:
mov.n a7, a10 # original0x4025190a
pc4025190c:
s32i.n a9, a1, 0 # original0x4025190c
pc4025190e:
mov.n a6, a13 # original0x4025190e
pc40251910:
mov.n a5, a11 # original0x40251910
pc40251912:
movi a3, 2 # original0x40251912
pc40251915:
call0 fixed_402493b0 # original0x40251915
pc40251918:
s32i a2, a1, 112 # original0x40251918
pc4025191b:
j pc402519b3 # original0x4025191b
pc4025191e:
l32i.n a2, a1, 36 # original0x4025191e
pc40251920:
# decoder-unreachable/check: bnez a2, 40251925 <quant_all_bands+4429>
pc40251922:
# decoder-unreachable/check: j 40252aee <quant_all_bands+8982>
pc40251925:
movi.n a10, 1 # original0x40251925
pc40251927:
l32i a11, a1, 112 # original0x40251927
pc4025192a:
ssl a13 # original0x4025192a
pc4025192d:
sll a4, a10 # original0x4025192d
pc40251930:
addi.n a4, a4, -1 # original0x40251930
pc40251932:
and a11, a11, a4 # original0x40251932
pc40251935:
s32i a11, a1, 112 # original0x40251935
pc40251938:
bnez.n a11, pc40251948 # original0x40251938
pc4025193a:
movi.n a4, 2 # original0x4025193a
pc4025193c:
l32i a2, a1, 132 # original0x4025193c
pc4025193f:
mov.n a3, a4 # original0x4025193f
pc40251941:
call0 fixed_40242a14 # original0x40251941
pc40251944:
j pc402519b3 # original0x40251944
pc40251948:
l32r a3, fixed_402507b0 # original0x40251948
pc4025194b:
l32i a2, a1, 72 # original0x4025194b
pc4025194e:
l32r a5, fixed_402507b4 # original0x4025194e
pc40251951:
mull a2, a2, a3 # original0x40251951
pc40251954:
l32i a12, a1, 152 # original0x40251954
pc40251957:
add.n a2, a2, a5 # original0x40251957
pc40251959:
mull a3, a2, a3 # original0x40251959
pc4025195c:
add.n a3, a3, a5 # original0x4025195c
pc4025195e:
beqz.n a12, pc40251990 # original0x4025195e
pc40251960:
l32r a7, fixed_4024f0f8 # original0x40251960
pc40251963:
movi.n a5, -4 # original0x40251963
pc40251965:
l16ui a6, a12, 0 # original0x40251965
pc40251968:
and a2, a2, a7 # original0x40251968
pc4025196b:
movi.n a4, 4 # original0x4025196b
pc4025196d:
mov.n a14, a5 # original0x4025196d
pc4025196f:
l32i a8, a1, 132 # original0x4025196f
pc40251972:
movnez a14, a4, a2 # original0x40251972
pc40251975:
add.n a2, a14, a6 # original0x40251975
pc40251977:
s16i a2, a8, 0 # original0x40251977
pc4025197a:
l16ui a2, a12, 2 # original0x4025197a
pc4025197d:
and a7, a3, a7 # original0x4025197d
pc40251980:
moveqz a4, a5, a7 # original0x40251980
pc40251983:
add.n a2, a4, a2 # original0x40251983
pc40251985:
s32i a3, a1, 72 # original0x40251985
pc40251988:
s16i a2, a8, 2 # original0x40251988
pc4025198b:
mov.n a2, a8 # original0x4025198b
pc4025198d:
j pc402519a8 # original0x4025198d
pc40251990:
l32i a9, a1, 132 # original0x40251990
pc40251993:
srai a2, a2, 20 # original0x40251993
pc40251996:
s16i a2, a9, 0 # original0x40251996
pc40251999:
s32i a3, a1, 72 # original0x40251999
pc4025199c:
srai a3, a3, 20 # original0x4025199c
pc4025199f:
s16i a3, a9, 2 # original0x4025199f
pc402519a2:
s32i a4, a1, 112 # original0x402519a2
pc402519a5:
or a2, a9, a9 # original0x402519a5
pc402519a8:
l32i a5, a1, 76 # original0x402519a8
pc402519ab:
l32r a4, fixed_4024f0bc # original0x402519ab
pc402519ae:
movi.n a3, 2 # original0x402519ae
pc402519b0:
call0 fixed_402496bc # original0x402519b0
pc402519b3:
l32i a10, a1, 112 # original0x402519b3
pc402519b6:
l32i.n a2, a1, 36 # original0x402519b6
pc402519b8:
extui a12, a10, 0, 8 # original0x402519b8
pc402519bb:
# decoder-unreachable/check: bnez a2, 402519c0 <quant_all_bands+4584>
pc402519bd:
# decoder-unreachable/check: j 40252af0 <quant_all_bands+8984>
pc402519c0:
bgei a13, 2, pc402519c6 # original0x402519c0
pc402519c3:
j pc40251b41 # original0x402519c3
pc402519c6:
l32i a14, a1, 124 # original0x402519c6
pc402519c9:
l32i a11, a1, 148 # original0x402519c9
pc402519cc:
ssl a14 # original0x402519cc
pc402519cf:
sll a6, a13 # original0x402519cf
pc402519d2:
ssr a14 # original0x402519d2
pc402519d5:
sra a12, a11 # original0x402519d5
pc402519d8:
mull a8, a12, a6 # original0x402519d8
pc402519db:
s32i a6, a1, 0x158 # original0x402519db
pc402519de:
s32i a8, a1, 152 # original0x402519de
pc402519e1:
call0 fixed_402428c4 # original0x402519e1
pc402519e4:
s32i a2, a1, 92 # original0x402519e4
pc402519e7:
l32i a2, a1, 152 # original0x402519e7
pc402519ea:
s32i a3, a1, 96 # original0x402519ea
pc402519ed:
movi.n a4, 0 # original0x402519ed
pc402519ef:
movi.n a3, 2 # original0x402519ef
pc402519f1:
call0 fixed_402428ec # original0x402519f1
pc402519f4:
l32i a9, a1, 0x138 # original0x402519f4
pc402519f7:
mov.n a14, a2 # original0x402519f7
pc402519f9:
l32i a6, a1, 0x158 # original0x402519f9
pc402519fc:
bnez.n a9, pc40251a28 # original0x402519fc
pc402519fe:
bgei a6, 1, pc40251a04 # original0x402519fe
pc40251a01:
j pc40251a9c # original0x40251a01
pc40251a04:
bgei a12, 1, pc40251a0a # original0x40251a04
pc40251a07:
j pc40251a9c # original0x40251a07
pc40251a0a:
slli a5, a12, 1 # original0x40251a0a
pc40251a0d:
slli a11, a12, 2 # original0x40251a0d
pc40251a10:
l32i a12, a1, 132 # original0x40251a10
pc40251a13:
mov.n a10, a5 # original0x40251a13
pc40251a15:
slli a6, a6, 1 # original0x40251a15
pc40251a18:
mov.n a7, a2 # original0x40251a18
pc40251a1a:
add.n a5, a12, a5 # original0x40251a1a
pc40251a1c:
add.n a9, a6, a2 # original0x40251a1c
pc40251a1e:
neg a10, a10 # original0x40251a1e
pc40251a21:
neg a11, a11 # original0x40251a21
pc40251a24:
j pc40251a91 # original0x40251a24
pc40251a28:
l32r a2, fixed_4024f14c # original0x40251a28
pc40251a2b:
add.n a7, a6, a2 # original0x40251a2b
pc40251a2d:
blti a6, 1, pc40251a9c # original0x40251a2d
pc40251a30:
blti a12, 1, pc40251a9c # original0x40251a30
pc40251a33:
l32r a3, fixed_402507b8 # original0x40251a33
pc40251a36:
slli a9, a6, 3 # original0x40251a36
pc40251a39:
slli a7, a7, 2 # original0x40251a39
pc40251a3c:
addi a2, a3, -8 # original0x40251a3c
pc40251a3f:
add.n a7, a7, a3 # original0x40251a3f
pc40251a41:
mov.n a8, a14 # original0x40251a41
pc40251a43:
add.n a9, a2, a9 # original0x40251a43
pc40251a45:
slli a6, a6, 1 # original0x40251a45
pc40251a48:
l32i a4, a1, 132 # original0x40251a48
pc40251a4b:
j pc40251a64 # original0x40251a4b
pc40251a50:
l16si a5, a2, 0 # original0x40251a50
pc40251a53:
addi.n a2, a2, 2 # original0x40251a53
pc40251a55:
s16i a5, a3, 0 # original0x40251a55
pc40251a58:
add.n a3, a3, a6 # original0x40251a58
pc40251a5a:
bne a10, a2, pc40251a50 # original0x40251a5a
pc40251a5d:
addi.n a7, a7, 4 # original0x40251a5d
pc40251a5f:
addi.n a8, a8, 2 # original0x40251a5f
pc40251a61:
beq a9, a7, pc40251a9c # original0x40251a61
pc40251a64:
l32i.n a2, a7, 0 # original0x40251a64
pc40251a66:
mov.n a3, a8 # original0x40251a66
pc40251a68:
mull a2, a12, a2 # original0x40251a68
pc40251a6b:
add.n a10, a12, a2 # original0x40251a6b
pc40251a6d:
slli a10, a10, 1 # original0x40251a6d
pc40251a70:
slli a2, a2, 1 # original0x40251a70
pc40251a73:
add.n a2, a4, a2 # original0x40251a73
pc40251a75:
add.n a10, a4, a10 # original0x40251a75
pc40251a77:
j pc40251a50 # original0x40251a77
pc40251a7c:
l16si a4, a2, 0 # original0x40251a7c
pc40251a7f:
addi.n a2, a2, 2 # original0x40251a7f
pc40251a81:
s16i a4, a3, 0 # original0x40251a81
pc40251a84:
add.n a3, a3, a6 # original0x40251a84
pc40251a86:
bne a5, a2, pc40251a7c # original0x40251a86
pc40251a89:
addi.n a7, a7, 2 # original0x40251a89
pc40251a8b:
sub a5, a8, a11 # original0x40251a8b
pc40251a8e:
beq a9, a7, pc40251a9c # original0x40251a8e
pc40251a91:
add.n a8, a10, a5 # original0x40251a91
pc40251a93:
mov.n a3, a7 # original0x40251a93
pc40251a95:
mov.n a2, a8 # original0x40251a95
pc40251a97:
j pc40251a7c # original0x40251a97
pc40251a9c:
l32i a2, a1, 132 # original0x40251a9c
pc40251a9f:
l32i a4, a1, 152 # original0x40251a9f
pc40251aa2:
or a3, a14, a14 # original0x40251aa2
pc40251aa5:
movi a5, 2 # original0x40251aa5
pc40251aa8:
call0 fixed_402429b0 # original0x40251aa8
pc40251aab:
l32i a2, a1, 92 # original0x40251aab
pc40251aae:
l32i a3, a1, 96 # original0x40251aae
pc40251ab1:
call0 fixed_402428d8 # original0x40251ab1
pc40251ab4:
j pc40251b41 # original0x40251ab4
pc40251ab8:
s32i a15, a1, 152 # original0x40251ab8
pc40251abb:
mov.n a15, a2 # original0x40251abb
pc40251abd:
l32i a9, a1, 112 # original0x40251abd
pc40251ac0:
l32i a8, a1, 148 # original0x40251ac0
pc40251ac3:
srai a13, a13, 1 # original0x40251ac3
pc40251ac6:
ssr a13 # original0x40251ac6
pc40251ac9:
srl a2, a9 # original0x40251ac9
pc40251acc:
slli a8, a8, 1 # original0x40251acc
pc40251acf:
or a9, a9, a2 # original0x40251acf
pc40251ad2:
s32i a8, a1, 148 # original0x40251ad2
pc40251ad5:
s32i a9, a1, 112 # original0x40251ad5
pc40251ad8:
srai a10, a8, 1 # original0x40251ad8
pc40251adb:
blti a13, 1, pc40251b30 # original0x40251adb
pc40251ade:
blti a10, 1, pc40251b30 # original0x40251ade
pc40251ae1:
l32i a3, a1, 132 # original0x40251ae1
pc40251ae4:
slli a11, a13, 1 # original0x40251ae4
pc40251ae7:
add.n a12, a11, a3 # original0x40251ae7
pc40251ae9:
slli a9, a13, 2 # original0x40251ae9
pc40251aec:
j pc40251b24 # original0x40251aec
pc40251af0:
l16si a7, a4, 0 # original0x40251af0
pc40251af3:
l16si a2, a5, 0 # original0x40251af3
pc40251af6:
l32r a11, fixed_4024f0d8 # original0x40251af6
pc40251af9:
mull a7, a7, a14 # original0x40251af9
pc40251afc:
mull a8, a2, a11 # original0x40251afc
pc40251aff:
addmi a2, a7, 0x4000 # original0x40251aff
pc40251b02:
add.n a7, a8, a2 # original0x40251b02
pc40251b04:
srai a7, a7, 15 # original0x40251b04
pc40251b07:
sub a2, a2, a8 # original0x40251b07
pc40251b0a:
s16i a7, a4, 0 # original0x40251b0a
pc40251b0d:
srai a2, a2, 15 # original0x40251b0d
pc40251b10:
s16i a2, a5, 0 # original0x40251b10
pc40251b13:
addi.n a6, a6, 1 # original0x40251b13
pc40251b15:
add.n a4, a4, a9 # original0x40251b15
pc40251b17:
add.n a5, a5, a9 # original0x40251b17
pc40251b19:
bne a10, a6, pc40251af0 # original0x40251b19
pc40251b1c:
addi.n a3, a3, 2 # original0x40251b1c
pc40251b1e:
l32i a11, a1, 140 # original0x40251b1e
pc40251b21:
beq a12, a3, pc40251b30 # original0x40251b21
pc40251b24:
add.n a5, a3, a11 # original0x40251b24
pc40251b26:
mov.n a4, a3 # original0x40251b26
pc40251b28:
movi.n a6, 0 # original0x40251b28
pc40251b2a:
s32i a11, a1, 140 # original0x40251b2a
pc40251b2d:
j pc40251af0 # original0x40251b2d
pc40251b30:
l32i a12, a1, 120 # original0x40251b30
pc40251b33:
addi.n a15, a15, 1 # original0x40251b33
pc40251b35:
bne a15, a12, pc40251abd # original0x40251b35
pc40251b38:
l32i a15, a1, 152 # original0x40251b38
pc40251b3b:
j pc40251b4f # original0x40251b3b
pc40251b41:
l32i a8, a1, 120 # original0x40251b41
pc40251b44:
movi.n a2, 0 # original0x40251b44
pc40251b46:
l32r a14, fixed_4024f0d8 # original0x40251b46
pc40251b49:
blti a8, 1, pc40251b4f # original0x40251b49
pc40251b4c:
j pc40251ab8 # original0x40251b4c
pc40251b4f:
l32i a9, a1, 124 # original0x40251b4f
pc40251b52:
beqz a9, pc40251bfd # original0x40251b52
pc40251b55:
l32r a10, fixed_402507bc # original0x40251b55
pc40251b58:
s32i a15, a1, 120 # original0x40251b58
pc40251b5b:
l32r a14, fixed_4024f0d8 # original0x40251b5b
pc40251b5e:
l32i a15, a1, 112 # original0x40251b5e
pc40251b61:
l32i a12, a1, 132 # original0x40251b61
pc40251b64:
s32i a10, a1, 148 # original0x40251b64
pc40251b67:
movi.n a9, 0 # original0x40251b67
pc40251b69:
s32i a13, a1, 152 # original0x40251b69
pc40251b6c:
l32i a11, a1, 148 # original0x40251b6c
pc40251b6f:
movi.n a3, 1 # original0x40251b6f
pc40251b71:
movi.n a2, 2 # original0x40251b71
pc40251b73:
add.n a15, a11, a15 # original0x40251b73
pc40251b75:
ssl a9 # original0x40251b75
pc40251b78:
sll a13, a3 # original0x40251b78
pc40251b7b:
ssr a9 # original0x40251b7b
pc40251b7e:
sra a11, a2 # original0x40251b7e
pc40251b81:
l8ui a15, a15, 0 # original0x40251b81
pc40251b84:
ssr a3 # original0x40251b84
pc40251b87:
sra a11, a11 # original0x40251b87
pc40251b8a:
blt a13, a3, pc40251be9 # original0x40251b8a
pc40251b8d:
movi.n a5, 0 # original0x40251b8d
pc40251b8f:
bge a11, a3, pc40251be1 # original0x40251b8f
pc40251b92:
j pc40251be9 # original0x40251b92
pc40251b95:
ssl a9 # original0x40251b95
pc40251b98:
sll a2, a3 # original0x40251b98
pc40251b9b:
slli a2, a2, 1 # original0x40251b9b
pc40251b9e:
ssl a9 # original0x40251b9e
pc40251ba1:
sll a7, a4 # original0x40251ba1
pc40251ba4:
add.n a2, a2, a5 # original0x40251ba4
pc40251ba6:
slli a2, a2, 1 # original0x40251ba6
pc40251ba9:
add.n a7, a7, a5 # original0x40251ba9
pc40251bab:
add.n a6, a12, a2 # original0x40251bab
pc40251bad:
slli a7, a7, 1 # original0x40251bad
pc40251bb0:
l16ui a8, a6, 0 # original0x40251bb0
pc40251bb3:
add.n a7, a12, a7 # original0x40251bb3
pc40251bb5:
l16ui a10, a7, 0 # original0x40251bb5
pc40251bb8:
l32r a2, fixed_4024f0d8 # original0x40251bb8
pc40251bbb:
mul16s a8, a8, a14 # original0x40251bbb
pc40251bbe:
mul16s a10, a10, a2 # original0x40251bbe
pc40251bc1:
addmi a2, a8, 0x4000 # original0x40251bc1
pc40251bc4:
add.n a8, a2, a10 # original0x40251bc4
pc40251bc6:
srai a8, a8, 15 # original0x40251bc6
pc40251bc9:
sub a2, a2, a10 # original0x40251bc9
pc40251bcc:
s16i a8, a6, 0 # original0x40251bcc
pc40251bcf:
srai a2, a2, 15 # original0x40251bcf
pc40251bd2:
s16i a2, a7, 0 # original0x40251bd2
pc40251bd5:
addi.n a3, a3, 1 # original0x40251bd5
pc40251bd7:
addi.n a4, a4, 2 # original0x40251bd7
pc40251bd9:
bne a11, a3, pc40251b95 # original0x40251bd9
pc40251bdc:
addi.n a5, a5, 1 # original0x40251bdc
pc40251bde:
beq a13, a5, pc40251be9 # original0x40251bde
pc40251be1:
movi.n a4, 1 # original0x40251be1
pc40251be3:
movi.n a3, 0 # original0x40251be3
pc40251be5:
j pc40251b95 # original0x40251be5
pc40251be9:
l32i a8, a1, 124 # original0x40251be9
pc40251bec:
addi.n a9, a9, 1 # original0x40251bec
pc40251bee:
beq a9, a8, pc40251bf4 # original0x40251bee
pc40251bf1:
j pc40251b6c # original0x40251bf1
pc40251bf4:
s32i a15, a1, 112 # original0x40251bf4
pc40251bf7:
l32i a13, a1, 152 # original0x40251bf7
pc40251bfa:
l32i a15, a1, 120 # original0x40251bfa
pc40251bfd:
l32i a9, a1, 124 # original0x40251bfd
pc40251c00:
l32i a10, a1, 236 # original0x40251c00
pc40251c03:
ssl a9 # original0x40251c03
pc40251c06:
sll a12, a13 # original0x40251c06
pc40251c09:
beqz.n a10, pc40251c35 # original0x40251c09
pc40251c0b:
l32r a2, fixed_4024f0cc # original0x40251c0b
pc40251c0e:
call0 fixed_40246ec4 # original0x40251c0e
pc40251c11:
l32i a11, a1, 132 # original0x40251c11
pc40251c14:
slli a2, a2, 16 # original0x40251c14
pc40251c17:
l16ui a3, a11, 0 # original0x40251c17
pc40251c1a:
srai a4, a2, 16 # original0x40251c1a
pc40251c1d:
mul16s a3, a3, a4 # original0x40251c1d
pc40251c20:
l32i a14, a1, 236 # original0x40251c20
pc40251c23:
srai a3, a3, 15 # original0x40251c23
pc40251c26:
s16i a3, a14, 0 # original0x40251c26
pc40251c29:
l16ui a2, a11, 2 # original0x40251c29
pc40251c2c:
mul16s a2, a2, a4 # original0x40251c2c
pc40251c2f:
srai a2, a2, 15 # original0x40251c2f
pc40251c32:
s16i a2, a14, 2 # original0x40251c32
pc40251c35:
l32i a8, a1, 132 # original0x40251c35
pc40251c38:
l32i a9, a1, 252 # original0x40251c38
pc40251c3b:
l16ui a3, a8, 2 # original0x40251c3b
pc40251c3e:
l32i a11, a1, 228 # original0x40251c3e
pc40251c41:
mul16s a3, a3, a9 # original0x40251c41
pc40251c44:
l32i.n a2, a1, 36 # original0x40251c44
pc40251c46:
s16i a3, a11, 0 # original0x40251c46
pc40251c49:
l16ui a3, a8, 0 # original0x40251c49
pc40251c4c:
l32i a14, a1, 0x100 # original0x40251c4c
pc40251c4f:
movi.n a10, 1 # original0x40251c4f
pc40251c51:
ssl a12 # original0x40251c51
pc40251c54:
sll a12, a10 # original0x40251c54
pc40251c57:
mul16s a3, a3, a14 # original0x40251c57
pc40251c5a:
l32i a6, a1, 112 # original0x40251c5a
pc40251c5d:
addi.n a12, a12, -1 # original0x40251c5d
pc40251c5f:
and a12, a12, a6 # original0x40251c5f
pc40251c62:
s16i a3, a11, 2 # original0x40251c62
pc40251c65:
extui a12, a12, 0, 8 # original0x40251c65
pc40251c68:
# decoder-unreachable/check: bnez a2, 40251c6d <quant_all_bands+5269>
pc40251c6a:
# decoder-unreachable/check: j 40252766 <quant_all_bands+8078>
pc40251c6d:
l32i a8, a1, 172 # original0x40251c6d
pc40251c70:
l32i a9, a1, 0x110 # original0x40251c70
pc40251c73:
l16si a3, a8, 0 # original0x40251c73
pc40251c76:
l16si a2, a8, 2 # original0x40251c76
pc40251c79:
mull a3, a3, a9 # original0x40251c79
pc40251c7c:
mull a2, a2, a9 # original0x40251c7c
pc40251c7f:
srai a3, a3, 15 # original0x40251c7f
pc40251c82:
srai a2, a2, 15 # original0x40251c82
pc40251c85:
s16i a3, a8, 0 # original0x40251c85
pc40251c88:
s16i a2, a8, 2 # original0x40251c88
pc40251c8b:
l16si a2, a15, 0 # original0x40251c8b
pc40251c8e:
l32i a10, a1, 216 # original0x40251c8e
pc40251c91:
l16si a3, a15, 2 # original0x40251c91
pc40251c94:
mull a2, a2, a10 # original0x40251c94
pc40251c97:
mull a3, a3, a10 # original0x40251c97
pc40251c9a:
slli a2, a2, 1 # original0x40251c9a
pc40251c9d:
srai a2, a2, 16 # original0x40251c9d
pc40251ca0:
srai a3, a3, 15 # original0x40251ca0
pc40251ca3:
s16i a3, a15, 2 # original0x40251ca3
pc40251ca6:
s16i a2, a15, 0 # original0x40251ca6
pc40251ca9:
l16si a3, a8, 0 # original0x40251ca9
pc40251cac:
sub a2, a3, a2 # original0x40251cac
pc40251caf:
s16i a2, a8, 0 # original0x40251caf
pc40251cb2:
l16ui a2, a15, 0 # original0x40251cb2
pc40251cb5:
l16ui a4, a15, 2 # original0x40251cb5
pc40251cb8:
add.n a3, a3, a2 # original0x40251cb8
pc40251cba:
s16i a3, a15, 0 # original0x40251cba
pc40251cbd:
l16si a2, a8, 2 # original0x40251cbd
pc40251cc0:
sub a3, a2, a4 # original0x40251cc0
pc40251cc3:
s16i a3, a8, 2 # original0x40251cc3
pc40251cc6:
l16ui a3, a15, 2 # original0x40251cc6
pc40251cc9:
add.n a2, a2, a3 # original0x40251cc9
pc40251ccb:
s16i a2, a15, 2 # original0x40251ccb
pc40251cce:
j pc40252ae5 # original0x40251cce
pc40251cd1:
l32r a11, fixed_4024f0bc # original0x40251cd1
pc40251cd4:
l32i a12, a1, 112 # original0x40251cd4
pc40251cd7:
movi.n a14, 0 # original0x40251cd7
pc40251cd9:
s32i a11, a1, 140 # original0x40251cd9
pc40251cdc:
s32i a12, a1, 0x114 # original0x40251cdc
pc40251cdf:
s32i a14, a1, 240 # original0x40251cdf
pc40251ce2:
l32i a8, a1, 188 # original0x40251ce2
pc40251ce5:
sub a2, a8, a2 # original0x40251ce5
pc40251ce8:
extui a3, a2, 31, 1 # original0x40251ce8
pc40251ceb:
add.n a2, a3, a2 # original0x40251ceb
pc40251ced:
srai a2, a2, 1 # original0x40251ced
pc40251cf0:
s32i a2, a1, 124 # original0x40251cf0
pc40251cf3:
bge a8, a2, pc40251cf9 # original0x40251cf3
pc40251cf6:
s32i a8, a1, 124 # original0x40251cf6
pc40251cf9:
l32i a10, a1, 124 # original0x40251cf9
pc40251cfc:
movi.n a9, 0 # original0x40251cfc
pc40251cfe:
movgez a9, a10, a10 # original0x40251cfe
pc40251d01:
l32i a12, a1, 228 # original0x40251d01
pc40251d04:
l32i a11, a1, 252 # original0x40251d04
pc40251d07:
l32i a14, a1, 188 # original0x40251d07
pc40251d0a:
s32i a9, a1, 124 # original0x40251d0a
pc40251d0d:
sub a2, a11, a12 # original0x40251d0d
pc40251d10:
sub a14, a14, a9 # original0x40251d10
pc40251d13:
l32i a8, a1, 0x114 # original0x40251d13
pc40251d16:
l32i a9, a1, 180 # original0x40251d16
pc40251d19:
l32i a10, a1, 124 # original0x40251d19
pc40251d1c:
s32i a14, a1, 0x100 # original0x40251d1c
pc40251d1f:
s32i a2, a1, 64 # original0x40251d1f
pc40251d22:
ssr a9 # original0x40251d22
pc40251d25:
sra a12, a8 # original0x40251d25
pc40251d28:
bge a10, a14, pc40251d2e # original0x40251d28
pc40251d2b:
j pc40252197 # original0x40251d2b
pc40251d2e:
l32i a14, a1, 168 # original0x40251d2e
pc40251d31:
mov.n a6, a9 # original0x40251d31
pc40251d33:
mov.n a5, a10 # original0x40251d33
pc40251d35:
s32i.n a8, a1, 16 # original0x40251d35
pc40251d37:
l32i a9, a1, 236 # original0x40251d37
pc40251d3a:
l32i a8, a1, 140 # original0x40251d3a
pc40251d3d:
l32i a10, a1, 0x1ac # original0x40251d3d
pc40251d40:
addi a11, a1, 32 # original0x40251d40
pc40251d43:
l32i a4, a1, 128 # original0x40251d43
pc40251d46:
l32i a3, a1, 172 # original0x40251d46
pc40251d49:
l32i a7, a1, 152 # original0x40251d49
pc40251d4c:
s32i.n a14, a1, 12 # original0x40251d4c
pc40251d4e:
s32i.n a8, a1, 8 # original0x40251d4e
pc40251d50:
mov.n a2, a11 # original0x40251d50
pc40251d52:
s32i.n a9, a1, 4 # original0x40251d52
pc40251d54:
s32i a10, a1, 0 # original0x40251d54
pc40251d57:
s32i a11, a1, 132 # original0x40251d57
pc40251d5a:
call0 fixed_4024e44c # original0x40251d5a
pc40251d5d:
s32i a2, a1, 236 # original0x40251d5d
pc40251d60:
l32i a11, a1, 252 # original0x40251d60
pc40251d63:
l32i a2, a1, 64 # original0x40251d63
pc40251d66:
l32i a14, a1, 228 # original0x40251d66
pc40251d69:
sub a2, a2, a11 # original0x40251d69
pc40251d6c:
l32i a8, a1, 124 # original0x40251d6c
pc40251d6f:
add.n a4, a2, a14 # original0x40251d6f
pc40251d71:
movi.n a3, 24 # original0x40251d71
pc40251d73:
add.n a2, a8, a4 # original0x40251d73
pc40251d75:
bge a3, a2, pc40251d89 # original0x40251d75
pc40251d78:
l32i a9, a1, 196 # original0x40251d78
pc40251d7b:
beqz.n a9, pc40251d89 # original0x40251d7b
pc40251d7d:
l32i a10, a1, 188 # original0x40251d7d
pc40251d80:
addi a2, a10, -24 # original0x40251d80
pc40251d83:
add a2, a2, a4 # original0x40251d83
pc40251d86:
s32i a2, a1, 0x100 # original0x40251d86
pc40251d89:
l32i.n a11, a1, 56 # original0x40251d89
pc40251d8b:
l32i a3, a1, 180 # original0x40251d8b
pc40251d8e:
l32i a2, a1, 128 # original0x40251d8e
pc40251d91:
s32i a11, a1, 112 # original0x40251d91
pc40251d94:
l32r a0, fixed_40250738 # original0x40251d94
pc40251d97:
callx0 a0 # original0x40251d97
pc40251d9a:
mov.n a14, a2 # original0x40251d9a
pc40251d9c:
l32i.n a2, a1, 32 # original0x40251d9c
pc40251d9e:
l32i a8, a1, 112 # original0x40251d9e
pc40251da1:
s32i a2, a1, 124 # original0x40251da1
pc40251da4:
bgei a8, 1, pc40251daa # original0x40251da4
pc40251da7:
j pc40251e79 # original0x40251da7
pc40251daa:
l32r a9, fixed_402507ac # original0x40251daa
pc40251dad:
s32i a14, a1, 152 # original0x40251dad
pc40251db0:
s32i a9, a1, 120 # original0x40251db0
pc40251db3:
l32i a14, a1, 120 # original0x40251db3
pc40251db6:
movi.n a9, 0 # original0x40251db6
pc40251db8:
l32i a10, a1, 124 # original0x40251db8
pc40251dbb:
# decoder-unreachable/check: beqz a10, 40251e3c <quant_all_bands+5732>
pc40251dbe:
# decoder-unreachable/check: l32i a8, a1, 128
pc40251dc1:
# decoder-unreachable/check: movi a10, 1
pc40251dc3:
# decoder-unreachable/check: ssr a9
pc40251dc6:
# decoder-unreachable/check: sra a11, a8
pc40251dc9:
# decoder-unreachable/check: ssl a9
pc40251dcc:
# decoder-unreachable/check: sll a13, a10
pc40251dcf:
# decoder-unreachable/check: ssr a10
pc40251dd2:
# decoder-unreachable/check: sra a11, a11
pc40251dd5:
# decoder-unreachable/check: blt a13, a10, 40251e3c <quant_all_bands+5732>
pc40251dd8:
# decoder-unreachable/check: movi a5, 0
pc40251dda:
# decoder-unreachable/check: bge a11, a10, 40251e30 <quant_all_bands+5720>
pc40251ddd:
# decoder-unreachable/check: j 40251e3c <quant_all_bands+5732>
pc40251de1:
# decoder-unreachable/check: ssl a9
pc40251de4:
# decoder-unreachable/check: sll a2, a3
pc40251de7:
# decoder-unreachable/check: slli a2, a2, 1
pc40251dea:
# decoder-unreachable/check: ssl a9
pc40251ded:
# decoder-unreachable/check: sll a7, a4
pc40251df0:
# decoder-unreachable/check: add a2, a2, a5
pc40251df2:
# decoder-unreachable/check: slli a2, a2, 1
pc40251df5:
# decoder-unreachable/check: add a7, a7, a5
pc40251df7:
# decoder-unreachable/check: add a6, a15, a2
pc40251df9:
# decoder-unreachable/check: slli a7, a7, 1
pc40251dfc:
# decoder-unreachable/check: l16ui a8, a6, 0
pc40251dff:
# decoder-unreachable/check: add a7, a15, a7
pc40251e01:
# decoder-unreachable/check: l32r a12, 4024f0d8 <anti_collapse+968>
pc40251e04:
# decoder-unreachable/check: l16ui a10, a7, 0
pc40251e07:
# decoder-unreachable/check: mul16s a8, a8, a12
pc40251e0a:
# decoder-unreachable/check: mul16s a10, a10, a12
pc40251e0d:
# decoder-unreachable/check: addmi a2, a8, 16384
pc40251e10:
# decoder-unreachable/check: add a8, a2, a10
pc40251e12:
# decoder-unreachable/check: srai a8, a8, 15
pc40251e15:
# decoder-unreachable/check: sub a2, a2, a10
pc40251e18:
# decoder-unreachable/check: s16i a8, a6, 0
pc40251e1b:
# decoder-unreachable/check: srai a2, a2, 15
pc40251e1e:
# decoder-unreachable/check: s16i a2, a7, 0
pc40251e21:
# decoder-unreachable/check: addi a3, a3, 1
pc40251e23:
# decoder-unreachable/check: addi a4, a4, 2
pc40251e25:
# decoder-unreachable/check: bne a11, a3, 40251de1 <quant_all_bands+5641>
pc40251e28:
# decoder-unreachable/check: addi a5, a5, 1
pc40251e2a:
# decoder-unreachable/check: l32i a12, a1, 120
pc40251e2d:
# decoder-unreachable/check: beq a13, a5, 40251e3c <quant_all_bands+5732>
pc40251e30:
# decoder-unreachable/check: movi a4, 1
pc40251e32:
# decoder-unreachable/check: movi a3, 0
pc40251e34:
# decoder-unreachable/check: s32i a12, a1, 120
pc40251e37:
# decoder-unreachable/check: j 40251de1 <quant_all_bands+5641>
pc40251e3c:
srai a2, a12, 4 # original0x40251e3c
pc40251e3f:
add.n a2, a14, a2 # original0x40251e3f
pc40251e41:
extui a12, a12, 0, 4 # original0x40251e41
pc40251e44:
add.n a12, a14, a12 # original0x40251e44
pc40251e46:
l8ui a2, a2, 0 # original0x40251e46
pc40251e49:
l8ui a12, a12, 0 # original0x40251e49
pc40251e4c:
l32i a8, a1, 112 # original0x40251e4c
pc40251e4f:
slli a2, a2, 2 # original0x40251e4f
pc40251e52:
addi.n a9, a9, 1 # original0x40251e52
pc40251e54:
or a12, a12, a2 # original0x40251e54
pc40251e57:
beq a8, a9, pc40251e5d # original0x40251e57
pc40251e5a:
j pc40251db8 # original0x40251e5a
pc40251e5d:
mov.n a9, a8 # original0x40251e5d
pc40251e5f:
l32i a14, a1, 152 # original0x40251e5f
pc40251e62:
l32i a8, a1, 180 # original0x40251e62
pc40251e65:
movi.n a10, 0 # original0x40251e65
pc40251e67:
ssr a9 # original0x40251e67
pc40251e6a:
sra a13, a8 # original0x40251e6a
pc40251e6d:
ssl a9 # original0x40251e6d
pc40251e70:
sll a14, a14 # original0x40251e70
pc40251e73:
s32i a10, a1, 152 # original0x40251e73
pc40251e76:
j pc40251f21 # original0x40251e76
pc40251e79:
l32i a13, a1, 180 # original0x40251e79
pc40251e7c:
bbci a14, 0, pc40251e82 # original0x40251e7c
pc40251e7f:
j pc40251f18 # original0x40251e7f
pc40251e82:
bgez a8, pc40251f18 # original0x40251e82
pc40251e85:
movi.n a10, 0 # original0x40251e85
pc40251e87:
s32i a10, a1, 152 # original0x40251e87
pc40251e8a:
s32i a15, a1, 120 # original0x40251e8a
pc40251e8d:
or a11, a10, a10 # original0x40251e8d
pc40251e90:
l32i a2, a1, 124 # original0x40251e90
pc40251e93:
srai a14, a14, 1 # original0x40251e93
pc40251e96:
slli a10, a13, 1 # original0x40251e96
pc40251e99:
# decoder-unreachable/check: beqz a2, 40251eed <quant_all_bands+5909>
pc40251e9c:
# decoder-unreachable/check: blti a13, 1, 40251eed <quant_all_bands+5909>
pc40251e9f:
# decoder-unreachable/check: blti a14, 1, 40251eed <quant_all_bands+5909>
pc40251ea2:
# decoder-unreachable/check: l32i a3, a1, 120
pc40251ea5:
# decoder-unreachable/check: slli a9, a13, 2
pc40251ea8:
# decoder-unreachable/check: add a15, a3, a10
pc40251eaa:
# decoder-unreachable/check: j 40251ee1 <quant_all_bands+5897>
pc40251ead:
# decoder-unreachable/check: l16ui a7, a4, 0
pc40251eb0:
# decoder-unreachable/check: l32r a10, 4024f0d8 <anti_collapse+968>
pc40251eb3:
# decoder-unreachable/check: l16ui a8, a5, 0
pc40251eb6:
# decoder-unreachable/check: mul16s a7, a7, a10
pc40251eb9:
# decoder-unreachable/check: mul16s a8, a8, a10
pc40251ebc:
# decoder-unreachable/check: addmi a2, a7, 16384
pc40251ebf:
# decoder-unreachable/check: add a7, a2, a8
pc40251ec1:
# decoder-unreachable/check: srai a7, a7, 15
pc40251ec4:
# decoder-unreachable/check: sub a2, a2, a8
pc40251ec7:
# decoder-unreachable/check: s16i a7, a4, 0
pc40251eca:
# decoder-unreachable/check: srai a2, a2, 15
pc40251ecd:
# decoder-unreachable/check: s16i a2, a5, 0
pc40251ed0:
# decoder-unreachable/check: addi a6, a6, 1
pc40251ed2:
# decoder-unreachable/check: add a4, a4, a9
pc40251ed4:
# decoder-unreachable/check: add a5, a5, a9
pc40251ed6:
# decoder-unreachable/check: bne a6, a14, 40251ead <quant_all_bands+5845>
pc40251ed9:
# decoder-unreachable/check: addi a3, a3, 2
pc40251edb:
# decoder-unreachable/check: l32i a10, a1, 140
pc40251ede:
# decoder-unreachable/check: beq a15, a3, 40251eed <quant_all_bands+5909>
pc40251ee1:
# decoder-unreachable/check: add a5, a10, a3
pc40251ee3:
# decoder-unreachable/check: mov a4, a3
pc40251ee5:
# decoder-unreachable/check: movi a6, 0
pc40251ee7:
# decoder-unreachable/check: s32i a10, a1, 140
pc40251eea:
# decoder-unreachable/check: j 40251ead <quant_all_bands+5845>
pc40251eed:
l32i a8, a1, 112 # original0x40251eed
pc40251ef0:
addi.n a11, a11, 1 # original0x40251ef0
pc40251ef2:
add.n a2, a11, a8 # original0x40251ef2
pc40251ef4:
movi.n a9, -1 # original0x40251ef4
pc40251ef6:
ssl a13 # original0x40251ef6
pc40251ef9:
sll a13, a12 # original0x40251ef9
pc40251efc:
extui a2, a2, 31, 1 # original0x40251efc
pc40251eff:
xor a3, a9, a14 # original0x40251eff
pc40251f02:
or a12, a12, a13 # original0x40251f02
pc40251f05:
mov.n a13, a10 # original0x40251f05
pc40251f07:
bany a3, a2, pc40251e90 # original0x40251f07
pc40251f0a:
movi.n a10, 0 # original0x40251f0a
pc40251f0c:
l32i a15, a1, 120 # original0x40251f0c
pc40251f0f:
s32i a11, a1, 152 # original0x40251f0f
pc40251f12:
s32i a10, a1, 112 # original0x40251f12
pc40251f15:
j pc40251f21 # original0x40251f15
pc40251f18:
movi a11, 0 # original0x40251f18
pc40251f1b:
s32i a11, a1, 112 # original0x40251f1b
pc40251f1e:
s32i a11, a1, 152 # original0x40251f1e
pc40251f21:
bgei a13, 2, pc40251f27 # original0x40251f21
pc40251f24:
j pc402528b2 # original0x40251f24
pc40251f27:
l32i a9, a1, 124 # original0x40251f27
pc40251f2a:
# decoder-unreachable/check: bnez a9, 40251f30 <quant_all_bands+5976>
pc40251f2d:
j pc40252878 # original0x40251f2d
pc40251f30:
# decoder-unreachable/check: l32i a10, a1, 112
pc40251f33:
# decoder-unreachable/check: l32i a5, a1, 312
pc40251f36:
# decoder-unreachable/check: ssl a10
pc40251f39:
# decoder-unreachable/check: sll a4, a13
pc40251f3c:
# decoder-unreachable/check: ssr a10
pc40251f3f:
# decoder-unreachable/check: sra a3, a14
pc40251f42:
# decoder-unreachable/check: or a2, a15, a15
pc40251f45:
# decoder-unreachable/check: call0 4024d92c <deinterleave_hadamard>
pc40251f48:
# decoder-unreachable/check: j 40252878 <quant_all_bands+8352>
pc40251f4b:
l32i a11, a1, 112 # original0x40251f4b
pc40251f4e:
ssl a11 # original0x40251f4e
pc40251f51:
sll a6, a13 # original0x40251f51
pc40251f54:
ssr a11 # original0x40251f54
pc40251f57:
sra a12, a14 # original0x40251f57
pc40251f5a:
mull a8, a12, a6 # original0x40251f5a
pc40251f5d:
s32i a6, a1, 0x158 # original0x40251f5d
pc40251f60:
s32i a8, a1, 140 # original0x40251f60
pc40251f63:
call0 fixed_402428c4 # original0x40251f63
pc40251f66:
s32i a2, a1, 92 # original0x40251f66
pc40251f69:
l32i a2, a1, 140 # original0x40251f69
pc40251f6c:
s32i a3, a1, 96 # original0x40251f6c
pc40251f6f:
movi a4, 0 # original0x40251f6f
pc40251f72:
movi a3, 2 # original0x40251f72
pc40251f75:
call0 fixed_402428ec # original0x40251f75
pc40251f78:
l32i a9, a1, 0x138 # original0x40251f78
pc40251f7b:
s32i a2, a1, 124 # original0x40251f7b
pc40251f7e:
l32i a6, a1, 0x158 # original0x40251f7e
pc40251f81:
bnez.n a9, pc40251fa9 # original0x40251f81
pc40251f83:
bgei a6, 1, pc40251f89 # original0x40251f83
pc40251f86:
j pc40252018 # original0x40251f86
pc40251f89:
bgei a12, 1, pc40251f8f # original0x40251f89
pc40251f8c:
j pc40252018 # original0x40251f8c
pc40251f8f:
slli a5, a12, 1 # original0x40251f8f
pc40251f92:
mov.n a10, a5 # original0x40251f92
pc40251f94:
slli a6, a6, 1 # original0x40251f94
pc40251f97:
slli a11, a12, 2 # original0x40251f97
pc40251f9a:
mov.n a7, a2 # original0x40251f9a
pc40251f9c:
add.n a5, a15, a5 # original0x40251f9c
pc40251f9e:
add.n a9, a6, a2 # original0x40251f9e
pc40251fa0:
neg a10, a10 # original0x40251fa0
pc40251fa3:
neg a11, a11 # original0x40251fa3
pc40251fa6:
j pc4025200d # original0x40251fa6
pc40251fa9:
l32r a2, fixed_4024f14c # original0x40251fa9
pc40251fac:
add.n a7, a6, a2 # original0x40251fac
pc40251fae:
blti a6, 1, pc40252018 # original0x40251fae
pc40251fb1:
blti a12, 1, pc40252018 # original0x40251fb1
pc40251fb4:
l32r a3, fixed_402507b8 # original0x40251fb4
pc40251fb7:
slli a9, a6, 3 # original0x40251fb7
pc40251fba:
slli a7, a7, 2 # original0x40251fba
pc40251fbd:
addi a2, a3, -8 # original0x40251fbd
pc40251fc0:
add.n a7, a7, a3 # original0x40251fc0
pc40251fc2:
l32i a8, a1, 124 # original0x40251fc2
pc40251fc5:
add.n a9, a2, a9 # original0x40251fc5
pc40251fc7:
slli a6, a6, 1 # original0x40251fc7
pc40251fca:
j pc40251fe1 # original0x40251fca
pc40251fcd:
l16si a4, a2, 0 # original0x40251fcd
pc40251fd0:
addi.n a2, a2, 2 # original0x40251fd0
pc40251fd2:
s16i a4, a3, 0 # original0x40251fd2
pc40251fd5:
add.n a3, a3, a6 # original0x40251fd5
pc40251fd7:
bne a5, a2, pc40251fcd # original0x40251fd7
pc40251fda:
addi.n a7, a7, 4 # original0x40251fda
pc40251fdc:
addi.n a8, a8, 2 # original0x40251fdc
pc40251fde:
beq a9, a7, pc40252018 # original0x40251fde
pc40251fe1:
l32i.n a2, a7, 0 # original0x40251fe1
pc40251fe3:
mov.n a3, a8 # original0x40251fe3
pc40251fe5:
mull a2, a12, a2 # original0x40251fe5
pc40251fe8:
add.n a5, a12, a2 # original0x40251fe8
pc40251fea:
slli a5, a5, 1 # original0x40251fea
pc40251fed:
slli a2, a2, 1 # original0x40251fed
pc40251ff0:
add.n a2, a15, a2 # original0x40251ff0
pc40251ff2:
add.n a5, a15, a5 # original0x40251ff2
pc40251ff4:
j pc40251fcd # original0x40251ff4
pc40251ff8:
l16si a4, a2, 0 # original0x40251ff8
pc40251ffb:
addi.n a2, a2, 2 # original0x40251ffb
pc40251ffd:
s16i a4, a3, 0 # original0x40251ffd
pc40252000:
add.n a3, a3, a6 # original0x40252000
pc40252002:
bne a5, a2, pc40251ff8 # original0x40252002
pc40252005:
addi.n a7, a7, 2 # original0x40252005
pc40252007:
sub a5, a8, a11 # original0x40252007
pc4025200a:
beq a9, a7, pc40252018 # original0x4025200a
pc4025200d:
add.n a8, a10, a5 # original0x4025200d
pc4025200f:
mov.n a3, a7 # original0x4025200f
pc40252011:
mov.n a2, a8 # original0x40252011
pc40252013:
j pc40251ff8 # original0x40252013
pc40252018:
l32i a4, a1, 140 # original0x40252018
pc4025201b:
l32i a3, a1, 124 # original0x4025201b
pc4025201e:
movi a5, 2 # original0x4025201e
pc40252021:
or a2, a15, a15 # original0x40252021
pc40252024:
call0 fixed_402429b0 # original0x40252024
pc40252027:
l32i a2, a1, 92 # original0x40252027
pc4025202a:
l32i a3, a1, 96 # original0x4025202a
pc4025202d:
call0 fixed_402428d8 # original0x4025202d
pc40252030:
l32i.n a10, a1, 36 # original0x40252030
pc40252032:
s32i a10, a1, 132 # original0x40252032
pc40252035:
j pc402520bd # original0x40252035
pc40252038:
s32i a15, a1, 140 # original0x40252038
pc4025203b:
mov.n a15, a2 # original0x4025203b
pc4025203d:
l32i a11, a1, 120 # original0x4025203d
pc40252040:
srai a13, a13, 1 # original0x40252040
pc40252043:
ssr a13 # original0x40252043
pc40252046:
srl a2, a11 # original0x40252046
pc40252049:
or a11, a11, a2 # original0x40252049
pc4025204c:
slli a14, a14, 1 # original0x4025204c
pc4025204f:
s32i a11, a1, 120 # original0x4025204f
pc40252052:
srai a10, a14, 1 # original0x40252052
pc40252055:
blti a13, 1, pc402520a9 # original0x40252055
pc40252058:
blti a10, 1, pc402520a9 # original0x40252058
pc4025205b:
l32i a3, a1, 140 # original0x4025205b
pc4025205e:
slli a11, a13, 1 # original0x4025205e
pc40252061:
add.n a12, a11, a3 # original0x40252061
pc40252063:
slli a9, a13, 2 # original0x40252063
pc40252066:
j pc4025209d # original0x40252066
pc40252069:
l16si a7, a4, 0 # original0x40252069
pc4025206c:
l16si a2, a5, 0 # original0x4025206c
pc4025206f:
l32r a11, fixed_4024f0d8 # original0x4025206f
pc40252072:
mull a7, a7, a15 # original0x40252072
pc40252075:
mull a8, a2, a11 # original0x40252075
pc40252078:
addmi a2, a7, 0x4000 # original0x40252078
pc4025207b:
add.n a7, a2, a8 # original0x4025207b
pc4025207d:
srai a7, a7, 15 # original0x4025207d
pc40252080:
sub a2, a2, a8 # original0x40252080
pc40252083:
s16i a7, a4, 0 # original0x40252083
pc40252086:
srai a2, a2, 15 # original0x40252086
pc40252089:
s16i a2, a5, 0 # original0x40252089
pc4025208c:
addi.n a6, a6, 1 # original0x4025208c
pc4025208e:
add.n a4, a4, a9 # original0x4025208e
pc40252090:
add.n a5, a5, a9 # original0x40252090
pc40252092:
bne a10, a6, pc40252069 # original0x40252092
pc40252095:
addi.n a3, a3, 2 # original0x40252095
pc40252097:
l32i a11, a1, 148 # original0x40252097
pc4025209a:
beq a12, a3, pc402520a9 # original0x4025209a
pc4025209d:
add.n a5, a11, a3 # original0x4025209d
pc4025209f:
mov.n a4, a3 # original0x4025209f
pc402520a1:
movi.n a6, 0 # original0x402520a1
pc402520a3:
s32i a11, a1, 148 # original0x402520a3
pc402520a6:
j pc40252069 # original0x402520a6
pc402520a9:
l32i a12, a1, 124 # original0x402520a9
pc402520ac:
l32i a8, a1, 152 # original0x402520ac
pc402520af:
addi.n a12, a12, 1 # original0x402520af
pc402520b1:
s32i a12, a1, 124 # original0x402520b1
pc402520b4:
bne a12, a8, pc4025203d # original0x402520b4
pc402520b7:
l32i a15, a1, 140 # original0x402520b7
pc402520ba:
j pc402520ce # original0x402520ba
pc402520bd:
movi.n a9, 0 # original0x402520bd
pc402520bf:
l32i a10, a1, 152 # original0x402520bf
pc402520c2:
s32i a9, a1, 124 # original0x402520c2
pc402520c5:
l32r a2, fixed_4024f0d8 # original0x402520c5
pc402520c8:
blti a10, 1, pc402520ce # original0x402520c8
pc402520cb:
j pc40252038 # original0x402520cb
pc402520ce:
l32i a11, a1, 112 # original0x402520ce
pc402520d1:
beqz a11, pc40252175 # original0x402520d1
pc402520d4:
l32r a12, fixed_402507bc # original0x402520d4
pc402520d7:
s32i a13, a1, 124 # original0x402520d7
pc402520da:
l32r a14, fixed_4024f0d8 # original0x402520da
pc402520dd:
l32i a13, a1, 120 # original0x402520dd
pc402520e0:
s32i a12, a1, 148 # original0x402520e0
pc402520e3:
movi.n a9, 0 # original0x402520e3
pc402520e5:
l32i a2, a1, 148 # original0x402520e5
pc402520e8:
l32i a8, a1, 128 # original0x402520e8
pc402520eb:
movi.n a10, 1 # original0x402520eb
pc402520ed:
add.n a13, a2, a13 # original0x402520ed
pc402520ef:
ssr a9 # original0x402520ef
pc402520f2:
sra a11, a8 # original0x402520f2
pc402520f5:
ssl a9 # original0x402520f5
pc402520f8:
sll a12, a10 # original0x402520f8
pc402520fb:
l8ui a13, a13, 0 # original0x402520fb
pc402520fe:
ssr a10 # original0x402520fe
pc40252101:
sra a11, a11 # original0x40252101
pc40252104:
blt a12, a10, pc40252164 # original0x40252104
pc40252107:
movi.n a5, 0 # original0x40252107
pc40252109:
bge a11, a10, pc4025215c # original0x40252109
pc4025210c:
j pc40252164 # original0x4025210c
pc40252110:
ssl a9 # original0x40252110
pc40252113:
sll a2, a3 # original0x40252113
pc40252116:
slli a2, a2, 1 # original0x40252116
pc40252119:
ssl a9 # original0x40252119
pc4025211c:
sll a7, a4 # original0x4025211c
pc4025211f:
add.n a2, a2, a5 # original0x4025211f
pc40252121:
slli a2, a2, 1 # original0x40252121
pc40252124:
add.n a7, a7, a5 # original0x40252124
pc40252126:
add.n a6, a15, a2 # original0x40252126
pc40252128:
slli a7, a7, 1 # original0x40252128
pc4025212b:
l16ui a8, a6, 0 # original0x4025212b
pc4025212e:
add.n a7, a15, a7 # original0x4025212e
pc40252130:
l16ui a10, a7, 0 # original0x40252130
pc40252133:
l32r a2, fixed_4024f0d8 # original0x40252133
pc40252136:
mul16s a8, a8, a14 # original0x40252136
pc40252139:
mul16s a10, a10, a2 # original0x40252139
pc4025213c:
addmi a2, a8, 0x4000 # original0x4025213c
pc4025213f:
add.n a8, a2, a10 # original0x4025213f
pc40252141:
srai a8, a8, 15 # original0x40252141
pc40252144:
sub a2, a2, a10 # original0x40252144
pc40252147:
s16i a8, a6, 0 # original0x40252147
pc4025214a:
srai a2, a2, 15 # original0x4025214a
pc4025214d:
s16i a2, a7, 0 # original0x4025214d
pc40252150:
addi.n a3, a3, 1 # original0x40252150
pc40252152:
addi.n a4, a4, 2 # original0x40252152
pc40252154:
bne a11, a3, pc40252110 # original0x40252154
pc40252157:
addi.n a5, a5, 1 # original0x40252157
pc40252159:
beq a12, a5, pc40252164 # original0x40252159
pc4025215c:
movi.n a4, 1 # original0x4025215c
pc4025215e:
movi.n a3, 0 # original0x4025215e
pc40252160:
j pc40252110 # original0x40252160
pc40252164:
l32i a8, a1, 112 # original0x40252164
pc40252167:
addi.n a9, a9, 1 # original0x40252167
pc40252169:
beq a8, a9, pc4025216f # original0x40252169
pc4025216c:
j pc402520e5 # original0x4025216c
pc4025216f:
s32i a13, a1, 120 # original0x4025216f
pc40252172:
l32i a13, a1, 124 # original0x40252172
pc40252175:
l32i a9, a1, 112 # original0x40252175
pc40252178:
movi.n a10, 1 # original0x40252178
pc4025217a:
ssl a9 # original0x4025217a
pc4025217d:
sll a12, a13 # original0x4025217d
pc40252180:
ssl a12 # original0x40252180
pc40252183:
sll a12, a10 # original0x40252183
pc40252186:
l32i a11, a1, 120 # original0x40252186
pc40252189:
addi.n a12, a12, -1 # original0x40252189
pc4025218b:
l32i a14, a1, 236 # original0x4025218b
pc4025218e:
and a12, a12, a11 # original0x4025218e
pc40252191:
or a12, a12, a14 # original0x40252191
pc40252194:
j pc40252a20 # original0x40252194
pc40252197:
l32i.n a8, a1, 56 # original0x40252197
pc40252199:
l32i a2, a1, 128 # original0x40252199
pc4025219c:
or a3, a9, a9 # original0x4025219c
pc4025219f:
s32i a8, a1, 112 # original0x4025219f
pc402521a2:
l32r a0, fixed_40250738 # original0x402521a2
pc402521a5:
callx0 a0 # original0x402521a5
pc402521a8:
l32i.n a9, a1, 32 # original0x402521a8
pc402521aa:
l32i a10, a1, 112 # original0x402521aa
pc402521ad:
s32i a9, a1, 132 # original0x402521ad
pc402521b0:
mov.n a14, a2 # original0x402521b0
pc402521b2:
bgei a10, 1, pc402521b8 # original0x402521b2
pc402521b5:
j pc40252284 # original0x402521b5
pc402521b8:
l32r a11, fixed_402507ac # original0x402521b8
pc402521bb:
movi.n a9, 0 # original0x402521bb
pc402521bd:
s32i a11, a1, 120 # original0x402521bd
pc402521c0:
s32i a2, a1, 148 # original0x402521c0
pc402521c3:
mov.n a14, a11 # original0x402521c3
pc402521c5:
l32i a2, a1, 132 # original0x402521c5
pc402521c8:
# decoder-unreachable/check: beqz a2, 40252248 <quant_all_bands+6768>
pc402521cb:
# decoder-unreachable/check: l32i a8, a1, 128
pc402521ce:
# decoder-unreachable/check: movi a10, 1
pc402521d0:
# decoder-unreachable/check: ssr a9
pc402521d3:
# decoder-unreachable/check: sra a11, a8
pc402521d6:
# decoder-unreachable/check: ssl a9
pc402521d9:
# decoder-unreachable/check: sll a13, a10
pc402521dc:
# decoder-unreachable/check: ssr a10
pc402521df:
# decoder-unreachable/check: sra a11, a11
pc402521e2:
# decoder-unreachable/check: blt a13, a10, 40252248 <quant_all_bands+6768>
pc402521e5:
# decoder-unreachable/check: movi a5, 0
pc402521e7:
# decoder-unreachable/check: bge a11, a10, 4025223c <quant_all_bands+6756>
pc402521ea:
# decoder-unreachable/check: j 40252248 <quant_all_bands+6768>
pc402521ed:
# decoder-unreachable/check: ssl a9
pc402521f0:
# decoder-unreachable/check: sll a2, a3
pc402521f3:
# decoder-unreachable/check: slli a2, a2, 1
pc402521f6:
# decoder-unreachable/check: ssl a9
pc402521f9:
# decoder-unreachable/check: sll a7, a4
pc402521fc:
# decoder-unreachable/check: add a2, a2, a5
pc402521fe:
# decoder-unreachable/check: slli a2, a2, 1
pc40252201:
# decoder-unreachable/check: add a7, a7, a5
pc40252203:
# decoder-unreachable/check: add a6, a15, a2
pc40252205:
# decoder-unreachable/check: slli a7, a7, 1
pc40252208:
# decoder-unreachable/check: l16ui a8, a6, 0
pc4025220b:
# decoder-unreachable/check: add a7, a15, a7
pc4025220d:
# decoder-unreachable/check: l32r a12, 4024f0d8 <anti_collapse+968>
pc40252210:
# decoder-unreachable/check: l16ui a10, a7, 0
pc40252213:
# decoder-unreachable/check: mul16s a8, a8, a12
pc40252216:
# decoder-unreachable/check: mul16s a10, a10, a12
pc40252219:
# decoder-unreachable/check: addmi a2, a8, 16384
pc4025221c:
# decoder-unreachable/check: add a8, a2, a10
pc4025221e:
# decoder-unreachable/check: srai a8, a8, 15
pc40252221:
# decoder-unreachable/check: sub a2, a2, a10
pc40252224:
# decoder-unreachable/check: s16i a8, a6, 0
pc40252227:
# decoder-unreachable/check: srai a2, a2, 15
pc4025222a:
# decoder-unreachable/check: s16i a2, a7, 0
pc4025222d:
# decoder-unreachable/check: addi a3, a3, 1
pc4025222f:
# decoder-unreachable/check: addi a4, a4, 2
pc40252231:
# decoder-unreachable/check: bne a11, a3, 402521ed <quant_all_bands+6677>
pc40252234:
# decoder-unreachable/check: addi a5, a5, 1
pc40252236:
# decoder-unreachable/check: l32i a12, a1, 120
pc40252239:
# decoder-unreachable/check: beq a13, a5, 40252248 <quant_all_bands+6768>
pc4025223c:
# decoder-unreachable/check: movi a4, 1
pc4025223e:
# decoder-unreachable/check: movi a3, 0
pc40252240:
# decoder-unreachable/check: s32i a12, a1, 120
pc40252243:
# decoder-unreachable/check: j 402521ed <quant_all_bands+6677>
pc40252248:
srai a2, a12, 4 # original0x40252248
pc4025224b:
add.n a2, a14, a2 # original0x4025224b
pc4025224d:
extui a12, a12, 0, 4 # original0x4025224d
pc40252250:
add.n a12, a14, a12 # original0x40252250
pc40252252:
l8ui a2, a2, 0 # original0x40252252
pc40252255:
l8ui a12, a12, 0 # original0x40252255
pc40252258:
l32i a8, a1, 112 # original0x40252258
pc4025225b:
slli a2, a2, 2 # original0x4025225b
pc4025225e:
addi.n a9, a9, 1 # original0x4025225e
pc40252260:
or a12, a12, a2 # original0x40252260
pc40252263:
beq a8, a9, pc40252269 # original0x40252263
pc40252266:
j pc402521c5 # original0x40252266
pc40252269:
l32i a14, a1, 148 # original0x40252269
pc4025226c:
l32i a11, a1, 180 # original0x4025226c
pc4025226f:
movi.n a9, 0 # original0x4025226f
pc40252271:
ssr a8 # original0x40252271
pc40252274:
sra a13, a11 # original0x40252274
pc40252277:
ssl a8 # original0x40252277
pc4025227a:
sll a14, a14 # original0x4025227a
pc4025227d:
s32i a9, a1, 188 # original0x4025227d
pc40252280:
j pc4025232e # original0x40252280
pc40252284:
l32i a13, a1, 180 # original0x40252284
pc40252287:
bgez a10, pc40252326 # original0x40252287
pc4025228a:
bbci a2, 0, pc40252290 # original0x4025228a
pc4025228d:
j pc40252326 # original0x4025228d
pc40252290:
movi a10, 0 # original0x40252290
pc40252293:
s32i a10, a1, 188 # original0x40252293
pc40252296:
s32i a15, a1, 120 # original0x40252296
pc40252299:
or a11, a10, a10 # original0x40252299
pc4025229c:
l32i a2, a1, 132 # original0x4025229c
pc4025229f:
srai a14, a14, 1 # original0x4025229f
pc402522a2:
slli a10, a13, 1 # original0x402522a2
pc402522a5:
# decoder-unreachable/check: beqz a2, 402522f9 <quant_all_bands+6945>
pc402522a8:
# decoder-unreachable/check: blti a13, 1, 402522f9 <quant_all_bands+6945>
pc402522ab:
# decoder-unreachable/check: blti a14, 1, 402522f9 <quant_all_bands+6945>
pc402522ae:
# decoder-unreachable/check: l32i a3, a1, 120
pc402522b1:
# decoder-unreachable/check: slli a9, a13, 2
pc402522b4:
# decoder-unreachable/check: add a15, a3, a10
pc402522b6:
# decoder-unreachable/check: j 402522ed <quant_all_bands+6933>
pc402522b9:
# decoder-unreachable/check: l16ui a7, a4, 0
pc402522bc:
# decoder-unreachable/check: l32r a10, 4024f0d8 <anti_collapse+968>
pc402522bf:
# decoder-unreachable/check: l16ui a8, a5, 0
pc402522c2:
# decoder-unreachable/check: mul16s a7, a7, a10
pc402522c5:
# decoder-unreachable/check: mul16s a8, a8, a10
pc402522c8:
# decoder-unreachable/check: addmi a2, a7, 16384
pc402522cb:
# decoder-unreachable/check: add a7, a2, a8
pc402522cd:
# decoder-unreachable/check: srai a7, a7, 15
pc402522d0:
# decoder-unreachable/check: sub a2, a2, a8
pc402522d3:
# decoder-unreachable/check: s16i a7, a4, 0
pc402522d6:
# decoder-unreachable/check: srai a2, a2, 15
pc402522d9:
# decoder-unreachable/check: s16i a2, a5, 0
pc402522dc:
# decoder-unreachable/check: addi a6, a6, 1
pc402522de:
# decoder-unreachable/check: add a4, a4, a9
pc402522e0:
# decoder-unreachable/check: add a5, a5, a9
pc402522e2:
# decoder-unreachable/check: bne a6, a14, 402522b9 <quant_all_bands+6881>
pc402522e5:
# decoder-unreachable/check: addi a3, a3, 2
pc402522e7:
# decoder-unreachable/check: l32i a10, a1, 148
pc402522ea:
# decoder-unreachable/check: beq a15, a3, 402522f9 <quant_all_bands+6945>
pc402522ed:
# decoder-unreachable/check: add a5, a10, a3
pc402522ef:
# decoder-unreachable/check: mov a4, a3
pc402522f1:
# decoder-unreachable/check: movi a6, 0
pc402522f3:
# decoder-unreachable/check: s32i a10, a1, 148
pc402522f6:
# decoder-unreachable/check: j 402522b9 <quant_all_bands+6881>
pc402522f9:
l32i a8, a1, 112 # original0x402522f9
pc402522fc:
addi.n a11, a11, 1 # original0x402522fc
pc402522fe:
add.n a2, a11, a8 # original0x402522fe
pc40252300:
movi.n a9, -1 # original0x40252300
pc40252302:
ssl a13 # original0x40252302
pc40252305:
sll a13, a12 # original0x40252305
pc40252308:
extui a2, a2, 31, 1 # original0x40252308
pc4025230b:
xor a3, a9, a14 # original0x4025230b
pc4025230e:
or a12, a12, a13 # original0x4025230e
pc40252311:
mov.n a13, a10 # original0x40252311
pc40252313:
bany a3, a2, pc4025229c # original0x40252313
pc40252316:
movi.n a10, 0 # original0x40252316
pc40252318:
l32i a15, a1, 120 # original0x40252318
pc4025231b:
s32i a11, a1, 188 # original0x4025231b
pc4025231e:
s32i a10, a1, 112 # original0x4025231e
pc40252321:
j pc4025232e # original0x40252321
pc40252326:
movi.n a11, 0 # original0x40252326
pc40252328:
s32i a11, a1, 112 # original0x40252328
pc4025232b:
s32i a11, a1, 188 # original0x4025232b
pc4025232e:
bgei a13, 2, pc40252334 # original0x4025232e
pc40252331:
j pc4025291c # original0x40252331
pc40252334:
l32i a9, a1, 132 # original0x40252334
pc40252337:
j pc402528ea # original0x40252337
pc4025233a:
# decoder-unreachable/check: l32i a10, a1, 112
pc4025233d:
# decoder-unreachable/check: l32i a5, a1, 312
pc40252340:
# decoder-unreachable/check: ssl a10
pc40252343:
# decoder-unreachable/check: sll a4, a13
pc40252346:
# decoder-unreachable/check: ssr a10
pc40252349:
# decoder-unreachable/check: sra a3, a14
pc4025234c:
# decoder-unreachable/check: mov a2, a15
pc4025234e:
# decoder-unreachable/check: call0 4024d92c <deinterleave_hadamard>
pc40252351:
# decoder-unreachable/check: j 402528ea <quant_all_bands+8466>
pc40252357:
l32i a11, a1, 112 # original0x40252357
pc4025235a:
ssl a11 # original0x4025235a
pc4025235d:
sll a6, a13 # original0x4025235d
pc40252360:
ssr a11 # original0x40252360
pc40252363:
sra a12, a14 # original0x40252363
pc40252366:
mull a8, a12, a6 # original0x40252366
pc40252369:
s32i a6, a1, 0x158 # original0x40252369
pc4025236c:
s32i a8, a1, 216 # original0x4025236c
pc4025236f:
call0 fixed_402428c4 # original0x4025236f
pc40252372:
s32i a2, a1, 92 # original0x40252372
pc40252375:
l32i a2, a1, 216 # original0x40252375
pc40252378:
s32i a3, a1, 96 # original0x40252378
pc4025237b:
movi a4, 0 # original0x4025237b
pc4025237e:
movi a3, 2 # original0x4025237e
pc40252381:
call0 fixed_402428ec # original0x40252381
pc40252384:
l32i a9, a1, 0x138 # original0x40252384
pc40252387:
s32i a2, a1, 148 # original0x40252387
pc4025238a:
l32i a6, a1, 0x158 # original0x4025238a
pc4025238d:
bnez.n a9, pc402523b5 # original0x4025238d
pc4025238f:
bgei a6, 1, pc40252395 # original0x4025238f
pc40252392:
j pc40252422 # original0x40252392
pc40252395:
bgei a12, 1, pc4025239b # original0x40252395
pc40252398:
j pc40252422 # original0x40252398
pc4025239b:
slli a5, a12, 1 # original0x4025239b
pc4025239e:
mov.n a10, a5 # original0x4025239e
pc402523a0:
slli a6, a6, 1 # original0x402523a0
pc402523a3:
slli a11, a12, 2 # original0x402523a3
pc402523a6:
mov.n a7, a2 # original0x402523a6
pc402523a8:
add.n a5, a15, a5 # original0x402523a8
pc402523aa:
add.n a9, a6, a2 # original0x402523aa
pc402523ac:
neg a10, a10 # original0x402523ac
pc402523af:
neg a11, a11 # original0x402523af
pc402523b2:
j pc40252419 # original0x402523b2
pc402523b5:
l32r a2, fixed_4024f14c # original0x402523b5
pc402523b8:
add.n a7, a6, a2 # original0x402523b8
pc402523ba:
blti a6, 1, pc40252422 # original0x402523ba
pc402523bd:
blti a12, 1, pc40252422 # original0x402523bd
pc402523c0:
l32r a3, fixed_402507b8 # original0x402523c0
pc402523c3:
slli a9, a6, 3 # original0x402523c3
pc402523c6:
slli a7, a7, 2 # original0x402523c6
pc402523c9:
addi a2, a3, -8 # original0x402523c9
pc402523cc:
add.n a7, a7, a3 # original0x402523cc
pc402523ce:
l32i a8, a1, 148 # original0x402523ce
pc402523d1:
add.n a9, a2, a9 # original0x402523d1
pc402523d3:
slli a6, a6, 1 # original0x402523d3
pc402523d6:
j pc402523ed # original0x402523d6
pc402523d9:
l16si a4, a2, 0 # original0x402523d9
pc402523dc:
addi.n a2, a2, 2 # original0x402523dc
pc402523de:
s16i a4, a3, 0 # original0x402523de
pc402523e1:
add.n a3, a3, a6 # original0x402523e1
pc402523e3:
bne a5, a2, pc402523d9 # original0x402523e3
pc402523e6:
addi.n a7, a7, 4 # original0x402523e6
pc402523e8:
addi.n a8, a8, 2 # original0x402523e8
pc402523ea:
beq a9, a7, pc40252422 # original0x402523ea
pc402523ed:
l32i.n a2, a7, 0 # original0x402523ed
pc402523ef:
mov.n a3, a8 # original0x402523ef
pc402523f1:
mull a2, a12, a2 # original0x402523f1
pc402523f4:
add.n a5, a12, a2 # original0x402523f4
pc402523f6:
slli a5, a5, 1 # original0x402523f6
pc402523f9:
slli a2, a2, 1 # original0x402523f9
pc402523fc:
add.n a2, a15, a2 # original0x402523fc
pc402523fe:
add.n a5, a15, a5 # original0x402523fe
pc40252400:
j pc402523d9 # original0x40252400
pc40252404:
l16si a4, a2, 0 # original0x40252404
pc40252407:
addi.n a2, a2, 2 # original0x40252407
pc40252409:
s16i a4, a3, 0 # original0x40252409
pc4025240c:
add.n a3, a3, a6 # original0x4025240c
pc4025240e:
bne a5, a2, pc40252404 # original0x4025240e
pc40252411:
addi.n a7, a7, 2 # original0x40252411
pc40252413:
sub a5, a8, a11 # original0x40252413
pc40252416:
beq a9, a7, pc40252422 # original0x40252416
pc40252419:
add.n a8, a10, a5 # original0x40252419
pc4025241b:
mov.n a3, a7 # original0x4025241b
pc4025241d:
mov.n a2, a8 # original0x4025241d
pc4025241f:
j pc40252404 # original0x4025241f
pc40252422:
l32i a3, a1, 148 # original0x40252422
pc40252425:
l32i a4, a1, 216 # original0x40252425
pc40252428:
mov.n a2, a15 # original0x40252428
pc4025242a:
movi.n a5, 2 # original0x4025242a
pc4025242c:
call0 fixed_402429b0 # original0x4025242c
pc4025242f:
l32i a2, a1, 92 # original0x4025242f
pc40252432:
l32i a3, a1, 96 # original0x40252432
pc40252435:
call0 fixed_402428d8 # original0x40252435
pc40252438:
j pc402524c1 # original0x40252438
pc4025243c:
s32i a15, a1, 216 # original0x4025243c
pc4025243f:
mov.n a15, a2 # original0x4025243f
pc40252441:
l32i a10, a1, 120 # original0x40252441
pc40252444:
srai a13, a13, 1 # original0x40252444
pc40252447:
ssr a13 # original0x40252447
pc4025244a:
srl a2, a10 # original0x4025244a
pc4025244d:
or a10, a10, a2 # original0x4025244d
pc40252450:
slli a14, a14, 1 # original0x40252450
pc40252453:
s32i a10, a1, 120 # original0x40252453
pc40252456:
srai a10, a14, 1 # original0x40252456
pc40252459:
blti a13, 1, pc402524ad # original0x40252459
pc4025245c:
blti a10, 1, pc402524ad # original0x4025245c
pc4025245f:
l32i a3, a1, 216 # original0x4025245f
pc40252462:
slli a11, a13, 1 # original0x40252462
pc40252465:
add.n a12, a11, a3 # original0x40252465
pc40252467:
slli a9, a13, 2 # original0x40252467
pc4025246a:
j pc402524a1 # original0x4025246a
pc4025246d:
l16si a7, a4, 0 # original0x4025246d
pc40252470:
l16si a2, a5, 0 # original0x40252470
pc40252473:
l32r a11, fixed_4024f0d8 # original0x40252473
pc40252476:
mull a7, a7, a15 # original0x40252476
pc40252479:
mull a8, a2, a11 # original0x40252479
pc4025247c:
addmi a2, a7, 0x4000 # original0x4025247c
pc4025247f:
add.n a7, a2, a8 # original0x4025247f
pc40252481:
srai a7, a7, 15 # original0x40252481
pc40252484:
sub a2, a2, a8 # original0x40252484
pc40252487:
s16i a7, a4, 0 # original0x40252487
pc4025248a:
srai a2, a2, 15 # original0x4025248a
pc4025248d:
s16i a2, a5, 0 # original0x4025248d
pc40252490:
addi.n a6, a6, 1 # original0x40252490
pc40252492:
add.n a4, a4, a9 # original0x40252492
pc40252494:
add.n a5, a5, a9 # original0x40252494
pc40252496:
bne a10, a6, pc4025246d # original0x40252496
pc40252499:
addi.n a3, a3, 2 # original0x40252499
pc4025249b:
l32i a11, a1, 0x138 # original0x4025249b
pc4025249e:
beq a12, a3, pc402524ad # original0x4025249e
pc402524a1:
add.n a5, a11, a3 # original0x402524a1
pc402524a3:
mov.n a4, a3 # original0x402524a3
pc402524a5:
movi.n a6, 0 # original0x402524a5
pc402524a7:
s32i a11, a1, 0x138 # original0x402524a7
pc402524aa:
j pc4025246d # original0x402524aa
pc402524ad:
l32i a12, a1, 148 # original0x402524ad
pc402524b0:
l32i a8, a1, 188 # original0x402524b0
pc402524b3:
addi.n a12, a12, 1 # original0x402524b3
pc402524b5:
s32i a12, a1, 148 # original0x402524b5
pc402524b8:
bne a8, a12, pc40252441 # original0x402524b8
pc402524bb:
l32i a15, a1, 216 # original0x402524bb
pc402524be:
j pc402524d2 # original0x402524be
pc402524c1:
movi.n a9, 0 # original0x402524c1
pc402524c3:
l32i a10, a1, 188 # original0x402524c3
pc402524c6:
s32i a9, a1, 148 # original0x402524c6
pc402524c9:
l32r a2, fixed_4024f0d8 # original0x402524c9
pc402524cc:
blti a10, 1, pc402524d2 # original0x402524cc
pc402524cf:
j pc4025243c # original0x402524cf
pc402524d2:
l32i a11, a1, 112 # original0x402524d2
pc402524d5:
beqz a11, pc40252579 # original0x402524d5
pc402524d8:
l32r a12, fixed_402507bc # original0x402524d8
pc402524db:
s32i a13, a1, 188 # original0x402524db
pc402524de:
l32r a14, fixed_4024f0d8 # original0x402524de
pc402524e1:
l32i a13, a1, 120 # original0x402524e1
pc402524e4:
s32i a12, a1, 148 # original0x402524e4
pc402524e7:
movi.n a9, 0 # original0x402524e7
pc402524e9:
l32i a2, a1, 148 # original0x402524e9
pc402524ec:
l32i a8, a1, 128 # original0x402524ec
pc402524ef:
movi.n a10, 1 # original0x402524ef
pc402524f1:
add.n a13, a2, a13 # original0x402524f1
pc402524f3:
ssr a9 # original0x402524f3
pc402524f6:
sra a11, a8 # original0x402524f6
pc402524f9:
ssl a9 # original0x402524f9
pc402524fc:
sll a12, a10 # original0x402524fc
pc402524ff:
l8ui a13, a13, 0 # original0x402524ff
pc40252502:
ssr a10 # original0x40252502
pc40252505:
sra a11, a11 # original0x40252505
pc40252508:
blt a12, a10, pc40252568 # original0x40252508
pc4025250b:
movi.n a5, 0 # original0x4025250b
pc4025250d:
bge a11, a10, pc40252560 # original0x4025250d
pc40252510:
j pc40252568 # original0x40252510
pc40252514:
ssl a9 # original0x40252514
pc40252517:
sll a2, a3 # original0x40252517
pc4025251a:
slli a2, a2, 1 # original0x4025251a
pc4025251d:
ssl a9 # original0x4025251d
pc40252520:
sll a7, a4 # original0x40252520
pc40252523:
add.n a2, a2, a5 # original0x40252523
pc40252525:
slli a2, a2, 1 # original0x40252525
pc40252528:
add.n a7, a7, a5 # original0x40252528
pc4025252a:
add.n a6, a15, a2 # original0x4025252a
pc4025252c:
slli a7, a7, 1 # original0x4025252c
pc4025252f:
l16ui a8, a6, 0 # original0x4025252f
pc40252532:
add.n a7, a15, a7 # original0x40252532
pc40252534:
l16ui a10, a7, 0 # original0x40252534
pc40252537:
l32r a2, fixed_4024f0d8 # original0x40252537
pc4025253a:
mul16s a8, a8, a14 # original0x4025253a
pc4025253d:
mul16s a10, a10, a2 # original0x4025253d
pc40252540:
addmi a2, a8, 0x4000 # original0x40252540
pc40252543:
add.n a8, a2, a10 # original0x40252543
pc40252545:
srai a8, a8, 15 # original0x40252545
pc40252548:
sub a2, a2, a10 # original0x40252548
pc4025254b:
s16i a8, a6, 0 # original0x4025254b
pc4025254e:
srai a2, a2, 15 # original0x4025254e
pc40252551:
s16i a2, a7, 0 # original0x40252551
pc40252554:
addi.n a3, a3, 1 # original0x40252554
pc40252556:
addi.n a4, a4, 2 # original0x40252556
pc40252558:
bne a11, a3, pc40252514 # original0x40252558
pc4025255b:
addi.n a5, a5, 1 # original0x4025255b
pc4025255d:
beq a12, a5, pc40252568 # original0x4025255d
pc40252560:
movi.n a4, 1 # original0x40252560
pc40252562:
movi.n a3, 0 # original0x40252562
pc40252564:
j pc40252514 # original0x40252564
pc40252568:
l32i a8, a1, 112 # original0x40252568
pc4025256b:
addi.n a9, a9, 1 # original0x4025256b
pc4025256d:
beq a8, a9, pc40252573 # original0x4025256d
pc40252570:
j pc402524e9 # original0x40252570
pc40252573:
s32i a13, a1, 120 # original0x40252573
pc40252576:
l32i a13, a1, 188 # original0x40252576
pc40252579:
l32i a9, a1, 112 # original0x40252579
pc4025257c:
movi.n a10, 1 # original0x4025257c
pc4025257e:
ssl a9 # original0x4025257e
pc40252581:
sll a2, a13 # original0x40252581
pc40252584:
l32i a11, a1, 120 # original0x40252584
pc40252587:
ssl a2 # original0x40252587
pc4025258a:
sll a2, a10 # original0x4025258a
pc4025258d:
addi.n a2, a2, -1 # original0x4025258d
pc4025258f:
and a11, a11, a2 # original0x4025258f
pc40252592:
s32i a11, a1, 120 # original0x40252592
pc40252595:
l32i a3, a1, 64 # original0x40252595
pc40252598:
l32i a12, a1, 252 # original0x40252598
pc4025259b:
l32i a14, a1, 228 # original0x4025259b
pc4025259e:
sub a3, a3, a12 # original0x4025259e
pc402525a1:
l32i a8, a1, 0x100 # original0x402525a1
pc402525a4:
add.n a3, a3, a14 # original0x402525a4
pc402525a6:
movi.n a2, 24 # original0x402525a6
pc402525a8:
add.n a3, a3, a8 # original0x402525a8
pc402525aa:
bge a2, a3, pc402525c0 # original0x402525aa
pc402525ad:
l32i a9, a1, 196 # original0x402525ad
pc402525b0:
addmi a2, a9, 0xffffc000 # original0x402525b0
pc402525b3:
beqz.n a2, pc402525c0 # original0x402525b3
pc402525b5:
l32i a10, a1, 124 # original0x402525b5
pc402525b8:
addi a2, a10, -24 # original0x402525b8
pc402525bb:
add.n a2, a3, a2 # original0x402525bb
pc402525bd:
s32i a2, a1, 124 # original0x402525bd
pc402525c0:
l32i a11, a1, 0x114 # original0x402525c0
pc402525c3:
l32i a12, a1, 168 # original0x402525c3
pc402525c6:
l32i a14, a1, 140 # original0x402525c6
pc402525c9:
l32i a8, a1, 236 # original0x402525c9
pc402525cc:
l32i a9, a1, 0x1ac # original0x402525cc
pc402525cf:
l32i a7, a1, 152 # original0x402525cf
pc402525d2:
l32i a6, a1, 180 # original0x402525d2
pc402525d5:
l32i a5, a1, 124 # original0x402525d5
pc402525d8:
l32i a4, a1, 128 # original0x402525d8
pc402525db:
l32i a3, a1, 172 # original0x402525db
pc402525de:
l32i a2, a1, 132 # original0x402525de
pc402525e1:
s32i a11, a1, 16 # original0x402525e1
pc402525e4:
s32i a12, a1, 12 # original0x402525e4
pc402525e7:
s32i a14, a1, 8 # original0x402525e7
pc402525ea:
s32i.n a8, a1, 4 # original0x402525ea
pc402525ec:
s32i.n a9, a1, 0 # original0x402525ec
pc402525ee:
call0 fixed_4024e44c # original0x402525ee
pc402525f1:
l32i a10, a1, 120 # original0x402525f1
pc402525f4:
l32i.n a11, a1, 36 # original0x402525f4
pc402525f6:
or a12, a2, a10 # original0x402525f6
pc402525f9:
s32i a11, a1, 132 # original0x402525f9
pc402525fc:
j pc40252a20 # original0x402525fc
pc402525ff:
l32i a14, a1, 128 # original0x402525ff
pc40252602:
blti a14, 1, pc4025264e # original0x40252602
pc40252605:
slli a9, a14, 1 # original0x40252605
pc40252608:
movi.n a7, 0 # original0x40252608
pc4025260a:
l32i a5, a1, 172 # original0x4025260a
pc4025260d:
mov.n a2, a15 # original0x4025260d
pc4025260f:
add.n a9, a9, a15 # original0x4025260f
pc40252611:
or a6, a7, a7 # original0x40252611
pc40252614:
l16si a4, a2, 0 # original0x40252614
pc40252617:
l16ui a3, a5, 0 # original0x40252617
pc4025261a:
mull a8, a4, a4 # original0x4025261a
pc4025261d:
mul16s a3, a3, a4 # original0x4025261d
pc40252620:
addi.n a2, a2, 2 # original0x40252620
pc40252622:
add.n a6, a6, a3 # original0x40252622
pc40252624:
add.n a7, a7, a8 # original0x40252624
pc40252626:
addi.n a5, a5, 2 # original0x40252626
pc40252628:
bne a9, a2, pc40252614 # original0x40252628
pc4025262b:
l32i a8, a1, 0x110 # original0x4025262b
pc4025262e:
srai a3, a6, 16 # original0x4025262e
pc40252631:
extui a2, a6, 0, 16 # original0x40252631
pc40252634:
mull a3, a3, a8 # original0x40252634
pc40252637:
mull a2, a2, a8 # original0x40252637
pc4025263a:
slli a3, a3, 1 # original0x4025263a
pc4025263d:
srai a2, a2, 15 # original0x4025263d
pc40252640:
add.n a2, a3, a2 # original0x40252640
pc40252642:
slli a4, a2, 1 # original0x40252642
pc40252645:
neg a4, a4 # original0x40252645
pc40252648:
slli a2, a2, 1 # original0x40252648
pc4025264b:
j pc40252654 # original0x4025264b
pc4025264e:
movi.n a4, 0 # original0x4025264e
pc40252650:
mov.n a2, a4 # original0x40252650
pc40252652:
mov.n a7, a4 # original0x40252652
pc40252654:
l32i a9, a1, 0x13c # original0x40252654
pc40252657:
l32r a5, fixed_402507c0 # original0x40252657
pc4025265a:
srai a3, a9, 1 # original0x4025265a
pc4025265d:
mull a3, a3, a3 # original0x4025265d
pc40252660:
add.n a7, a3, a7 # original0x40252660
pc40252662:
add.n a6, a7, a2 # original0x40252662
pc40252664:
add.n a7, a7, a4 # original0x40252664
pc40252666:
bge a5, a6, pc402526bc # original0x40252666
pc40252669:
bge a5, a7, pc402526bc # original0x40252669
pc4025266c:
nsau a3, a7 # original0x4025266c
pc4025266f:
movi a2, 31 # original0x4025266f
pc40252672:
sub a3, a2, a3 # original0x40252672
pc40252675:
slli a3, a3, 16 # original0x40252675
pc40252678:
srai a3, a3, 17 # original0x40252678
pc4025267b:
nsau a13, a6 # original0x4025267b
pc4025267e:
sub a13, a2, a13 # original0x4025267e
pc40252681:
addi a2, a3, -7 # original0x40252681
pc40252684:
slli a2, a2, 1 # original0x40252684
pc40252687:
ssr a2 # original0x40252687
pc4025268a:
sra a2, a7 # original0x4025268a
pc4025268d:
slli a13, a13, 16 # original0x4025268d
pc40252690:
s32i a3, a1, 0x154 # original0x40252690
pc40252693:
s32i a6, a1, 0x158 # original0x40252693
pc40252696:
srai a13, a13, 17 # original0x40252696
pc40252699:
call0 fixed_40246e54 # original0x40252699
pc4025269c:
l32i a6, a1, 0x158 # original0x4025269c
pc4025269f:
mov.n a14, a2 # original0x4025269f
pc402526a1:
addi a2, a13, -7 # original0x402526a1
pc402526a4:
slli a2, a2, 1 # original0x402526a4
pc402526a7:
ssr a2 # original0x402526a7
pc402526aa:
sra a2, a6 # original0x402526aa
pc402526ad:
call0 fixed_40246e54 # original0x402526ad
pc402526b0:
l32i a10, a1, 128 # original0x402526b0
pc402526b3:
l32i a3, a1, 0x154 # original0x402526b3
pc402526b6:
bgei a10, 1, pc402526d5 # original0x402526b6
pc402526b9:
j pc40252766 # original0x402526b9
pc402526bc:
l32i a4, a1, 128 # original0x402526bc
pc402526bf:
l32i a3, a1, 172 # original0x402526bf
pc402526c2:
movi.n a5, 2 # original0x402526c2
pc402526c4:
mov.n a2, a15 # original0x402526c4
pc402526c6:
call0 fixed_402429b0 # original0x402526c6
pc402526c9:
l32i a11, a1, 240 # original0x402526c9
pc402526cc:
bnez a11, pc40252748 # original0x402526cc
pc402526cf:
j pc40252766 # original0x402526cf
pc402526d5:
mov.n a4, a10 # original0x402526d5
pc402526d7:
addi.n a7, a3, 1 # original0x402526d7
pc402526d9:
addi.n a11, a13, 1 # original0x402526d9
pc402526db:
movi.n a3, 1 # original0x402526db
pc402526dd:
l32i a13, a1, 172 # original0x402526dd
pc402526e0:
ssl a7 # original0x402526e0
pc402526e3:
sll a10, a3 # original0x402526e3
pc402526e6:
ssl a11 # original0x402526e6
pc402526e9:
sll a9, a3 # original0x402526e9
pc402526ec:
ssl a3 # original0x402526ec
pc402526ef:
sll a8, a4 # original0x402526ef
pc402526f2:
mov.n a5, a15 # original0x402526f2
pc402526f4:
s32i a15, a1, 112 # original0x402526f4
pc402526f7:
l32i a15, a1, 0x110 # original0x402526f7
pc402526fa:
ssr a3 # original0x402526fa
pc402526fd:
sra a10, a10 # original0x402526fd
pc40252700:
ssr a3 # original0x40252700
pc40252703:
sra a9, a9 # original0x40252703
pc40252706:
add.n a8, a13, a8 # original0x40252706
pc40252708:
l16si a3, a13, 0 # original0x40252708
pc4025270b:
l16si a6, a5, 0 # original0x4025270b
pc4025270e:
mull a3, a3, a15 # original0x4025270e
pc40252711:
addmi a3, a3, 0x4000 # original0x40252711
pc40252714:
slli a3, a3, 1 # original0x40252714
pc40252717:
srai a3, a3, 16 # original0x40252717
pc4025271a:
sub a4, a3, a6 # original0x4025271a
pc4025271d:
mul16s a4, a4, a14 # original0x4025271d
pc40252720:
add.n a3, a3, a6 # original0x40252720
pc40252722:
mul16s a3, a3, a2 # original0x40252722
pc40252725:
add.n a4, a4, a10 # original0x40252725
pc40252727:
ssr a7 # original0x40252727
pc4025272a:
sra a4, a4 # original0x4025272a
pc4025272d:
add.n a3, a3, a9 # original0x4025272d
pc4025272f:
s16i a4, a13, 0 # original0x4025272f
pc40252732:
ssr a11 # original0x40252732
pc40252735:
sra a3, a3 # original0x40252735
pc40252738:
s16i a3, a5, 0 # original0x40252738
pc4025273b:
addi.n a13, a13, 2 # original0x4025273b
pc4025273d:
addi.n a5, a5, 2 # original0x4025273d
pc4025273f:
bne a8, a13, pc40252708 # original0x4025273f
pc40252742:
l32i a15, a1, 112 # original0x40252742
pc40252745:
j pc40252ae5 # original0x40252745
pc40252748:
l32i a8, a1, 128 # original0x40252748
pc4025274b:
blti a8, 1, pc40252766 # original0x4025274b
pc4025274e:
l32i a9, a1, 128 # original0x4025274e
pc40252751:
mov.n a2, a15 # original0x40252751
pc40252753:
slli a4, a9, 1 # original0x40252753
pc40252756:
add.n a4, a15, a4 # original0x40252756
pc40252758:
l16ui a3, a2, 0 # original0x40252758
pc4025275b:
neg a3, a3 # original0x4025275b
pc4025275e:
s16i a3, a2, 0 # original0x4025275e
pc40252761:
addi.n a2, a2, 2 # original0x40252761
pc40252763:
bne a2, a4, pc40252758 # original0x40252763
pc40252766:
movi.n a10, 0 # original0x40252766
pc40252768:
mov.n a2, a12 # original0x40252768
pc4025276a:
s32i a10, a1, 0x194 # original0x4025276a
pc4025276d:
j pc402527d6 # original0x4025276d
pc40252770:
movi.n a7, 0 # original0x40252770
pc40252772:
beqi a13, -1, pc4025277d # original0x40252772
pc40252775:
l32i a11, a1, 184 # original0x40252775
pc40252778:
slli a13, a13, 1 # original0x40252778
pc4025277b:
add.n a7, a11, a13 # original0x4025277b
pc4025277d:
l32i a12, a1, 116 # original0x4025277d
pc40252780:
l32i a8, a1, 200 # original0x40252780
pc40252783:
beq a12, a8, pc402527a4 # original0x40252783
pc40252786:
l32i a9, a1, 144 # original0x40252786
pc40252789:
l32i a10, a1, 0x1ac # original0x40252789
pc4025278c:
l16si a2, a9, 0 # original0x4025278c
pc4025278f:
l32i a11, a1, 212 # original0x4025278f
pc40252792:
ssl a10 # original0x40252792
pc40252795:
sll a2, a2 # original0x40252795
pc40252798:
sub a2, a2, a11 # original0x40252798
pc4025279b:
l32i a12, a1, 184 # original0x4025279b
pc4025279e:
slli a2, a2, 1 # original0x4025279e
pc402527a1:
add a15, a12, a2 # original0x402527a1
pc402527a4:
l32r a8, fixed_4024f0bc # original0x402527a4
pc402527a7:
l32i a9, a1, 168 # original0x402527a7
pc402527aa:
l32i a10, a1, 0x1ac # original0x402527aa
pc402527ad:
or a14, a6, a14 # original0x402527ad
pc402527b0:
l32i a5, a1, 136 # original0x402527b0
pc402527b3:
l32i a6, a1, 180 # original0x402527b3
pc402527b6:
l32i a4, a1, 128 # original0x402527b6
pc402527b9:
l32i a3, a1, 172 # original0x402527b9
pc402527bc:
s32i.n a14, a1, 16 # original0x402527bc
pc402527be:
s32i.n a9, a1, 12 # original0x402527be
pc402527c0:
s32i.n a8, a1, 8 # original0x402527c0
pc402527c2:
s32i.n a15, a1, 4 # original0x402527c2
pc402527c4:
s32i.n a10, a1, 0 # original0x402527c4
pc402527c6:
addi a2, a1, 32 # original0x402527c6
pc402527c9:
call0 fixed_4024e44c # original0x402527c9
pc402527cc:
extui a12, a2, 0, 8 # original0x402527cc
pc402527cf:
movi.n a11, 0 # original0x402527cf
pc402527d1:
mov.n a2, a12 # original0x402527d1
pc402527d3:
s32i a11, a1, 0x194 # original0x402527d3
pc402527d6:
l32i a14, a1, 156 # original0x402527d6
pc402527d9:
l32i a8, a1, 248 # original0x402527d9
pc402527dc:
l32i a9, a1, 0x10c # original0x402527dc
pc402527df:
sub a3, a14, a8 # original0x402527df
pc402527e2:
s8i a12, a14, 0 # original0x402527e2
pc402527e5:
add.n a3, a3, a9 # original0x402527e5
pc402527e7:
l32i a10, a1, 164 # original0x402527e7
pc402527ea:
s8i a2, a3, 0 # original0x402527ea
pc402527ed:
l32i.n a2, a10, 0 # original0x402527ed
pc402527ef:
l32i a12, a1, 160 # original0x402527ef
pc402527f2:
l32i a14, a1, 116 # original0x402527f2
pc402527f5:
l32i a8, a1, 0x1a4 # original0x402527f5
pc402527f8:
l32i a11, a1, 128 # original0x402527f8
pc402527fb:
add.n a2, a12, a2 # original0x402527fb
pc402527fd:
addi.n a14, a14, 1 # original0x402527fd
pc402527ff:
add.n a8, a8, a2 # original0x402527ff
pc40252801:
l32i a9, a1, 136 # original0x40252801
pc40252804:
s32i a14, a1, 116 # original0x40252804
pc40252807:
slli a3, a11, 3 # original0x40252807
pc4025280a:
s32i a8, a1, 0x1a4 # original0x4025280a
pc4025280d:
movi.n a14, 1 # original0x4025280d
pc4025280f:
blt a3, a9, pc40252815 # original0x4025280f
pc40252812:
movi a14, 0 # original0x40252812
pc40252815:
l32i a11, a1, 144 # original0x40252815
pc40252818:
l32i a12, a1, 156 # original0x40252818
pc4025281b:
l32i a9, a1, 164 # original0x4025281b
pc4025281e:
l32i a8, a1, 204 # original0x4025281e
pc40252821:
movi.n a10, 0 # original0x40252821
pc40252823:
addi.n a11, a11, 2 # original0x40252823
pc40252825:
s32i a10, a1, 88 # original0x40252825
pc40252828:
s32i a11, a1, 144 # original0x40252828
pc4025282b:
add.n a12, a12, a8 # original0x4025282b
pc4025282d:
addi.n a9, a9, 4 # original0x4025282d
pc4025282f:
l32i a10, a1, 116 # original0x4025282f
pc40252832:
l32i a11, a1, 244 # original0x40252832
pc40252835:
s32i a12, a1, 156 # original0x40252835
pc40252838:
s32i a9, a1, 164 # original0x40252838
pc4025283b:
beq a10, a11, pc40252841 # original0x4025283b
pc4025283e:
j pc40250ab0 # original0x4025283e
pc40252841:
l32i a4, a1, 72 # original0x40252841
pc40252844:
l32i a12, a1, 0x1b4 # original0x40252844
pc40252847:
l32i a2, a1, 100 # original0x40252847
pc4025284a:
l32i a3, a1, 104 # original0x4025284a
pc4025284d:
s32i a4, a12, 0 # original0x4025284d
pc40252850:
call0 fixed_402428d8 # original0x40252850
pc40252853:
l32i a0, a1, 0x17c # original0x40252853
pc40252856:
movi a9, 0x180 # original0x40252856
pc40252859:
l32i a12, a1, 0x178 # original0x40252859
pc4025285c:
l32i a13, a1, 0x174 # original0x4025285c
pc4025285f:
l32i a14, a1, 0x170 # original0x4025285f
pc40252862:
l32i a15, a1, 0x16c # original0x40252862
pc40252865:
add a1, a1, a9 # original0x40252865
pc40252868:
ret  # original0x40252868
pc4025286c:
l32i a14, a1, 188 # original0x4025286c
pc4025286f:
blt a6, a14, pc40252875 # original0x4025286f
pc40252872:
j pc4025191e # original0x40252872
pc40252875:
j pc402518a4 # original0x40252875
pc40252878:
l32i a8, a1, 216 # original0x40252878
pc4025287b:
l32i a9, a1, 0x1ac # original0x4025287b
pc4025287e:
l32i a5, a1, 0x100 # original0x4025287e
pc40252881:
l32i a4, a1, 128 # original0x40252881
pc40252884:
l32i a2, a1, 132 # original0x40252884
pc40252887:
s32i a12, a1, 8 # original0x40252887
pc4025288a:
s32i a8, a1, 4 # original0x4025288a
pc4025288d:
s32i a9, a1, 0 # original0x4025288d
pc40252890:
movi.n a7, 0 # original0x40252890
pc40252892:
mov.n a6, a13 # original0x40252892
pc40252894:
mov.n a3, a15 # original0x40252894
pc40252896:
call0 fixed_4024dafc # original0x40252896
pc40252899:
s32i a2, a1, 120 # original0x40252899
pc4025289c:
l32i.n a2, a1, 36 # original0x4025289c
pc4025289e:
# decoder-unreachable/check: beqz a2, 402528a3 <quant_all_bands+8395>
pc402528a0:
j pc40251f4b # original0x402528a0
pc402528a3:
# decoder-unreachable/check: l32i a10, a1, 236
pc402528a6:
# decoder-unreachable/check: l32i a11, a1, 120
pc402528a9:
# decoder-unreachable/check: or a12, a10, a11
pc402528ac:
# decoder-unreachable/check: extui a12, a12, 0, 8
pc402528af:
# decoder-unreachable/check: j 40252766 <quant_all_bands+8078>
pc402528b2:
s32i.n a12, a1, 8 # original0x402528b2
pc402528b4:
l32i a8, a1, 0x1ac # original0x402528b4
pc402528b7:
l32i a12, a1, 216 # original0x402528b7
pc402528ba:
l32i a5, a1, 0x100 # original0x402528ba
pc402528bd:
l32i a4, a1, 128 # original0x402528bd
pc402528c0:
l32i a2, a1, 132 # original0x402528c0
pc402528c3:
s32i.n a12, a1, 4 # original0x402528c3
pc402528c5:
s32i.n a8, a1, 0 # original0x402528c5
pc402528c7:
movi.n a7, 0 # original0x402528c7
pc402528c9:
mov.n a6, a13 # original0x402528c9
pc402528cb:
mov.n a3, a15 # original0x402528cb
pc402528cd:
call0 fixed_4024dafc # original0x402528cd
pc402528d0:
l32i.n a9, a1, 36 # original0x402528d0
pc402528d2:
s32i a2, a1, 120 # original0x402528d2
pc402528d5:
s32i a9, a1, 132 # original0x402528d5
pc402528d8:
# decoder-unreachable/check: beqz a9, 402528dd <quant_all_bands+8453>
pc402528da:
j pc402520bd # original0x402528da
pc402528dd:
# decoder-unreachable/check: l32i a10, a1, 236
pc402528e0:
# decoder-unreachable/check: or a12, a10, a2
pc402528e3:
# decoder-unreachable/check: extui a12, a12, 0, 8
pc402528e6:
# decoder-unreachable/check: j 40252766 <quant_all_bands+8078>
pc402528ea:
s32i a12, a1, 8 # original0x402528ea
pc402528ed:
l32i a8, a1, 0x1ac # original0x402528ed
pc402528f0:
l32i a12, a1, 216 # original0x402528f0
pc402528f3:
addi a11, a1, 32 # original0x402528f3
pc402528f6:
l32i a5, a1, 0x100 # original0x402528f6
pc402528f9:
l32i a4, a1, 128 # original0x402528f9
pc402528fc:
s32i a12, a1, 4 # original0x402528fc
pc402528ff:
s32i a8, a1, 0 # original0x402528ff
pc40252902:
movi.n a7, 0 # original0x40252902
pc40252904:
mov.n a6, a13 # original0x40252904
pc40252906:
mov.n a3, a15 # original0x40252906
pc40252908:
mov.n a2, a11 # original0x40252908
pc4025290a:
s32i a11, a1, 132 # original0x4025290a
pc4025290d:
call0 fixed_4024dafc # original0x4025290d
pc40252910:
s32i a2, a1, 120 # original0x40252910
pc40252913:
l32i.n a2, a1, 36 # original0x40252913
pc40252915:
# decoder-unreachable/check: beqz a2, 40252595 <quant_all_bands+7613>
pc40252918:
j pc40252357 # original0x40252918
pc4025291c:
l32i a10, a1, 216 # original0x4025291c
pc4025291f:
l32i a11, a1, 0x1ac # original0x4025291f
pc40252922:
addi a9, a1, 32 # original0x40252922
pc40252925:
l32i a5, a1, 0x100 # original0x40252925
pc40252928:
l32i a4, a1, 128 # original0x40252928
pc4025292b:
s32i.n a12, a1, 8 # original0x4025292b
pc4025292d:
s32i.n a10, a1, 4 # original0x4025292d
pc4025292f:
s32i.n a11, a1, 0 # original0x4025292f
pc40252931:
movi.n a7, 0 # original0x40252931
pc40252933:
mov.n a6, a13 # original0x40252933
pc40252935:
mov.n a3, a15 # original0x40252935
pc40252937:
or a2, a9, a9 # original0x40252937
pc4025293a:
s32i a9, a1, 132 # original0x4025293a
pc4025293d:
call0 fixed_4024dafc # original0x4025293d
pc40252940:
s32i a2, a1, 120 # original0x40252940
pc40252943:
l32i.n a2, a1, 36 # original0x40252943
pc40252945:
j pc402524c1 # original0x40252945
pc40252948:
# decoder-unreachable/check: j 40252595 <quant_all_bands+7613>
pc4025294c:
# decoder-unreachable/check: mov a2, a14
pc4025294e:
# decoder-unreachable/check: call0 40246830 <ec_tell_frac>
pc40252951:
# decoder-unreachable/check: l32i a12, a1, 132
pc40252954:
# decoder-unreachable/check: l32i a8, a1, 136
pc40252957:
# decoder-unreachable/check: sub a2, a2, a12
pc4025295a:
# decoder-unreachable/check: sub a8, a8, a2
pc4025295d:
# decoder-unreachable/check: s32i a2, a1, 228
pc40252960:
# decoder-unreachable/check: s32i a8, a1, 188
pc40252963:
# decoder-unreachable/check: j 40251270 <quant_all_bands+2712>
pc40252966:
or a3, a13, a13 # original0x40252966
pc40252969:
slli a2, a12, 14 # original0x40252969
pc4025296c:
l32r a0, fixed_40250738 # original0x4025296c
pc4025296f:
callx0 a0 # original0x4025296f
pc40252972:
s32i a2, a1, 196 # original0x40252972
pc40252975:
or a2, a14, a14 # original0x40252975
pc40252978:
call0 fixed_40246830 # original0x40252978
pc4025297b:
l32i a9, a1, 120 # original0x4025297b
pc4025297e:
l32i a10, a1, 136 # original0x4025297e
pc40252981:
sub a2, a2, a9 # original0x40252981
pc40252984:
sub a10, a10, a2 # original0x40252984
pc40252987:
l32i a11, a1, 196 # original0x40252987
pc4025298a:
s32i a2, a1, 228 # original0x4025298a
pc4025298d:
s32i a10, a1, 188 # original0x4025298d
pc40252990:
beqz a11, pc40252996 # original0x40252990
pc40252993:
j pc40251270 # original0x40252993
pc40252996:
j pc40251245 # original0x40252996
pc40252999:
# decoder-unreachable/check: l32i a12, a1, 128
pc4025299c:
# decoder-unreachable/check: blti a12, 1, 402529a2 <quant_all_bands+8650>
pc4025299f:
# decoder-unreachable/check: j 40251140 <quant_all_bands+2408>
pc402529a2:
# decoder-unreachable/check: j 4025294c <quant_all_bands+8564>
pc402529a5:
srai a5, a12, 1 # original0x402529a5
pc402529a8:
addi a12, a5, 1 # original0x402529a8
pc402529ab:
slli a4, a12, 1 # original0x402529ab
pc402529ae:
add a4, a4, a12 # original0x402529ae
pc402529b1:
add a7, a5, a4 # original0x402529b1
pc402529b4:
mov.n a3, a7 # original0x402529b4
pc402529b6:
mov.n a2, a14 # original0x402529b6
pc402529b8:
s32i a4, a1, 0x15c # original0x402529b8
pc402529bb:
s32i a5, a1, 0x158 # original0x402529bb
pc402529be:
s32i a7, a1, 0x154 # original0x402529be
pc402529c1:
call0 fixed_4024695c # original0x402529c1
pc402529c4:
l32i a4, a1, 0x15c # original0x402529c4
pc402529c7:
l32i a5, a1, 0x158 # original0x402529c7
pc402529ca:
l32i a7, a1, 0x154 # original0x402529ca
pc402529cd:
bge a2, a4, pc402529d3 # original0x402529cd
pc402529d0:
j pc402510b8 # original0x402529d0
pc402529d3:
j pc402510d7 # original0x402529d3
pc402529d6:
# decoder-unreachable/check: srai a4, a12, 1
pc402529d9:
# decoder-unreachable/check: addi a3, a4, 1
pc402529db:
# decoder-unreachable/check: slli a2, a3, 1
pc402529de:
# decoder-unreachable/check: add a2, a2, a3
pc402529e0:
# decoder-unreachable/check: add a5, a2, a4
pc402529e2:
# decoder-unreachable/check: blt a4, a6, 402529e8 <quant_all_bands+8720>
pc402529e5:
# decoder-unreachable/check: j 40251084 <quant_all_bands+2220>
pc402529e8:
# decoder-unreachable/check: j 4025108e <quant_all_bands+2230>
pc402529eb:
# decoder-unreachable/check: l32i a8, a1, 128
pc402529ee:
# decoder-unreachable/check: bgei a8, 3, 402529d6 <quant_all_bands+8702>
pc402529f1:
# decoder-unreachable/check: j 40252a85 <quant_all_bands+8877>
pc402529f4:
l32i a9, a1, 240 # original0x402529f4
pc402529f7:
# decoder-unreachable/check: bnez a9, 40252b75 <quant_all_bands+9117>
pc402529fa:
or a2, a14, a14 # original0x402529fa
pc402529fd:
call0 fixed_40246830 # original0x402529fd
pc40252a00:
or a12, a2, a2 # original0x40252a00
pc40252a03:
movi a13, 0 # original0x40252a03
pc40252a06:
j pc402511c8 # original0x40252a06
pc40252a09:
l32i a12, a1, 176 # original0x40252a09
pc40252a0c:
s32i a4, a1, 220 # original0x40252a0c
pc40252a0f:
l32i a4, a1, 176 # original0x40252a0f
pc40252a12:
movnez a12, a14, a13 # original0x40252a12
pc40252a15:
s32i a14, a1, 204 # original0x40252a15
pc40252a18:
extui a12, a12, 0, 8 # original0x40252a18
pc40252a1b:
mov.n a14, a4 # original0x40252a1b
pc40252a1d:
j pc40250848 # original0x40252a1d
pc40252a20:
l32i a10, a1, 132 # original0x40252a20
pc40252a23:
extui a12, a12, 0, 8 # original0x40252a23
pc40252a26:
# decoder-unreachable/check: beqz a10, 40252766 <quant_all_bands+8078>
pc40252a29:
j pc402525ff # original0x40252a29
pc40252a2c:
l32i a9, a1, 188 # original0x40252a2c
pc40252a2f:
mov.n a10, a8 # original0x40252a2f
pc40252a31:
l32i a8, a1, 228 # original0x40252a31
pc40252a34:
addi a12, a11, -8 # original0x40252a34
pc40252a37:
sub a12, a12, a8 # original0x40252a37
pc40252a3a:
addi a9, a9, -8 # original0x40252a3a
pc40252a3d:
l32r a2, fixed_4024f620 # original0x40252a3d
pc40252a40:
s32i a12, a1, 64 # original0x40252a40
pc40252a43:
s32i a9, a1, 188 # original0x40252a43
pc40252a46:
blt a2, a10, pc40252a4c # original0x40252a46
pc40252a49:
j pc402513c9 # original0x40252a49
pc40252a4c:
l32i a11, a1, 172 # original0x40252a4c
pc40252a4f:
s32i a15, a1, 132 # original0x40252a4f
pc40252a52:
s32i a11, a1, 228 # original0x40252a52
pc40252a55:
j pc402513d2 # original0x40252a55
pc40252a58:
l32i a8, a1, 228 # original0x40252a58
pc40252a5b:
l32r a2, fixed_4024f620 # original0x40252a5b
pc40252a5e:
sub a12, a14, a8 # original0x40252a5e
pc40252a61:
l32i a9, a1, 196 # original0x40252a61
pc40252a64:
s32i a12, a1, 64 # original0x40252a64
pc40252a67:
blt a2, a9, pc40252a6d # original0x40252a67
pc40252a6a:
j pc40251449 # original0x40252a6a
pc40252a6d:
l32i a10, a1, 172 # original0x40252a6d
pc40252a70:
movi.n a11, 1 # original0x40252a70
pc40252a72:
movi.n a12, -1 # original0x40252a72
pc40252a74:
s32i a15, a1, 132 # original0x40252a74
pc40252a77:
s32i a10, a1, 228 # original0x40252a77
pc40252a7a:
s32i a11, a1, 0x100 # original0x40252a7a
pc40252a7d:
s32i a12, a1, 252 # original0x40252a7d
pc40252a80:
j pc4025145c # original0x40252a80
pc40252a85:
# decoder-unreachable/check: or a3, a6, a6
pc40252a88:
# decoder-unreachable/check: addi a4, a13, 1
pc40252a8b:
# decoder-unreachable/check: or a2, a14, a14
pc40252a8e:
# decoder-unreachable/check: s32i a6, a1, 344
pc40252a91:
# decoder-unreachable/check: call0 40253774 <ec_enc_uint>
pc40252a94:
# decoder-unreachable/check: l32i a6, a1, 344
pc40252a97:
# decoder-unreachable/check: mov a3, a13
pc40252a99:
# decoder-unreachable/check: slli a2, a6, 14
pc40252a9c:
# decoder-unreachable/check: l32r a0, 40250738 <anti_collapse+6696>
pc40252a9f:
# decoder-unreachable/check: callx0 a0
pc40252aa2:
# decoder-unreachable/check: s32i a2, a1, 196
pc40252aa5:
# decoder-unreachable/check: bnez a2, 40252999 <quant_all_bands+8641>
pc40252aa8:
# decoder-unreachable/check: j 40251108 <quant_all_bands+2352>
pc40252aac:
addi a3, a13, 1 # original0x40252aac
pc40252aaf:
or a2, a14, a14 # original0x40252aaf
pc40252ab2:
call0 fixed_40246c20 # original0x40252ab2
pc40252ab5:
or a12, a2, a2 # original0x40252ab5
pc40252ab8:
j pc40252966 # original0x40252ab8
pc40252abc:
mov.n a3, a9 # original0x40252abc
pc40252abe:
addi a2, a2, -16 # original0x40252abe
pc40252ac1:
j pc40250f97 # original0x40252ac1
pc40252ac4:
slli a3, a9, 1 # original0x40252ac4
pc40252ac7:
addi a2, a2, -4 # original0x40252ac7
pc40252aca:
addi.n a3, a3, -1 # original0x40252aca
pc40252acc:
j pc40250f97 # original0x40252acc
pc40252acf:
l32i a11, a1, 192 # original0x40252acf
pc40252ad2:
beqz.n a11, pc40252ada # original0x40252ad2
pc40252ad4:
bbsi a14, 0, pc40252ada # original0x40252ad4
pc40252ad7:
j pc40250bc0 # original0x40252ad7
pc40252ada:
l32i a14, a1, 0x104 # original0x40252ada
pc40252add:
s32i a14, a1, 192 # original0x40252add
pc40252ae0:
j pc40250bc0 # original0x40252ae0
pc40252ae5:
l32i a8, a1, 240 # original0x40252ae5
pc40252ae8:
beqz a8, pc40252766 # original0x40252ae8
pc40252aeb:
j pc4025274e # original0x40252aeb
pc40252aee:
# decoder-unreachable/check: movi a12, 0
pc40252af0:
# decoder-unreachable/check: l32i a9, a1, 132
pc40252af3:
# decoder-unreachable/check: l32i a10, a1, 252
pc40252af6:
# decoder-unreachable/check: l16ui a2, a9, 2
pc40252af9:
# decoder-unreachable/check: l32i a11, a1, 228
pc40252afc:
# decoder-unreachable/check: mul16s a2, a2, a10
pc40252aff:
# decoder-unreachable/check: l32i a14, a1, 256
pc40252b02:
# decoder-unreachable/check: s16i a2, a11, 0
pc40252b05:
# decoder-unreachable/check: l16ui a2, a9, 0
pc40252b08:
# decoder-unreachable/check: mul16s a2, a2, a14
pc40252b0b:
# decoder-unreachable/check: s16i a2, a11, 2
pc40252b0e:
# decoder-unreachable/check: j 40252766 <quant_all_bands+8078>
pc40252b11:
# decoder-unreachable/check: l32i a11, a1, 196
pc40252b14:
# decoder-unreachable/check: beqz a11, 40252b19 <quant_all_bands+9025>
pc40252b16:
# decoder-unreachable/check: j 40251618 <quant_all_bands+3648>
pc40252b19:
# decoder-unreachable/check: j 40251621 <quant_all_bands+3657>
pc40252b1d:
# decoder-unreachable/check: l32i a9, a1, 152
pc40252b20:
# decoder-unreachable/check: beqz a9, 40252b25 <quant_all_bands+9037>
pc40252b22:
# decoder-unreachable/check: j 40251714 <quant_all_bands+3900>
pc40252b25:
# decoder-unreachable/check: j 40251725 <quant_all_bands+3917>
pc40252b28:
l32i a11, a1, 0x144 # original0x40252b28
pc40252b2b:
l32i a10, a1, 64 # original0x40252b2b
pc40252b2e:
extui a11, a11, 0, 8 # original0x40252b2e
pc40252b31:
l32i a12, a1, 128 # original0x40252b31
pc40252b34:
s32i a10, a1, 252 # original0x40252b34
pc40252b37:
s32i a11, a1, 0x138 # original0x40252b37
pc40252b3a:
mov.n a14, a10 # original0x40252b3a
pc40252b3c:
bnei a12, 2, pc40252b42 # original0x40252b3c
pc40252b3f:
j pc40252a58 # original0x40252b3f
pc40252b42:
j pc40251ce2 # original0x40252b42
pc40252b45:
# decoder-unreachable/check: l32i a6, a1, 76
pc40252b48:
# decoder-unreachable/check: l32i a5, a1, 128
pc40252b4b:
# decoder-unreachable/check: l32i a2, a1, 172
pc40252b4e:
# decoder-unreachable/check: movi a4, 1
pc40252b51:
# decoder-unreachable/check: or a3, a15, a15
pc40252b54:
# decoder-unreachable/check: call0 40249774 <stereo_itheta>
pc40252b57:
# decoder-unreachable/check: mov a3, a2
pc40252b59:
# decoder-unreachable/check: mov a2, a14
pc40252b5b:
# decoder-unreachable/check: s32i a3, a1, 340
pc40252b5e:
# decoder-unreachable/check: call0 40246830 <ec_tell_frac>
pc40252b61:
# decoder-unreachable/check: l32i a3, a1, 340
pc40252b64:
# decoder-unreachable/check: l32i a4, a1, 80
pc40252b67:
# decoder-unreachable/check: s32i a2, a1, 132
pc40252b6a:
# decoder-unreachable/check: mull a6, a13, a3
pc40252b6d:
# decoder-unreachable/check: bnez a4, 40252b72 <quant_all_bands+9114>
pc40252b6f:
# decoder-unreachable/check: j 40251024 <quant_all_bands+2124>
pc40252b72:
# decoder-unreachable/check: j 4025102d <quant_all_bands+2133>
pc40252b75:
# decoder-unreachable/check: l32i a6, a1, 76
pc40252b78:
# decoder-unreachable/check: l32i a5, a1, 128
pc40252b7b:
# decoder-unreachable/check: l32i a2, a1, 172
pc40252b7e:
# decoder-unreachable/check: movi a4, 1
pc40252b81:
# decoder-unreachable/check: or a3, a15, a15
pc40252b84:
# decoder-unreachable/check: call0 40249774 <stereo_itheta>
pc40252b87:
# decoder-unreachable/check: mov a13, a2
pc40252b89:
# decoder-unreachable/check: mov a2, a14
pc40252b8b:
# decoder-unreachable/check: call0 40246830 <ec_tell_frac>
pc40252b8e:
# decoder-unreachable/check: mov a12, a2
pc40252b90:
# decoder-unreachable/check: j 4025117b <quant_all_bands+2467>
pc40252b94:
l32r a9, fixed_4024f0bc # original0x40252b94
pc40252b97:
l32i a10, a1, 168 # original0x40252b97
pc40252b9a:
l32i a11, a1, 144 # original0x40252b9a
pc40252b9d:
s32i a6, a1, 16 # original0x40252b9d
pc40252ba0:
s32i a10, a1, 12 # original0x40252ba0
pc40252ba3:
s32i a9, a1, 8 # original0x40252ba3
pc40252ba6:
l16si a2, a11, 0 # original0x40252ba6
pc40252ba9:
s32i a9, a1, 140 # original0x40252ba9
pc40252bac:
l32i a9, a1, 0x1ac # original0x40252bac
pc40252baf:
l32i a10, a1, 212 # original0x40252baf
pc40252bb2:
ssl a9 # original0x40252bb2
pc40252bb5:
sll a2, a2 # original0x40252bb5
pc40252bb8:
sub a2, a2, a10 # original0x40252bb8
pc40252bbb:
l32i a11, a1, 184 # original0x40252bbb
pc40252bbe:
slli a2, a2, 1 # original0x40252bbe
pc40252bc1:
addi a12, a1, 32 # original0x40252bc1
pc40252bc4:
add.n a2, a11, a2 # original0x40252bc4
pc40252bc6:
l32i a6, a1, 180 # original0x40252bc6
pc40252bc9:
l32i a4, a1, 128 # original0x40252bc9
pc40252bcc:
l32i a3, a1, 172 # original0x40252bcc
pc40252bcf:
s32i.n a2, a1, 4 # original0x40252bcf
pc40252bd1:
movi.n a7, 0 # original0x40252bd1
pc40252bd3:
mov.n a5, a8 # original0x40252bd3
pc40252bd5:
mov.n a2, a12 # original0x40252bd5
pc40252bd7:
s32i.n a9, a1, 0 # original0x40252bd7
pc40252bd9:
s32i a12, a1, 132 # original0x40252bd9
pc40252bdc:
s32i a8, a1, 0x154 # original0x40252bdc
pc40252bdf:
call0 fixed_4024e44c # original0x40252bdf
pc40252be2:
mov.n a12, a2 # original0x40252be2
pc40252be4:
movi.n a7, 0 # original0x40252be4
pc40252be6:
l32i a8, a1, 0x154 # original0x40252be6
pc40252be9:
j pc40250e01 # original0x40252be9
pc40252bec:
l32i a12, a1, 116 # original0x40252bec
pc40252bef:
l32i a9, a1, 200 # original0x40252bef
pc40252bf2:
bne a12, a9, pc40252b94 # original0x40252bf2
pc40252bf5:
j pc40252c5b # original0x40252bf5
pc40252bf8:
mov.n a8, a7 # original0x40252bf8
pc40252bfa:
mov.n a4, a5 # original0x40252bfa
pc40252bfc:
add.n a8, a2, a8 # original0x40252bfc
pc40252bfe:
l8ui a5, a8, 0 # original0x40252bfe
pc40252c01:
l32i a3, a1, 64 # original0x40252c01
pc40252c04:
addi.n a5, a5, 1 # original0x40252c04
pc40252c06:
sub a3, a3, a5 # original0x40252c06
pc40252c09:
s32i a3, a1, 64 # original0x40252c09
pc40252c0c:
bgez a3, pc40252c12 # original0x40252c0c
pc40252c0f:
j pc402518ac # original0x40252c0f
pc40252c12:
j pc402518c6 # original0x40252c12
pc40252c15:
l32r a10, fixed_4024f0bc # original0x40252c15
pc40252c18:
l32i a12, a1, 168 # original0x40252c18
pc40252c1b:
l32i a9, a1, 0x1ac # original0x40252c1b
pc40252c1e:
addi a11, a1, 32 # original0x40252c1e
pc40252c21:
s32i a6, a1, 16 # original0x40252c21
pc40252c24:
movi a2, 0 # original0x40252c24
pc40252c27:
l32i a6, a1, 180 # original0x40252c27
pc40252c2a:
l32i a4, a1, 128 # original0x40252c2a
pc40252c2d:
l32i a3, a1, 172 # original0x40252c2d
pc40252c30:
s32i a12, a1, 12 # original0x40252c30
pc40252c33:
s32i.n a10, a1, 8 # original0x40252c33
pc40252c35:
s32i.n a2, a1, 4 # original0x40252c35
pc40252c37:
s32i.n a9, a1, 0 # original0x40252c37
pc40252c39:
mov.n a5, a8 # original0x40252c39
pc40252c3b:
mov.n a2, a11 # original0x40252c3b
pc40252c3d:
s32i a10, a1, 140 # original0x40252c3d
pc40252c40:
s32i a8, a1, 0x154 # original0x40252c40
pc40252c43:
s32i a11, a1, 132 # original0x40252c43
pc40252c46:
call0 fixed_4024e44c # original0x40252c46
pc40252c49:
l32i a10, a1, 0x1c4 # original0x40252c49
pc40252c4c:
mov.n a12, a2 # original0x40252c4c
pc40252c4e:
add.n a7, a10, a13 # original0x40252c4e
pc40252c50:
movi.n a2, 0 # original0x40252c50
pc40252c52:
l32i a8, a1, 0x154 # original0x40252c52
pc40252c55:
l32i a9, a1, 0x1ac # original0x40252c55
pc40252c58:
j pc40250e20 # original0x40252c58
pc40252c5b:
l32r a11, fixed_4024f0bc # original0x40252c5b
pc40252c5e:
l32i a9, a1, 168 # original0x40252c5e
pc40252c61:
s32i a11, a1, 140 # original0x40252c61
pc40252c64:
s32i a11, a1, 8 # original0x40252c64
pc40252c67:
l32i a11, a1, 0x1ac # original0x40252c67
pc40252c6a:
addi a12, a1, 32 # original0x40252c6a
pc40252c6d:
movi a10, 0 # original0x40252c6d
pc40252c70:
s32i a6, a1, 16 # original0x40252c70
pc40252c73:
l32i a4, a1, 128 # original0x40252c73
pc40252c76:
l32i a6, a1, 180 # original0x40252c76
pc40252c79:
l32i a3, a1, 172 # original0x40252c79
pc40252c7c:
s32i.n a9, a1, 12 # original0x40252c7c
pc40252c7e:
mov.n a7, a10 # original0x40252c7e
pc40252c80:
mov.n a5, a8 # original0x40252c80
pc40252c82:
mov.n a2, a12 # original0x40252c82
pc40252c84:
s32i.n a10, a1, 4 # original0x40252c84
pc40252c86:
s32i.n a11, a1, 0 # original0x40252c86
pc40252c88:
s32i a12, a1, 132 # original0x40252c88
pc40252c8b:
s32i a8, a1, 0x154 # original0x40252c8b
pc40252c8e:
call0 fixed_4024e44c # original0x40252c8e
pc40252c91:
movi.n a7, 0 # original0x40252c91
pc40252c93:
mov.n a12, a2 # original0x40252c93
pc40252c95:
l32i a8, a1, 0x154 # original0x40252c95
pc40252c98:
mov.n a2, a7 # original0x40252c98
pc40252c9a:
l32i a9, a1, 0x1ac # original0x40252c9a
pc40252c9d:
j pc40250e20 # original0x40252c9d
quant_live_end:
.space 9416 - (. - pc402507d8), 0
.end no-transform
