/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: mix_radix_fft @ ram:4300b770
 * Types and parameter counts are inferred; verify against disassembly. */

uint mix_radix_fft(int *param_1,uint *param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int *piVar11;
  uint *puVar12;
  uint uStack_28;
  uint uStack_24;

  gp = &__global_pointer_;
  uStack_28 = *param_2;
  iVar4 = pv_normalize(uStack_28);
  uVar1 = 4;
  if (iVar4 < 5) {
    uVar2 = 4 - iVar4;
    uVar1 = 8 - iVar4;
  }
  else {
    uVar2 = 0;
  }
  iVar8 = param_1[0x100];
  iVar6 = param_1[0x101];
  param_1[0x100] = iVar8 + param_1[0x300] >> (uVar1 & 0x1f);
  iVar4 = param_1[0x301];
  param_1[0x301] = -(iVar8 - param_1[0x300] >> (uVar1 & 0x1f));
  param_1[0x101] = iVar6 + iVar4 >> (uVar1 & 0x1f);
  param_1[0x300] = iVar6 - iVar4 >> (uVar1 & 0x1f);
  iVar4 = *param_1;
  iVar6 = param_1[1];
  *param_1 = iVar4 + param_1[0x200] >> (uVar1 & 0x1f);
  param_1[1] = param_1[0x201] + iVar6 >> (uVar1 & 0x1f);
  param_1[0x200] = iVar4 - param_1[0x200] >> (uVar1 & 0x1f);
  param_1[0x201] = iVar6 - param_1[0x201] >> (uVar1 & 0x1f);
  iVar6 = param_1[0x302];
  iVar4 = param_1[0x102];
  puVar12 = &w_512rx2;
  piVar11 = param_1 + 0x202;
  do {
    piVar11[-0x100] = iVar4 + iVar6 >> (uVar1 & 0x1f);
    uVar3 = *puVar12 & 0xffff0000;
    iVar8 = iVar4 - iVar6 >> (uVar2 & 0x1f);
    iVar7 = *puVar12 << 0x10;
    iVar9 = piVar11[-0xff] - piVar11[0x101] >> (uVar2 & 0x1f);
    iVar10 = piVar11[-0x200] - *piVar11 >> (uVar2 & 0x1f);
    iVar5 = piVar11[-0x1ff] - piVar11[1] >> (uVar2 & 0x1f);
    piVar11[-0xff] = piVar11[-0xff] + piVar11[0x101] >> (uVar1 & 0x1f);
    piVar11[-0x1ff] = piVar11[1] + piVar11[-0x1ff] >> (uVar1 & 0x1f);
    piVar11[-0x200] = piVar11[-0x200] + *piVar11 >> (uVar1 & 0x1f);
    puVar12 = puVar12 + 1;
    iVar4 = piVar11[-0xfe];
    piVar11[0x101] =
         -((int)((ulonglong)((longlong)iVar8 * (longlong)(int)uVar3) >> 0x20) +
          (int)((ulonglong)((longlong)iVar9 * (longlong)iVar7) >> 0x20)) >> 3;
    iVar6 = piVar11[0x102];
    *piVar11 = (int)((ulonglong)((longlong)iVar10 * (longlong)(int)uVar3) >> 0x20) +
               (int)((ulonglong)((longlong)iVar5 * (longlong)iVar7) >> 0x20) >> 3;
    piVar11[0x100] =
         (int)((ulonglong)((longlong)(int)uVar3 * (longlong)iVar9) >> 0x20) +
         (int)((ulonglong)((longlong)-iVar8 * (longlong)iVar7) >> 0x20) >> 3;
    piVar11[1] = (int)((ulonglong)((longlong)iVar5 * (longlong)(int)uVar3) >> 0x20) +
                 (int)((ulonglong)((longlong)-iVar10 * (longlong)iVar7) >> 0x20) >> 3;
    piVar11 = piVar11 + 2;
  } while (puVar12 != &W_256rx4);
  fft_rx4_long(param_1,&uStack_28);
  fft_rx4_long(param_1 + 0x200,&uStack_24);
  digit_reversal_swapping(param_1,param_1 + 0x200);
  *param_2 = uStack_28 | uStack_24;
  return uVar1;
}
