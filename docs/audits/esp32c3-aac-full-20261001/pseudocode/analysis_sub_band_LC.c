/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: analysis_sub_band_LC @ ram:430004d2
 * Types and parameter counts are inferred; verify against disassembly. */

void analysis_sub_band_LC(int *param_1,int *param_2,int param_3,int *param_4)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  int *piVar6;

  gp = &__global_pointer_;
  piVar6 = param_1 + 0x20;
  piVar3 = param_4;
  do {
    iVar4 = param_1[0x20];
    iVar5 = *param_1;
    iVar2 = param_1[0x21];
    iVar1 = param_1[1];
    *piVar3 = iVar4 - iVar5 >> 1;
    piVar3[1] = iVar2 - iVar1 >> 1;
    piVar3[0x20] = iVar4 + iVar5;
    piVar3[0x21] = iVar2 + iVar1;
    iVar2 = param_1[0x22];
    iVar5 = param_1[2];
    iVar1 = param_1[0x23];
    iVar4 = param_1[3];
    piVar3[2] = iVar2 - iVar5 >> 1;
    param_1 = param_1 + 4;
    piVar3[0x22] = iVar2 + iVar5;
    piVar3[3] = iVar1 - iVar4 >> 1;
    piVar3[0x23] = iVar1 + iVar4;
    piVar3 = piVar3 + 4;
  } while (piVar6 != param_1);
  idct_32(param_4);
  dst_32(param_4 + 0x20,param_4 + 0x40);
  iVar1 = 0;
  piVar3 = param_2;
  if (0 < param_3) {
    do {
      *piVar3 = *param_4 + param_4[0x20];
      iVar1 = iVar1 + 4;
      piVar3[1] = param_4[0x21] - param_4[1];
      piVar3[2] = -param_4[0x22] - param_4[2];
      piVar3[3] = param_4[3] - param_4[0x23];
      param_4 = param_4 + 4;
      piVar3 = piVar3 + 4;
    } while (iVar1 < param_3);
    if (param_3 == 0x20) {
      return;
    }
  }
  memset(param_2 + param_3,0,(0x20 - param_3) * 4);
  return;
}
