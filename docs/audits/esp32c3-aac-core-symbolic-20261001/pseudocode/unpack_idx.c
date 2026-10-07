/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: unpack_idx @ ram:43015c06
 * Types and parameter counts are inferred; verify against disassembly. */

void unpack_idx(undefined2 *param_1,int param_2,aac_analysis_codebook_t *book,undefined4 param_4,
               int *param_5)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;

  gp = &__global_pointer_;
  iVar1 = book->modulus;
  iVar7 = book->offset;
  iVar6 = *param_5;
  if (book->dimensions == 4) {
    iVar3 = param_2 * 0x13 >> 9;
    uVar4 = iVar3 - iVar7;
    *param_1 = (short)uVar4;
    iVar2 = ((int)uVar4 >> 0x1f ^ uVar4) - ((int)uVar4 >> 0x1f);
    iVar3 = iVar3 * -0x1b + param_2;
    if (iVar6 < iVar2) {
      *param_5 = iVar2;
      iVar6 = iVar2;
    }
    iVar5 = iVar3 * 0x39 >> 9;
    uVar4 = iVar5 - iVar7;
    param_1[1] = (short)uVar4;
    iVar2 = ((int)uVar4 >> 0x1f ^ uVar4) - ((int)uVar4 >> 0x1f);
    param_1 = param_1 + 2;
    param_2 = iVar3 + iVar5 * -9;
    if (iVar6 < iVar2) {
      *param_5 = iVar2;
      iVar6 = iVar2;
    }
  }
  iVar3 = param_2 * *(int *)(div_mod + iVar1 * 4) >> 0xd;
  uVar4 = iVar3 - iVar7;
  *param_1 = (short)uVar4;
  iVar2 = ((int)uVar4 >> 0x1f ^ uVar4) - ((int)uVar4 >> 0x1f);
  if (iVar6 < iVar2) {
    *param_5 = iVar2;
    iVar6 = iVar2;
  }
  uVar4 = (param_2 - iVar1 * iVar3) - iVar7;
  param_1[1] = (short)uVar4;
  iVar1 = ((int)uVar4 >> 0x1f ^ uVar4) - ((int)uVar4 >> 0x1f);
  if (iVar6 < iVar1) {
    *param_5 = iVar1;
  }
  return;
}
