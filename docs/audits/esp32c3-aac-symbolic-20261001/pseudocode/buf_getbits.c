/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: buf_getbits @ ram:43000b7e
 * Types and parameter counts are inferred; verify against disassembly. */

uint buf_getbits(undefined4 *param_1,uint param_2)

{
  byte bVar1;
  byte *pbVar2;
  uint uVar3;
  uint uVar4;

  gp = &__global_pointer_;
  uVar3 = param_1[1];
  uVar4 = param_1[2];
  if (uVar3 < 0x11) {
    pbVar2 = (byte *)*param_1;
    uVar3 = uVar3 + 0x10;
    *param_1 = pbVar2 + 1;
    bVar1 = *pbVar2;
    *param_1 = pbVar2 + 2;
    uVar4 = (uint)bVar1 << 8 | uVar4 << 0x10;
    param_1[2] = uVar4;
    uVar4 = pbVar2[1] | uVar4;
    param_1[2] = uVar4;
  }
  param_1[1] = uVar3 - param_2;
  param_1[3] = param_2 + param_1[3];
  return (1 << (param_2 & 0x1f)) - 1U & uVar4 >> (uVar3 - param_2 & 0x1f);
}
