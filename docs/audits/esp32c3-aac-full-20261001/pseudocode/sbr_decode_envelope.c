/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_decode_envelope @ ram:43011572
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_decode_envelope(int param_1)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int *piVar6;
  int *piVar7;
  int iVar8;
  int *piVar9;
  int iVar10;
  int *piVar11;
  int *piVar12;
  int iVar13;
  int *piVar14;

  gp = &__global_pointer_;
  iVar5 = *(int *)(param_1 + 0x10);
  if (iVar5 < 1) {
    return;
  }
  iVar1 = *(int *)(param_1 + 0xa8);
  piVar2 = (int *)(param_1 + 0x1020);
  piVar6 = (int *)(param_1 + 0x710);
  piVar9 = (int *)(param_1 + 0x100);
  iVar8 = 0;
  do {
    while( true ) {
      iVar10 = *(int *)((iVar8 + iVar5) * 4 + param_1 + 0x18);
      iVar13 = *(int *)(iVar10 * 4 + param_1 + 0x9c);
      if (*piVar9 != 0) break;
      if (iVar10 == 0) {
        mapLowResEnergyVal_part_0(*piVar6,piVar2,iVar1);
      }
      else {
        *(int *)(param_1 + 0x1020) = *piVar6;
      }
      piVar7 = piVar6 + 1;
      if (iVar13 < 2) goto LAB_ram_4301165e;
      piVar12 = (int *)(param_1 + 0x1024);
      iVar5 = 1;
      do {
        while( true ) {
          iVar3 = *piVar7 + piVar7[-1];
          *piVar7 = iVar3;
          if (iVar10 == 0) break;
          *piVar12 = iVar3;
          iVar5 = iVar5 + 1;
          piVar7 = piVar7 + 1;
          piVar12 = piVar12 + 1;
          if (iVar13 == iVar5) goto LAB_ram_43011700;
        }
        iVar4 = iVar5 + 1;
        mapLowResEnergyVal_part_0(iVar3,piVar2,iVar1,iVar5);
        piVar7 = piVar7 + 1;
        piVar12 = piVar12 + 1;
        iVar5 = iVar4;
      } while (iVar13 != iVar4);
LAB_ram_43011700:
      iVar5 = *(int *)(param_1 + 0x10);
      iVar8 = iVar8 + 1;
      piVar6 = piVar6 + iVar13;
      piVar9 = piVar9 + 1;
      if (iVar5 <= iVar8) {
        return;
      }
    }
    if (0 < iVar13) {
      piVar7 = piVar2 + -iVar1;
      piVar12 = piVar2;
      piVar11 = piVar2;
      iVar5 = 0;
      piVar14 = piVar6;
      do {
        while (iVar3 = *piVar14, iVar10 != 0) {
          iVar4 = *piVar12;
          iVar5 = iVar5 + 1;
          *piVar14 = iVar3 + iVar4;
          *piVar12 = iVar3 + iVar4;
          piVar11 = piVar11 + 3;
          piVar12 = piVar12 + 1;
          piVar7 = piVar7 + 2;
          piVar14 = piVar14 + 1;
          if (iVar13 == iVar5) goto LAB_ram_43011658;
        }
        if (iVar1 < 0) {
          if (-iVar1 <= iVar5) goto LAB_ram_43011688;
          iVar3 = iVar3 + *piVar11;
        }
        else if (iVar5 < iVar1) {
          iVar3 = iVar3 + *piVar12;
        }
        else {
LAB_ram_43011688:
          iVar3 = iVar3 + *piVar7;
        }
        *piVar14 = iVar3;
        iVar4 = iVar5 + 1;
        mapLowResEnergyVal_part_0(iVar3,piVar2,iVar1,iVar5);
        piVar14 = piVar14 + 1;
        piVar12 = piVar12 + 1;
        piVar11 = piVar11 + 3;
        piVar7 = piVar7 + 2;
        iVar5 = iVar4;
      } while (iVar13 != iVar4);
LAB_ram_43011658:
      piVar7 = piVar6 + iVar13;
LAB_ram_4301165e:
      iVar5 = *(int *)(param_1 + 0x10);
      piVar6 = piVar7;
    }
    iVar8 = iVar8 + 1;
    piVar9 = piVar9 + 1;
    if (iVar5 <= iVar8) {
      return;
    }
  } while( true );
}
