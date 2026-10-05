
idf\esp32c3-oled-native\build-heap-fragment\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026a6a <__wrap_heap_caps_free>:
42026a6a:	1101                	addi	sp,sp,-32
42026a6c:	ce06                	sw	ra,28(sp)
42026a6e:	c62a                	sw	a0,12(sp)
42026a70:	fe360097          	auipc	ra,0xfe360
42026a74:	2d6080e7          	jalr	726(ra) # 40386d46 <vPortEnterCritical>
42026a78:	4532                	lw	a0,12(sp)
42026a7a:	8e5de0ef          	jal	4200535e <heap_caps_free>
42026a7e:	40f2                	lw	ra,28(sp)
42026a80:	6105                	addi	sp,sp,32
42026a82:	fe360317          	auipc	t1,0xfe360
42026a86:	30030067          	jr	768(t1) # 40386d82 <vPortExitCritical>
