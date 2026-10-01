/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: find_adts_syncword @ ram:43006e58
 * Types and parameter counts are inferred; verify against disassembly. */

int find_adts_syncword(uint *param_1,int *param_2,int param_3,uint param_4)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  byte *pbVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;

  gp = &__global_pointer_;
  uVar5 = param_2[1];
  if (param_2[2] - param_3 <= (int)uVar5) {
    *param_1 = 0;
    return -1;
  }
  uVar3 = param_2[3] - (uVar5 >> 3);
  uVar8 = *param_1;
  iVar2 = (param_2[2] - param_3) - uVar5;
  pbVar4 = (byte *)((uVar5 >> 3) + *param_2);
  uVar7 = uVar5 & 7;
  if (3 < uVar3) {
    uVar6 = (((uint)*pbVar4 << 0x18 | (uint)pbVar4[1] << 0x10 | (uint)pbVar4[3] |
             (uint)pbVar4[2] << 8) << uVar7) >> (0x20U - param_3 & 0x1f);
    uVar3 = param_4 & uVar6;
    goto LAB_ram_43006ec6;
  }
  if (uVar3 == 2) {
    uVar3 = 0;
LAB_ram_43006fca:
    uVar3 = (uint)pbVar4[1] << 0x10 | uVar3;
  }
  else {
    if (uVar3 == 3) {
      uVar3 = (uint)pbVar4[2] << 8;
      goto LAB_ram_43006fca;
    }
    if (uVar3 != 1) {
      uVar3 = 0;
      uVar6 = 0;
      goto LAB_ram_43006ec6;
    }
    uVar3 = 0;
  }
  uVar6 = (((uint)*pbVar4 << 0x18 | uVar3) << uVar7) >> (0x20U - param_3 & 0x1f);
  uVar3 = param_4 & uVar6;
LAB_ram_43006ec6:
  param_2[1] = uVar5 + param_3;
  if ((iVar2 != 0) && (uVar5 = uVar5 + param_3, uVar8 != uVar3)) {
    do {
      uVar3 = uVar5;
      uVar5 = param_2[3] - (uVar3 >> 3);
      iVar2 = iVar2 + -1;
      uVar6 = uVar6 << 1;
      pbVar4 = (byte *)((uVar3 >> 3) + *param_2);
      if (uVar5 < 4) {
        if (uVar5 == 2) {
          uVar5 = 0;
LAB_ram_43006fac:
          uVar5 = (uint)pbVar4[1] << 0x10 | uVar5;
        }
        else {
          if (uVar5 == 3) {
            uVar5 = (uint)pbVar4[2] << 8;
            goto LAB_ram_43006fac;
          }
          if (uVar5 != 1) goto LAB_ram_43006f08;
          uVar5 = 0;
        }
        bVar1 = *pbVar4;
        param_2[1] = uVar3 + 1;
        uVar6 = uVar6 | (((uint)bVar1 << 0x18 | uVar5) << (uVar3 & 7)) >> 0x1f;
      }
      else {
        uVar6 = uVar6 | (((uint)*pbVar4 << 0x18 | (uint)pbVar4[1] << 0x10 | (uint)pbVar4[3] |
                         (uint)pbVar4[2] << 8) << (uVar3 & 7)) >> 0x1f;
LAB_ram_43006f08:
        param_2[1] = uVar3 + 1;
      }
    } while (((param_4 & uVar6) != uVar8) && (uVar5 = uVar3 + 1, iVar2 != 0));
    uVar7 = (uVar3 + 1) - param_3 & 7;
  }
  param_2[4] = uVar7;
  *param_1 = uVar6;
  return -(uint)(iVar2 == 0);
}
