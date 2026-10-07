/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_ele_list @ ram:43007a10
 * Types and parameter counts are inferred; verify against disassembly. */

void get_ele_list(int *param_1,int *param_2,int param_3)

{
  ushort uVar1;
  uint *puVar2;
  ushort *puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;

  gp = &__global_pointer_;
  iVar7 = *param_1;
  if (0 < iVar7) {
    iVar8 = *param_2;
    puVar2 = (uint *)(param_1 + 0x11);
    do {
      while( true ) {
        uVar5 = 0;
        if (param_3 != 0) {
          uVar4 = param_2[1];
          if (uVar4 >> 3 < (uint)param_2[3]) {
            uVar5 = ((uint)*(byte *)(iVar8 + (uVar4 >> 3)) << (uVar4 & 7)) >> 7 & 1;
          }
          param_2[1] = uVar4 + 1;
        }
        puVar2[-0x10] = uVar5;
        uVar4 = param_2[1];
        uVar5 = 0;
        uVar6 = param_2[3] - (uVar4 >> 3);
        puVar3 = (ushort *)((uVar4 >> 3) + iVar8);
        if (1 < uVar6) break;
        if (uVar6 != 1) goto LAB_ram_43007a3c;
        uVar1 = *puVar3;
        param_2[1] = uVar4 + 4;
        iVar7 = iVar7 + -1;
        *puVar2 = (((uint)(byte)uVar1 << 8) << (uVar4 & 7)) >> 0xc & 0xf;
        puVar2 = puVar2 + 1;
        if (iVar7 == 0) {
          gp = &__global_pointer_;
          return;
        }
      }
      uVar1 = *puVar3;
      uVar5 = (((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar4 & 7)) << 0x10) >> 0x1c;
LAB_ram_43007a3c:
      param_2[1] = uVar4 + 4;
      iVar7 = iVar7 + -1;
      *puVar2 = uVar5;
      puVar2 = puVar2 + 1;
    } while (iVar7 != 0);
  }
  return;
}
