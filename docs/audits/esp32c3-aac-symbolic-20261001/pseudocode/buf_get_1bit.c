/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: buf_get_1bit @ ram:43000bca
 * Types and parameter counts are inferred; verify against disassembly. */

uint buf_get_1bit(undefined4 *param_1)

{
  byte bVar1;
  uint uVar2;
  byte *pbVar3;
  uint uVar4;

  gp = &__global_pointer_;
  uVar4 = param_1[1];
  uVar2 = param_1[2];
  if (uVar4 < 0x11) {
    pbVar3 = (byte *)*param_1;
    uVar4 = uVar4 + 0x10;
    *param_1 = pbVar3 + 1;
    bVar1 = *pbVar3;
    *param_1 = pbVar3 + 2;
    uVar2 = (uint)bVar1 << 8 | uVar2 << 0x10;
    param_1[2] = uVar2;
    uVar2 = pbVar3[1] | uVar2;
    param_1[2] = uVar2;
  }
  param_1[1] = uVar4 - 1;
  param_1[3] = param_1[3] + 1;
  return uVar2 >> (uVar4 - 1 & 0x1f) & 1;
}
