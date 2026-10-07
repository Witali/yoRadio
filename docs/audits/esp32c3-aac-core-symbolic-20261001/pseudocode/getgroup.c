/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: getgroup @ ram:43008a0e
 * Types and parameter counts are inferred; verify against disassembly. */

void getgroup(int *param_1,aac_analysis_bits_t *bits)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;

  gp = &__global_pointer_;
  uVar4 = bits->used_bits;
  uVar3 = bits->input_length - (uVar4 >> 3);
  if (uVar3 < 2) {
    uVar2 = 0;
    if (uVar3 == 1) {
      uVar2 = (((uint)(byte)*(ushort *)(bits->buffer + (uVar4 >> 3)) << 8) << (uVar4 & 7)) >> 9 &
              0x7f;
    }
  }
  else {
    uVar1 = *(ushort *)(bits->buffer + (uVar4 >> 3));
    uVar2 = (((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar4 & 7)) << 0x10) >> 0x19;
  }
  bits->used_bits = uVar4 + 7;
  uVar3 = 0x40;
  iVar5 = 1;
  do {
    if ((uVar3 & uVar2) == 0) {
      *param_1 = iVar5;
      param_1 = param_1 + 1;
    }
    iVar5 = iVar5 + 1;
    uVar3 = uVar3 >> 1;
  } while (iVar5 != 8);
  *param_1 = 8;
  return;
}
