/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: check_crc @ ram:42056780
 * Types and parameter counts are inferred; verify against disassembly. */

void check_crc(ushort *param_1,uint param_2,int param_3)

{
  int iVar1;
  uint uVar2;
  ushort uVar3;
  ushort uVar4;

  gp = &__global_pointer_;
  if (param_3 < 1) {
    return;
  }
  uVar2 = 1 << (param_3 - 1U & 0x1f);
  uVar3 = *param_1;
  iVar1 = 0;
  do {
    uVar4 = param_1[1] & uVar3;
    uVar3 = uVar3 << 1;
    if (uVar4 == 0) {
      if ((uVar2 & param_2) != 0) {
LAB_ram_4205679e:
        uVar3 = uVar3 ^ param_1[2];
      }
    }
    else if ((uVar2 & param_2) == 0) goto LAB_ram_4205679e;
    uVar2 = uVar2 >> 1;
    iVar1 = iVar1 + 1;
    if (param_3 == iVar1) {
      *param_1 = uVar3;
      return;
    }
  } while( true );
}
