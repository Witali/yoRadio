
factory-irom.bin:     file format binary


Disassembly of section .data:

42008a96 <.data+0x8a76>:
42008a96:	810d                	srli	a0,a0,0x3
42008a98:	8189                	srli	a1,a1,0x2
42008a9a:	820d                	srli	a2,a2,0x3
42008a9c:	052e                	slli	a0,a0,0xb
42008a9e:	0596                	slli	a1,a1,0x5
42008aa0:	8d4d                	or	a0,a0,a1
42008aa2:	0542                	slli	a0,a0,0x10
42008aa4:	8541                	srai	a0,a0,0x10
42008aa6:	8d51                	or	a0,a0,a2
42008aa8:	0542                	slli	a0,a0,0x10
42008aaa:	8141                	srli	a0,a0,0x10
42008aac:	8082                	ret
