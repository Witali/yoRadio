/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: gen_rand_vector @ ram:420582f0
 * Types and parameter counts are inferred; verify against disassembly. */

int gen_rand_vector(int *param_1,uint param_2,int *param_3,uint param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int *piVar6;
  uint uVar7;
  int iVar8;

  gp = &__global_pointer_;
  if (0x400 < param_2) {
    return 0x1e;
  }
  if ((int)param_2 >> 1 == 0) {
LAB_ram_42058408:
    return 0x1e - ((int)param_4 >> 2);
  }
  iVar3 = *param_3;
  iVar8 = 0;
  piVar1 = param_1;
  do {
    piVar6 = piVar1 + 2;
    iVar3 = iVar3 * 0x19660d + 0x3c6ef35f;
    iVar5 = iVar3 >> 0x10;
    *piVar1 = iVar5;
    iVar3 = iVar3 * 0x19660d + 0x3c6ef35f;
    iVar2 = iVar3 >> 0x10;
    piVar1[1] = iVar2;
    iVar8 = (iVar2 * iVar2 >> 6) + (iVar5 * iVar5 >> 6) + iVar8;
    piVar1 = piVar6;
  } while (piVar6 != param_1 + ((int)param_2 >> 1) * 2);
  *param_3 = iVar3;
  if (iVar8 == 0) goto LAB_ram_42058408;
  if (iVar8 < 0x8000) {
    uVar7 = *(uint *)(scale_mod_4 + (param_4 & 3) * 4);
    iVar3 = 0x18;
  }
  else {
    iVar3 = 0;
    do {
      iVar2 = iVar3;
      iVar8 = iVar8 >> 1;
      iVar3 = iVar2 + 1;
    } while (0x7fff < iVar8);
    uVar4 = iVar2 - 0xc;
    uVar7 = *(uint *)(scale_mod_4 + (param_4 & 3) * 4);
    if (-1 < (int)uVar4) {
      iVar3 = 0x1e;
      if (uVar4 != 0) {
        if ((uVar4 & 1) != 0) {
          uVar7 = uVar7 * 0x2d41 >> 0xe;
        }
        iVar3 = ((int)uVar4 >> 1) + 0x1e;
      }
      goto LAB_ram_420583a2;
    }
    uVar4 = 0xd - iVar3;
    iVar3 = 0x1e - ((int)uVar4 >> 1);
    if ((uVar4 & 1) == 0) goto LAB_ram_420583a2;
  }
  uVar7 = uVar7 * 0x5a82 >> 0xe;
LAB_ram_420583a2:
  uVar7 = ((((((((iVar8 * 0x1248 >> 0xf) + -0x460f) * iVar8 >> 0xf) + 0x6c31) * iVar8 >> 0xf) +
            -0x5736) * iVar8 >> 0xf) + 0x2ecc) * uVar7 >> 0xd;
  piVar1 = param_1;
  do {
    piVar6 = piVar1 + 2;
    *piVar1 = *piVar1 * uVar7;
    piVar1[1] = uVar7 * piVar1[1];
    piVar1 = piVar6;
  } while (piVar6 != param_1 + ((int)param_2 >> 1) * 2);
  return iVar3 - ((int)param_4 >> 2);
}
