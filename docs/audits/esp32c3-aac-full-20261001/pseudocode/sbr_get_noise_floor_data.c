/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_get_noise_floor_data @ ram:43013052
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_get_noise_floor_data(int param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int *piVar5;
  undefined1 *puVar6;
  undefined1 *puVar7;
  int iVar8;
  int *piVar9;
  int iVar10;
  int *piVar11;

  gp = &__global_pointer_;
  iVar3 = *(int *)(param_1 + 0x178);
  iVar1 = *(int *)(param_1 + 0xa4);
  if (iVar3 == 2) {
    puVar7 = bookSbrNoiseBalance11T;
    puVar6 = bookSbrEnvBalance11F;
  }
  else {
    puVar7 = bookSbrNoiseLevel11T;
    puVar6 = bookSbrEnvLevel11F;
  }
  uVar4 = (uint)(iVar3 == 2);
  iVar2 = *(int *)(param_1 + 0xb0);
  *(int *)(param_1 + 4) = *(int *)(*(int *)(param_1 + 0x10) * 8 + param_1 + 0x1c) * iVar1;
  if (0 < iVar2) {
    piVar5 = (int *)(param_1 + 0x1108);
    piVar9 = (int *)(param_1 + 0x114);
    iVar8 = 0;
    do {
      if (*piVar9 == 0) {
        if (iVar3 == 2) {
          iVar2 = buf_getbits(param_2,5);
          iVar2 = iVar2 << 1;
        }
        else {
          iVar2 = buf_getbits();
        }
        *piVar5 = iVar2;
        piVar5[10] = 0;
        iVar2 = 1;
        piVar11 = piVar5;
        if (1 < iVar1) {
          do {
            iVar10 = sbr_decode_huff_cw(puVar6,param_2);
            piVar11[0xb] = 0;
            piVar11[1] = iVar10 << uVar4;
            iVar2 = iVar2 + 1;
            piVar11 = piVar11 + 1;
          } while (iVar1 != iVar2);
        }
LAB_ram_430130ec:
        iVar2 = *(int *)(param_1 + 0xb0);
      }
      else {
        iVar10 = 0;
        piVar11 = piVar5;
        if (0 < iVar1) {
          do {
            iVar2 = sbr_decode_huff_cw(puVar7,param_2);
            piVar11[10] = 0;
            *piVar11 = iVar2 << uVar4;
            iVar10 = iVar10 + 1;
            piVar11 = piVar11 + 1;
          } while (iVar1 != iVar10);
          goto LAB_ram_430130ec;
        }
      }
      iVar8 = iVar8 + 1;
      piVar9 = piVar9 + 1;
      piVar5 = piVar5 + iVar1;
    } while (iVar8 < iVar2);
  }
  return;
}
