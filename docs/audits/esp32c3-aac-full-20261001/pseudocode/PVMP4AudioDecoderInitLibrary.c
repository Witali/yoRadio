/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: PVMP4AudioDecoderInitLibrary @ ram:4300f5ee
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4
PVMP4AudioDecoderInitLibrary
          (int param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;

  gp = &__global_pointer_;
  memset(param_2,0,0x8a84);
  *(int *)(param_2 + 0x2570) = param_2 + 0x4a58;
  *(int *)(param_2 + 0x4a24) = param_2 + 0x6a58;
  *(int *)(param_2 + 0x2574) = param_2 + 0x5a58;
  *(int *)(param_2 + 0x4a28) = param_2 + 0x7a58;
  *(int *)(param_2 + 0x8a6c) = param_2 + 0x6770;
  iVar1 = media_lib_module_calloc("AUD_Codec",1,0x35c);
  *(int *)(param_2 + 0x2c) = iVar1;
  if (iVar1 != 0) {
    iVar1 = media_lib_module_calloc("AUD_Codec",1,0x2b8);
    *(int *)(param_2 + 0x70) = iVar1;
    if (iVar1 != 0) {
      iVar1 = media_lib_module_calloc("AUD_Codec",1,0x2b8);
      *(int *)(param_2 + 0x74) = iVar1;
      if (iVar1 != 0) {
        iVar1 = *(int *)(param_1 + 0x1c);
        *(bool *)(param_2 + 8) = iVar1 != 0;
        *(bool *)(param_2 + 0x8a80) = iVar1 != 0;
        if (iVar1 != 0) {
          iVar1 = media_lib_module_calloc("AUD_Codec",1,0x414);
          *(int *)(param_2 + 0x8a60) = iVar1;
          if (iVar1 == 0) {
            return 10;
          }
        }
        iVar1 = media_lib_module_calloc("AUD_Codec",1,0x3000);
        *(int *)(param_2 + 0x8a7c) = iVar1;
        if (iVar1 != 0) {
          *(int *)(param_2 + 0x8a74) = iVar1;
          *(int *)(param_2 + 0x8a78) = iVar1 + 0x1000;
          *(undefined4 *)(*(int *)(param_2 + 0x2c) + 0x348) = param_3;
          uVar3 = *(undefined4 *)(param_2 + 0x70);
          uVar2 = *(undefined4 *)(param_2 + 0x74);
          *(undefined4 *)(param_1 + 0x14) = 0;
          *(undefined4 *)(param_2 + 0xc) = 0xffffffff;
          *(undefined4 *)(param_2 + 0x78) = uVar3;
          *(undefined4 *)(param_2 + 0x7c) = uVar3;
          *(undefined4 *)(param_2 + 0x84) = uVar3;
          *(undefined4 *)(param_2 + 0x80) = uVar2;
          *(undefined4 *)(param_2 + 0x10) = 0x400;
          *(undefined4 *)(param_2 + 0xa8) = 4;
          *(undefined4 *)(param_2 + 0xac) = 1;
          infoinit(4,param_2 + 0x78,param_2 + 0x30);
          iVar1 = *(int *)(param_2 + 0x2c);
          *(undefined4 *)(param_1 + 0x34) = 0;
          *(undefined4 *)(param_1 + 0x38) = 0;
          iVar1 = *(int *)(iVar1 + 0x348);
          *(undefined4 *)(param_1 + 0x30) = 0;
          *(undefined4 *)(param_1 + 0x18) = 1;
          *(undefined4 *)(param_1 + 0x28) = 0;
          if ((iVar1 != 0) ||
             (iVar1 = raw_stream_parameter_setup(param_4,param_5,param_2), iVar1 == 0)) {
            gp = &__global_pointer_;
            return 0;
          }
        }
      }
    }
  }
  return 10;
}
