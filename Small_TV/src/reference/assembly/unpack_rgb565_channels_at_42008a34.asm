
factory-irom.bin:     file format binary


Disassembly of section .data:

42008a34 <.data+0x8a14>:
42008a34:	00b55813          	srli	a6,a0,0xb
42008a38:	00555793          	srli	a5,a0,0x5
42008a3c:	03f7f793          	andi	a5,a5,63
42008a40:	01f57713          	andi	a4,a0,31
42008a44:	8135                	srli	a0,a0,0xd
42008a46:	080e                	slli	a6,a6,0x3
42008a48:	01056533          	or	a0,a0,a6
42008a4c:	00a58023          	sb	a0,0(a1)
42008a50:	0047d593          	srli	a1,a5,0x4
42008a54:	078a                	slli	a5,a5,0x2
42008a56:	8fcd                	or	a5,a5,a1
42008a58:	00f60023          	sb	a5,0(a2)
42008a5c:	00275793          	srli	a5,a4,0x2
42008a60:	070e                	slli	a4,a4,0x3
42008a62:	8fd9                	or	a5,a5,a4
42008a64:	00f68023          	sb	a5,0(a3)
42008a68:	8082                	ret
