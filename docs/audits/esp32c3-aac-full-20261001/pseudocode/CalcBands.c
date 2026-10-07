/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: CalcBands @ ram:43013966
 * Types and parameter counts are inferred; verify against disassembly. */

void CalcBands(int *param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;

  gp = &__global_pointer_;
  if (0 < param_4) {
    iVar3 = 1;
    iVar4 = param_2;
    do {
      iVar1 = pv_log2((param_3 << 0x14) / param_2);
      iVar2 = iVar3 << 0x1b;
      iVar3 = iVar3 + 1;
      iVar2 = iVar2 / param_4;
      iVar1 = pv_pow2(((uint)(iVar2 * iVar1) >> 0x14) +
                      (int)((ulonglong)((longlong)iVar2 * (longlong)iVar1) >> 0x20) * 0x1000);
      iVar1 = (int)(((uint)(iVar1 * param_2) >> 0x14) +
                    (int)((ulonglong)((longlong)iVar1 * (longlong)param_2) >> 0x20) * 0x1000 + 0x10)
              >> 5;
      *param_1 = iVar1 - iVar4;
      param_1 = param_1 + 1;
      iVar4 = iVar1;
    } while (iVar3 <= param_4);
    return;
  }
  return;
}
