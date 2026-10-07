/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_crc_check @ ram:43010420
 * Types and parameter counts are inferred; verify against disassembly. */

bool sbr_crc_check(undefined4 *param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uStack_3c;
  undefined2 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  int iStack_28;
  int iStack_24;

  gp = &__global_pointer_;
  uVar2 = buf_getbits(param_1,10);
  iStack_28 = param_1[3];
  iStack_24 = param_1[4];
  uStack_34 = *param_1;
  uStack_2c = param_1[2];
  uStack_30 = param_1[1];
  uVar4 = iStack_24 - iStack_28;
  if (param_2 < (uint)(iStack_24 - iStack_28)) {
    uVar4 = param_2;
  }
  uStack_3c = 0x2000000;
  uStack_38 = 0x233;
  if (uVar4 >> 4 != 0) {
    uVar1 = 0;
    do {
      uVar3 = buf_getbits(&uStack_34,0x10);
      uVar1 = uVar1 + 1;
      check_crc(&uStack_3c,uVar3,0x10);
    } while (uVar4 >> 4 != uVar1);
  }
  uVar3 = buf_getbits(&uStack_34,uVar4 & 0xf);
  check_crc(&uStack_3c,uVar3,uVar4 & 0xf);
  return (uStack_3c & 0x3ff) == uVar2;
}
