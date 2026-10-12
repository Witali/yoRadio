/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Executable reconstruction: app/media/assets.c.
 */

// Audit label: application_review; entry: ram:4200c33e; name: jpeg_input_callback_at_4200c33e

int jpeg_input_callback_at_4200c33e(int decoder,int read_buffer,int requested_bytes)

{
  int *flash_read_position;

  flash_read_position = *(int **)(decoder + 0x74);
  if (read_buffer == 0) {
    *flash_read_position = *flash_read_position + requested_bytes;
  }
  else {
    esp_flash_read(0,read_buffer,*flash_read_position,requested_bytes);
    *flash_read_position = *flash_read_position + requested_bytes;
  }
  return requested_bytes;
}

// Audit label: application_review; entry: ram:4200c374; name: jpeg_output_callback_at_4200c374

undefined4 jpeg_output_callback_at_4200c374(int decoder,int decoded_pixels,ushort *output_rectangle)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  void *stripe_buffer;
  uint uVar4;
  int iVar5;
  int iVar6;

  iVar6 = *(int *)(decoder + 0x74);
  uVar1 = (uint)output_rectangle[2];
  iVar5 = *(int *)(iVar6 + 8);
  iVar2 = *(int *)(iVar6 + 4) + ((uVar1 - DAT_ram_3fcc3a65) * iVar5 + (uint)*output_rectangle) * 2;
  uVar4 = (((uint)output_rectangle[1] - (uint)*output_rectangle) + 1) * 0x20000 >> 0x10;
  for (; uVar3 = (uint)output_rectangle[3], uVar1 <= uVar3; uVar1 = uVar1 + 1 & 0xffff) {
    (*(code *)&SUB_ram_4000048c)(iVar2,decoded_pixels,uVar4);
    decoded_pixels = decoded_pixels + uVar4;
    iVar2 = iVar2 + iVar5 * 2;
  }
  if (*(int *)(iVar6 + 8) - 1U <= (uint)output_rectangle[1]) {
    stripe_buffer = *(void **)(iVar6 + 4);
    uVar1 = (iVar2 + uVar4 + iVar5 * -2) - (int)stripe_buffer & 0xffff;
    if ((0x13ff < ((uint)(*(int *)(iVar6 + 8) << 0x14) >> 0x10) + uVar1) ||
       ((uint)DAT_ram_3fcc3a66 <= uVar3 + 1)) {
      if (DAT_ram_3fcc3a6c == '\0') {
        st7789_blit_rectangle_at_4200950e((uint)DAT_ram_3fcc3a5a,
                         (uint)DAT_ram_3fcc3a58 + (uint)DAT_ram_3fcc3a65 & 0xffff,
                         (uint)output_rectangle[1] + (uint)DAT_ram_3fcc3a5a & 0xffff,
                         uVar3 + DAT_ram_3fcc3a58 & 0xffff,stripe_buffer);
      }
      else {
        esp_flash_write(0,stripe_buffer,DAT_ram_3fcc3a5c,uVar1);
        DAT_ram_3fcc3a5c = DAT_ram_3fcc3a5c + uVar1;
      }
      DAT_ram_3fcc3a65 = (char)output_rectangle[3] + 1;
    }
  }
  return 1;
}

// Audit label: application_review; entry: ram:4200c4ac; name: decode_jpeg_at_4200c4ac

void decode_jpeg_at_4200c4ac(void)

{
  int iVar1;
  undefined4 uStack_98;
  undefined *puStack_94;
  uint uStack_90;
  uint uStack_8c;
  undefined1 auStack_88 [28];
  ushort uStack_6c;
  ushort uStack_6a;

  uStack_98 = DAT_ram_3fcc3a60;
  iVar1 = FUN_ram_42011c48(auStack_88,jpeg_input_callback_at_4200c33e,&DAT_ram_3fcba9f8,0xdac,&uStack_98);
  if (iVar1 == 0) {
    puStack_94 = &DAT_ram_3fcbb7a4;
    uStack_90 = (uint)uStack_6c;
    uStack_8c = (uint)uStack_6a;
    DAT_ram_3fcc3a68 = uStack_6c;
    DAT_ram_3fcc3a66 = uStack_6a;
    FUN_ram_42011fd8(auStack_88,jpeg_output_callback_at_4200c374,0);
  }
  return;
}

// Audit label: application_review; entry: ram:4200c518; name: draw_jpeg_at_flash_offset_at_4200c518

void draw_jpeg_at_flash_offset_at_4200c518(undefined2 x,undefined2 y,undefined4 flash_offset)

{
  DAT_ram_3fcc3a65 = 0;
  DAT_ram_3fcc3a64 = 1;
  DAT_ram_3fcc3a6c = 0;
  DAT_ram_3fcc3a58 = y;
  DAT_ram_3fcc3a5a = x;
  DAT_ram_3fcc3a60 = flash_offset;
  (*(code *)&SUB_ram_40000488)(&DAT_ram_3fcbb7a4,0,0x1400);
  decode_jpeg_at_4200c4ac();
  DAT_ram_3fcc3a64 = 0;
  return;
}

// Audit label: application_review; entry: ram:42010eca; name: draw_weather_bmp_at_42010eca

void draw_weather_bmp_at_42010eca(uint param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  void *arg4;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  undefined1 auStack_68 [4];
  uint uStack_64;
  uint uStack_60;
  short sStack_5a;
  short asStack_40 [5];
  int iStack_36;

  esp_flash_read(0,asStack_40,param_3,0xe);
  esp_flash_read(0,auStack_68,param_3 + 0xe,0x28);
  if ((asStack_40[0] == 0x4d42) && (sStack_5a == 0x18)) {
    uVar7 = (uStack_60 ^ (int)uStack_60 >> 0x1f) - ((int)uStack_60 >> 0x1f);
    uVar6 = (uStack_64 + 1) * 3 & 0xfffffffc;
    iVar2 = FUN_ram_4038e4be(uVar6);
    arg4 = (void *)FUN_ram_4038e4be(uStack_64 << 1);
    for (uVar5 = 0; uVar5 < uVar7; uVar5 = uVar5 + 1) {
      uVar3 = uVar5;
      if (0 < (int)uStack_60) {
        uVar3 = (uVar7 - uVar5) - 1;
      }
      esp_flash_read(0,iVar2,uVar3 * uVar6 + iStack_36 + param_3,uVar6);
      for (uVar3 = 0; uVar3 < uStack_64; uVar3 = uVar3 + 1) {
        iVar1 = uVar3 * 3;
        iVar4 = (*(byte *)(iVar1 + 1 + iVar2) & 0xfc) << 3;
        *(ushort *)(uVar3 * 2 + (int)arg4) =
             (ushort)(*(byte *)(iVar1 + 2 + iVar2) & 0xf8) | (ushort)((uint)iVar4 >> 8) |
             ((ushort)iVar4 | (ushort)(*(byte *)(iVar2 + iVar1) >> 3)) << 8;
      }
      uVar3 = param_2 + uVar5 & 0xffff;
      st7789_blit_rectangle_at_4200950e(param_1,uVar3,(param_1 + uStack_64 & 0xffff) - 1 & 0xffff,uVar3,arg4);
    }
    FUN_ram_4038e4da(iVar2);
    FUN_ram_4038e4da(arg4);
  }
  return;
}
