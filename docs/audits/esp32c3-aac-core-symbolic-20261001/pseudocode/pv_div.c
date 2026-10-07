/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: pv_div @ ram:4300e336
 * Types and parameter counts are inferred; verify against disassembly. */

void pv_div(int param_1,int param_2,aac_analysis_fraction_t *result)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;

  gp = &__global_pointer_;
  result->exponent = 0;
  if (param_2 != 0) {
    bVar1 = param_2 < 0;
    if (bVar1) {
      param_2 = -param_2;
    }
    if (param_1 < 0) {
      param_1 = -param_1;
      bVar1 = !bVar1;
    }
    else if (param_1 == 0) goto LAB_ram_4300e33c;
    uVar2 = pv_normalize(param_1);
    uVar3 = pv_normalize(param_2);
    iVar4 = param_2 << (uVar3 & 0x1f);
    iVar5 = 0x40000000 / (iVar4 >> 0xf);
    result->exponent = uVar2 - uVar3;
    iVar4 = 0x7fffffff -
            (((uint)(iVar4 * iVar5) >> 0xf) +
            (int)((ulonglong)((longlong)iVar4 * (longlong)iVar5) >> 0x20) * 0x20000);
    iVar5 = (int)((ulonglong)
                  ((longlong)(param_1 << (uVar2 & 0x1f)) *
                  (longlong)
                  (int)(((uint)(iVar5 * iVar4) >> 0xe) +
                       (int)((ulonglong)((longlong)iVar5 * (longlong)iVar4) >> 0x20) * 0x40000)) >>
                 0x20);
    iVar4 = iVar5 * 2;
    if (bVar1) {
      iVar4 = iVar5 * -2;
    }
    result->mantissa = iVar4;
    return;
  }
LAB_ram_4300e33c:
  result->mantissa = 0;
  return;
}
