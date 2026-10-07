/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: pv_sqrt @ ram:4300e694
 * Types and parameter counts are inferred; verify against disassembly. */

void pv_sqrt(int param_1,uint param_2,aac_analysis_fraction_t *result,
            aac_analysis_sqrt_cache_t *cache)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  int32_t iVar5;
  int iVar6;
  int32_t iVar7;
  undefined1 *puVar8;

  gp = &__global_pointer_;
  if (((cache->input).mantissa == param_1) && ((cache->input).exponent == param_2)) {
    iVar7 = (cache->output).mantissa;
    result->mantissa = iVar7;
    result->exponent = (int)(short)(cache->output).exponent;
    (cache->output).mantissa = iVar7;
    (cache->output).exponent = result->exponent;
    return;
  }
  (cache->input).mantissa = param_1;
  (cache->input).exponent = param_2;
  if (param_1 < 1) {
    result->exponent = 0;
    result->mantissa = 0;
    (cache->output).mantissa = 0;
    (cache->output).exponent = result->exponent;
    return;
  }
  if (param_1 < 0x10000000) {
    for (; iVar3 = param_1, uVar4 = param_2, param_1 < 0x8000000; param_1 = param_1 << 2) {
      iVar3 = param_1 << 1;
      uVar4 = param_2 - 1;
      if (0x7ffffff < iVar3) break;
      param_2 = param_2 - 2;
    }
  }
  else if (param_1 >> 1 < 0x10000001) {
    iVar3 = param_1 >> 1;
    uVar4 = param_2 + 1;
  }
  else if (param_1 >> 2 < 0x10000001) {
    iVar3 = param_1 >> 2;
    uVar4 = param_2 + 2;
  }
  else {
    iVar3 = param_1 >> 3;
    uVar4 = param_2 + 3;
  }
  puVar8 = sqrt_table;
  iVar6 = (int)((ulonglong)((longlong)iVar3 * -0x2367758) >> 0x20) * 0x10 +
          ((uint)(iVar3 * -0x2367758) >> 0x1c);
  do {
    piVar1 = (int *)(puVar8 + 4);
    piVar2 = (int *)(puVar8 + 8);
    puVar8 = puVar8 + 8;
    iVar6 = ((uint)((iVar6 + *piVar1) * iVar3) >> 0x1c) +
            (int)((ulonglong)((longlong)(iVar6 + *piVar1) * (longlong)iVar3) >> 0x20) * 0x10 +
            *piVar2;
    iVar6 = ((uint)(iVar6 * iVar3) >> 0x1c) +
            (int)((ulonglong)((longlong)iVar6 * (longlong)iVar3) >> 0x20) * 0x10;
  } while (puVar8 != (undefined1 *)0x4301c208);
  iVar7 = ((uint)((iVar6 + 0x1dc9e260) * iVar3) >> 0x1c) +
          (int)((ulonglong)((longlong)(iVar6 + 0x1dc9e260) * (longlong)iVar3) >> 0x20) * 0x10 +
          0x2a5826c;
  if ((int)uVar4 < 0) {
    if ((uVar4 & 1) != 0) {
      iVar7 = (int)((ulonglong)((longlong)iVar7 * 0xb504f30) >> 0x20) * 0x10 +
              ((uint)(iVar7 * 0xb504f30) >> 0x1c);
    }
    iVar5 = -0x1d - ((int)-uVar4 >> 1);
  }
  else {
    iVar5 = ((int)uVar4 >> 1) + -0x1d;
    if ((uVar4 & 1) != 0) {
      iVar5 = ((int)uVar4 >> 1) + -0x1c;
      iVar7 = (int)((ulonglong)((longlong)iVar7 * 0x16a09e60) >> 0x20) * 8 +
              ((uint)(iVar7 * 0x16a09e60) >> 0x1d);
    }
  }
  result->exponent = iVar5;
  result->mantissa = iVar7;
  (cache->output).mantissa = iVar7;
  (cache->output).exponent = result->exponent;
  return;
}
