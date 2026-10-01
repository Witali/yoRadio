/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: q_normalize @ ram:4300fb2a
 * Types and parameter counts are inferred; verify against disassembly. */

int q_normalize(int *param_1,int param_2,uint *param_3,uint *param_4)

{
  uint uVar1;
  uint *puVar2;
  int *piVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  uint *puVar7;
  uint uVar8;
  int iVar9;
  uint *puVar10;
  uint *puVar11;
  int iVar12;
  int *piVar13;
  uint uVar14;
  int iVar15;
  uint uVar16;
  int iVar17;
  int iVar18;
  short *psVar19;

  gp = &__global_pointer_;
  iVar12 = *(int *)(param_2 + 4);
  if (iVar12 == 0) {
    iVar17 = 1000;
  }
  else {
    puVar2 = (uint *)(param_2 + 0x30);
    iVar17 = 1000;
    piVar3 = param_1;
    puVar7 = puVar2;
    iVar15 = iVar12;
    do {
      uVar8 = *puVar7;
      if (0x80 < uVar8) break;
      puVar7 = puVar7 + 1;
      piVar13 = piVar3;
      if (uVar8 != 0) {
        do {
          iVar9 = *piVar13;
          piVar13 = piVar13 + 1;
          if (iVar9 < iVar17) {
            iVar17 = iVar9;
          }
        } while (piVar3 + uVar8 != piVar13);
        piVar3 = piVar3 + uVar8;
      }
      iVar15 = iVar15 + -1;
    } while (iVar15 != 0);
    iVar15 = 0;
    if (0 < iVar12) {
      do {
        uVar8 = *puVar2;
        if (0x80 < uVar8) {
          return iVar17;
        }
        if (uVar8 != 0) {
          psVar19 = (short *)puVar2[0x10];
          uVar16 = 0;
          iVar9 = 0;
          piVar3 = param_1;
          do {
            while( true ) {
              iVar18 = (int)*psVar19;
              param_1 = piVar3 + 1;
              iVar5 = iVar18 - iVar9;
              if (iVar5 < 2) goto LAB_ram_4300fc7a;
              psVar19 = psVar19 + 1;
              uVar1 = *piVar3 - iVar17;
              iVar6 = iVar5 >> 1;
              iVar9 = iVar18;
              if (*piVar3 != iVar17) break;
              uVar4 = *param_4;
              uVar1 = param_4[1];
              puVar7 = param_4 + 2;
              if (iVar6 != 1) {
                puVar10 = puVar7;
                do {
                  uVar14 = (int)uVar4 >> 0x1f ^ uVar4;
                  uVar4 = *puVar10;
                  puVar11 = puVar10 + 2;
                  uVar16 = uVar16 | uVar14 | (int)uVar1 >> 0x1f ^ uVar1;
                  uVar1 = puVar10[1];
                  puVar10 = puVar11;
                } while (param_4 + iVar6 * 2 != puVar11);
                puVar7 = puVar7 + iVar6 * 2 + -2;
              }
              uVar16 = uVar16 | (int)uVar4 >> 0x1f ^ uVar4 | (int)uVar1 >> 0x1f ^ uVar1;
              param_4 = puVar7;
LAB_ram_4300fbcc:
              *param_3 = uVar16;
              uVar8 = uVar8 - 1;
              piVar3 = param_1;
              if (uVar8 == 0) goto LAB_ram_4300fc7a;
            }
            if (0x1e < (int)uVar1) {
              iVar18 = memset(param_4,0,iVar5 * 4);
              param_4 = (uint *)(iVar18 + iVar5 * 4);
              goto LAB_ram_4300fbcc;
            }
            uVar14 = (int)*param_4 >> (uVar1 & 0x1f);
            uVar4 = (int)param_4[1] >> (uVar1 & 0x1f);
            if (iVar6 != 1) {
              puVar7 = param_4;
              do {
                *puVar7 = uVar14;
                puVar10 = puVar7 + 2;
                puVar7[1] = uVar4;
                uVar16 = uVar16 | (int)uVar14 >> 0x1f ^ uVar14 | (int)uVar4 >> 0x1f ^ uVar4;
                uVar14 = (int)puVar7[2] >> (uVar1 & 0x1f);
                uVar4 = (int)puVar7[3] >> (uVar1 & 0x1f);
                puVar7 = puVar10;
              } while (param_4 + (iVar6 + -1) * 2 != puVar10);
              param_4 = param_4 + (iVar6 + -2) * 2 + 2;
            }
            *param_4 = uVar14;
            param_4[1] = uVar4;
            uVar16 = uVar16 | (int)uVar14 >> 0x1f ^ uVar14 | (int)uVar4 >> 0x1f ^ uVar4;
            *param_3 = uVar16;
            uVar8 = uVar8 - 1;
            param_4 = param_4 + 2;
            piVar3 = param_1;
          } while (uVar8 != 0);
        }
LAB_ram_4300fc7a:
        iVar15 = iVar15 + 1;
        param_3 = param_3 + 1;
        puVar2 = puVar2 + 1;
      } while (iVar12 != iVar15);
    }
  }
  return iVar17;
}
