/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: huffdecode @ ram:43009192
 * Types and parameter counts are inferred; verify against disassembly. */

int huffdecode(uint param_1,int *param_2,int param_3,int *param_4)

{
  byte bVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  uint uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  int iVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  int iVar13;

  gp = &__global_pointer_;
  iVar10 = param_2[1];
  uVar7 = iVar10 + 4;
  param_2[1] = uVar7;
  uVar4 = *(uint *)(param_3 + 200);
  if (param_1 == 1) {
    if (uVar7 >> 3 < (uint)param_2[3]) {
      bVar1 = *(byte *)(*param_2 + (uVar7 >> 3));
      param_2[1] = iVar10 + 5;
      if (uVar4 != 1) {
        if (*(int *)(param_3 + 0xac) == 0) {
          return 1;
        }
        *(undefined4 *)(param_3 + 200) = 1;
        *(undefined4 *)(param_3 + 0x8c) = 2;
      }
      iVar2 = *param_4;
      uVar4 = ((uint)bVar1 << (uVar7 & 7)) >> 7 & 1;
      iVar10 = *(int *)(iVar2 + 0x2484);
      if (uVar4 != 0) {
        iVar13 = *(int *)(param_4[1] + 0x2484);
        puVar3 = (undefined4 *)(iVar10 + 0x8ac);
        iVar2 = get_ics_info(param_2,1,iVar2 + 0x24a8,iVar2 + 0x24b0,puVar3,iVar10 + 0xacc,
                             param_3 + 0x78,iVar10 + 0xad0,iVar13 + 0xad0);
        if (iVar2 != 0) {
          return iVar2;
        }
        iVar2 = param_4[1];
        uVar5 = *(undefined4 *)(*param_4 + 0x24b0);
        uVar8 = *(undefined4 *)(iVar10 + 0xacc);
        *(undefined4 *)(iVar2 + 0x24a8) = *(undefined4 *)(*param_4 + 0x24a8);
        *(undefined4 *)(iVar2 + 0x24b0) = uVar5;
        *(undefined4 *)(iVar13 + 0xacc) = uVar8;
        uVar5 = *(undefined4 *)(iVar10 + 0x8b8);
        uVar8 = *(undefined4 *)(iVar10 + 0x8bc);
        uVar6 = *(undefined4 *)(iVar10 + 0x8c0);
        uVar9 = *(undefined4 *)(iVar10 + 0x8c4);
        uVar12 = *puVar3;
        uVar11 = *(undefined4 *)(iVar10 + 0x8b0);
        *(undefined4 *)(iVar13 + 0x8b4) = *(undefined4 *)(iVar10 + 0x8b4);
        *(undefined4 *)(iVar13 + 0x8b8) = uVar5;
        *(undefined4 *)(iVar13 + 0x8bc) = uVar8;
        *(undefined4 *)(iVar13 + 0x8ac) = uVar12;
        *(undefined4 *)(iVar13 + 0x8b0) = uVar11;
        *(undefined4 *)(iVar13 + 0x8c0) = uVar6;
        *(undefined4 *)(iVar13 + 0x8c4) = uVar9;
        *(undefined4 *)(iVar13 + 0x8c8) = *(undefined4 *)(iVar10 + 0x8c8);
        iVar10 = getmask(*(undefined4 *)(*(int *)(*param_4 + 0x24a8) * 4 + param_3 + 0x78),param_2,
                         puVar3,*(undefined4 *)(iVar10 + 0xacc),*(undefined4 *)(param_3 + 0x8a6c));
        *(int *)(param_3 + 0x8a70) = iVar10;
        if (iVar10 == 3) {
          return 1;
        }
        uVar7 = 2;
        iVar10 = *(int *)(*param_4 + 0x2484);
        goto LAB_ram_430091fc;
      }
    }
    else {
      param_2[1] = iVar10 + 5;
      if (uVar4 == 1) {
        iVar10 = *(int *)(*param_4 + 0x2484);
      }
      else {
        if (*(int *)(param_3 + 0xac) == 0) {
          return 1;
        }
        iVar10 = *(int *)(*param_4 + 0x2484);
        *(undefined4 *)(param_3 + 200) = 1;
        *(undefined4 *)(param_3 + 0x8c) = 2;
      }
    }
    *(undefined4 *)(param_3 + 0x8a70) = 0;
    uVar4 = 0;
    uVar7 = 2;
  }
  else {
    if (uVar4 != param_1) {
      if (*(int *)(param_3 + 0xac) == 0) {
        return 1;
      }
      *(uint *)(param_3 + 200) = param_1 & 1;
      *(uint *)(param_3 + 0x8c) = (param_1 & 1) + 1;
      uVar4 = param_1;
    }
    if (uVar4 != 0) {
      return 0;
    }
    iVar10 = *(int *)(*param_4 + 0x2484);
    *(undefined4 *)(param_3 + 0x8a70) = 0;
    uVar4 = 0;
    uVar7 = 1;
  }
LAB_ram_430091fc:
  iVar2 = 0;
  while( true ) {
    iVar10 = getics(param_2,uVar4,param_3,*param_4,iVar10 + 0x8ac,iVar10 + 0xacc,iVar10 + 0x6ac,
                    iVar10,param_3 + 0x78,*(int *)(param_3 + 0x8a78) + 0xc08,
                    *(int *)(param_3 + 0x8a78) + 0x800);
    param_4 = param_4 + 1;
    if ((uVar7 <= iVar2 + 1U) || (iVar10 != 0)) break;
    iVar2 = 1;
    iVar10 = *(int *)(*param_4 + 0x2484);
  }
  return iVar10;
}
