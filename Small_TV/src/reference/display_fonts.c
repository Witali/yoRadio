/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Executable reconstruction: app/display/st7789.c.
 */

// Audit label: application_review; entry: ram:4200a5be; name: draw_glyph_with_background_at_4200a5be

void draw_glyph_with_background_at_4200a5be(uint param_1,uint param_2,int param_3,uint param_4,undefined4 param_5,
                     undefined4 param_6)

{
  uint uVar1;
  byte bVar2;
  byte bVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  undefined1 *puVar7;
  byte bVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;

  if (param_4 == 0x28) {
    uVar12 = 0x14;
    uVar11 = 0x28;
  }
  else if (param_4 < 0x29) {
    if (param_4 == 0x18) {
      uVar12 = 0xc;
      uVar11 = 0x18;
    }
    else if (param_4 == 0x20) {
      uVar12 = 0x10;
      uVar11 = 0x20;
    }
    else {
      uVar12 = 8;
      uVar11 = 0x10;
    }
  }
  else if (param_4 == 0x40) {
    uVar12 = 0x20;
    uVar11 = 0x40;
  }
  else if (param_4 == 0x50) {
    uVar12 = 0x28;
    uVar11 = 0x50;
  }
  else {
    uVar12 = 8;
    uVar11 = 0x10;
  }
  uVar9 = uVar12 >> 3;
  if ((uVar12 & 7) != 0) {
    uVar9 = uVar9 + 1;
  }
  if (param_4 == 0x50) {
    uVar6 = param_3 - 0x30U & 0xffff;
  }
  else if (param_4 == 0x40) {
    uVar6 = param_3 - 0x30U & 0xffff;
  }
  else if (param_4 == 0x28) {
    uVar6 = param_3 - 0x30U & 0xffff;
  }
  else {
    uVar6 = param_3 - 0x20U & 0xffff;
  }
  uVar10 = uVar6 * uVar11 * uVar9 & 0xffff;
  (*(code *)&SUB_ram_40000488)(&glyph_pixel_buffer_at_3fcb7da8,0,0x2800);
  uVar6 = 0;
  puVar7 = &glyph_pixel_buffer_at_3fcb7da8;
  do {
    if (uVar11 <= uVar6) {
      st7789_blit_rectangle_at_4200950e(param_1,param_2,(uVar12 + param_1 & 0xffff) - 1 & 0xffff,
                       (uVar11 + param_2 & 0xffff) - 1 & 0xffff,&glyph_pixel_buffer_at_3fcb7da8);
      return;
    }
    uVar4 = uVar12;
    for (uVar1 = 0; uVar1 < uVar9; uVar1 = uVar1 + 1 & 0xff) {
      if (param_4 == 0x18) {
        bVar2 = (&UNK_ram_3c0ec3e4)[uVar6 * uVar9 + uVar1 + uVar10];
      }
      else if (param_4 == 0x20) {
        bVar2 = (&UNK_ram_3c0ed5e4)[uVar6 * uVar9 + uVar1 + uVar10];
      }
      else if (param_4 == 0x50) {
        bVar2 = (&UNK_ram_3c0eacb4)[uVar6 * uVar9 + uVar1 + uVar10];
      }
      else if (param_4 == 0x40) {
        bVar2 = (&UNK_ram_3c0e9d04)[uVar6 * uVar9 + uVar1 + uVar10];
      }
      else if (param_4 == 0x28) {
        bVar2 = (&UNK_ram_3c0ea804)[uVar6 * uVar9 + uVar1 + uVar10];
      }
      else {
        bVar2 = (&DAT_ram_3c0ebde4)[uVar6 * uVar9 + uVar1 + uVar10];
      }
      bVar3 = 1;
      for (bVar8 = 0; bVar8 < 8; bVar8 = bVar8 + 1) {
        if ((bVar2 & bVar3) == 0) {
          *puVar7 = (char)((uint)param_6 >> 8);
          puVar7[1] = (char)param_6;
        }
        else {
          *puVar7 = (char)((uint)param_5 >> 8);
          puVar7[1] = (char)param_5;
        }
        puVar7 = puVar7 + 2;
        bVar3 = bVar3 << 1;
        uVar5 = uVar4 - 1;
        uVar4 = uVar5 & 0xffff;
        if ((uVar5 & 0xffff) == 0) break;
      }
    }
    uVar6 = uVar6 + 1 & 0xff;
  } while( true );
}

// Audit label: application_review; entry: ram:4200a81e; name: draw_glyph_transparent_at_4200a81e

void draw_glyph_transparent_at_4200a81e(uint param_1,uint param_2,int param_3,uint param_4,ushort param_5)

{
  byte bVar1;
  byte bVar2;
  uint uVar3;
  uint uVar4;
  uint arg0;
  uint uVar5;
  byte bVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uStack_4c;
  uint uStack_48;

  if (param_4 == 0x28) {
    uStack_48 = 0x14;
    uStack_4c = 0x28;
  }
  else if (param_4 < 0x29) {
    if (param_4 == 0x18) {
      uStack_48 = 0xc;
      uStack_4c = 0x18;
    }
    else if (param_4 == 0x20) {
      uStack_48 = 0x10;
      uStack_4c = 0x20;
    }
    else {
      uStack_48 = 8;
      uStack_4c = 0x10;
    }
  }
  else if (param_4 == 0x50) {
    uStack_48 = 0x28;
    uStack_4c = 0x50;
  }
  else {
    uStack_48 = 8;
    uStack_4c = 0x10;
  }
  uVar8 = uStack_48 >> 3;
  if ((uStack_48 & 7) != 0) {
    uVar8 = uVar8 + 1;
  }
  if (param_4 == 0x50) {
    uVar3 = param_3 - 0x30U & 0xffff;
  }
  else if (param_4 == 0x28) {
    uVar3 = param_3 - 0x30U & 0xffff;
  }
  else {
    uVar3 = param_3 - 0x20U & 0xffff;
  }
  uVar9 = uVar3 * uStack_4c * uVar8 & 0xffff;
  uVar3 = 0;
  do {
    if (uStack_4c <= uVar3) {
      return;
    }
    arg0 = param_1;
    uVar5 = uStack_48;
    for (uVar7 = 0; uVar7 < uVar8; uVar7 = uVar7 + 1 & 0xff) {
      if (param_4 == 0x18) {
        bVar6 = (&UNK_ram_3c0ec3e4)[uVar3 * uVar8 + uVar7 + uVar9];
      }
      else if (param_4 == 0x20) {
        bVar6 = (&UNK_ram_3c0ed5e4)[uVar3 * uVar8 + uVar7 + uVar9];
      }
      else if (param_4 == 0x50) {
        bVar6 = (&UNK_ram_3c0eacb4)[uVar3 * uVar8 + uVar7 + uVar9];
      }
      else if (param_4 == 0x28) {
        bVar6 = (&UNK_ram_3c0ea804)[uVar3 * uVar8 + uVar7 + uVar9];
      }
      else {
        bVar6 = (&DAT_ram_3c0ebde4)[uVar3 * uVar8 + uVar7 + uVar9];
      }
      bVar1 = 1;
      for (bVar2 = 0; bVar2 < 8; bVar2 = bVar2 + 1) {
        if ((bVar6 & bVar1) != 0) {
          st7789_draw_pixel_at_4200958a(arg0,param_2,param_5);
        }
        arg0 = arg0 + 1 & 0xffff;
        bVar1 = bVar1 << 1;
        uVar4 = uVar5 - 1;
        uVar5 = uVar4 & 0xffff;
        if ((uVar4 & 0xffff) == 0) break;
      }
    }
    param_2 = param_2 + 1 & 0xffff;
    uVar3 = uVar3 + 1 & 0xff;
  } while( true );
}

// Audit label: application_review; entry: ram:4200aa1e; name: draw_encoded_text_at_4200aa1e

void draw_encoded_text_at_4200aa1e(uint param_1,undefined4 param_2,byte *param_3,uint param_4,undefined4 param_5)

{
  ushort uVar1;
  ushort uVar2;
  byte *pbVar3;

  uVar2 = (*(code *)&SUB_ram_400004a8)(param_3);
  if (uVar2 != 0) {
    for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1) {
      pbVar3 = param_3 + 1;
      if (*param_3 < 0x81) {
        draw_glyph_transparent_at_4200a81e(param_1,param_2,*param_3,param_4,param_5);
        param_1 = param_1 + (param_4 >> 1 & 0xff) & 0xffff;
        if (param_4 == 0x10) {
          param_1 = param_1 - 3 & 0xffff;
        }
      }
      else {
        pbVar3 = param_3 + 2;
        uVar1 = uVar1 + 1;
        draw_glyph_transparent_at_4200a81e(param_1,param_2,param_3[1],param_4,param_5);
        param_1 = param_1 + param_4 & 0xffff;
      }
      param_3 = pbVar3;
    }
  }
  return;
}

// Audit label: application_review; entry: ram:4200aae0; name: draw_large_digit_at_4200aae0

void draw_large_digit_at_4200aae0(uint param_1,uint param_2,int param_3,undefined4 param_4,undefined4 param_5,
                     undefined4 param_6)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  byte bVar4;
  byte bVar5;
  undefined1 *puVar6;
  short sVar7;
  int iVar8;

  if (param_3 == 0xa1e6) {
    iVar8 = 0;
  }
  else if (param_3 == 0xa848) {
    iVar8 = 0x48;
  }
  else {
    iVar8 = 0;
  }
  (*(code *)&SUB_ram_40000488)(&glyph_pixel_buffer_at_3fcb7da8,0,0x2800);
  uVar2 = 0;
  puVar6 = &glyph_pixel_buffer_at_3fcb7da8;
  do {
    if (0x17 < uVar2) {
      st7789_blit_rectangle_at_4200950e(param_1,param_2,param_1 + 0x17 & 0xffff,param_2 + 0x17 & 0xffff,
                       &glyph_pixel_buffer_at_3fcb7da8);
      return;
    }
    sVar7 = 0x18;
    for (uVar3 = 0; uVar3 < 3; uVar3 = uVar3 + 1 & 0xff) {
      bVar1 = (&DAT_ram_3c0e9c74)[uVar2 * 3 + uVar3 + iVar8];
      bVar5 = 1;
      for (bVar4 = 0; bVar4 < 8; bVar4 = bVar4 + 1) {
        if ((bVar5 & bVar1) == 0) {
          *puVar6 = (char)((uint)param_6 >> 8);
          puVar6[1] = (char)param_6;
        }
        else {
          *puVar6 = (char)((uint)param_5 >> 8);
          puVar6[1] = (char)param_5;
        }
        puVar6 = puVar6 + 2;
        bVar5 = bVar5 << 1;
        sVar7 = sVar7 + -1;
        if (sVar7 == 0) break;
      }
    }
    uVar2 = uVar2 + 1 & 0xff;
  } while( true );
}

// Audit label: application_review; entry: ram:4200abee; name: draw_ascii_text_at_4200abee

void draw_ascii_text_at_4200abee(uint param_1,undefined4 param_2,byte *param_3,uint param_4,undefined4 param_5,
                     undefined4 param_6)

{
  byte bVar1;
  ushort uVar2;
  ushort uVar3;
  uint uVar4;
  byte *pbVar5;

  uVar3 = (*(code *)&SUB_ram_400004a8)(param_3);
  if (uVar3 != 0) {
    for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1) {
      bVar1 = *param_3;
      pbVar5 = param_3 + 1;
      if (bVar1 < 0x81) {
        draw_glyph_with_background_at_4200a5be(param_1,param_2,bVar1,param_4,param_5,param_6);
        uVar4 = param_4 >> 1 & 0xff;
      }
      else {
        pbVar5 = param_3 + 2;
        uVar2 = uVar2 + 1;
        draw_large_digit_at_4200aae0(param_1,param_2,CONCAT11(bVar1,param_3[1]),param_4,param_5,param_6);
        uVar4 = param_4;
      }
      param_1 = param_1 + uVar4 & 0xffff;
      param_3 = pbVar5;
    }
  }
  return;
}

// Audit label: application_review; entry: ram:4200acae; name: draw_clock_separator_at_4200acae

void draw_clock_separator_at_4200acae(uint param_1,uint param_2,int param_3,undefined4 param_4,undefined4 param_5)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  undefined1 *puVar4;
  uint arg3;
  byte bVar5;
  byte bVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;

  if (param_3 == 1) {
    uVar10 = 0x50;
    uVar11 = 0x1e;
  }
  else if (param_3 == 2) {
    uVar10 = 100;
    uVar11 = 100;
  }
  else if (param_3 == 3) {
    uVar10 = 200;
    uVar11 = 0xf;
  }
  else if (param_3 == 4) {
    uVar10 = 5;
    uVar11 = 0xb;
  }
  else {
    uVar10 = 0;
    uVar11 = 0;
  }
  uVar8 = uVar10 >> 3;
  if ((uVar10 & 7) != 0) {
    uVar8 = uVar8 + 1;
  }
  (*(code *)&SUB_ram_40000488)(&glyph_pixel_buffer_at_3fcb7da8,0,0x2800);
  uVar9 = 0;
  puVar4 = &glyph_pixel_buffer_at_3fcb7da8;
  bVar1 = 0;
  arg3 = param_2;
  do {
    if (uVar11 <= uVar9) {
      if (&glyph_pixel_buffer_at_3fcb7da8 < puVar4) {
        st7789_blit_rectangle_at_4200950e(param_1,param_2,(uVar10 + param_1 & 0xffff) - 1 & 0xffff,arg3 - 1 & 0xffff,
                         &glyph_pixel_buffer_at_3fcb7da8);
      }
      return;
    }
    uVar2 = uVar10;
    for (uVar7 = 0; uVar7 < uVar8; uVar7 = uVar7 + 1 & 0xff) {
      if (param_3 == 1) {
        bVar1 = (&DAT_ram_3c0e9b48)[uVar9 * uVar8 + uVar7];
      }
      else if (param_3 == 2) {
        bVar1 = (&DAT_ram_3c0e9634)[uVar9 * uVar8 + uVar7];
      }
      else if (param_3 == 3) {
        bVar1 = (&DAT_ram_3c0e94bc)[uVar9 * uVar8 + uVar7];
      }
      else if (param_3 == 4) {
        bVar1 = (&DAT_ram_3c0e94b0)[uVar9 * uVar8 + uVar7];
      }
      bVar6 = 1;
      for (bVar5 = 0; bVar5 < 8; bVar5 = bVar5 + 1) {
        if ((bVar1 & bVar6) == 0) {
          *puVar4 = (char)((uint)param_5 >> 8);
          puVar4[1] = (char)param_5;
        }
        else {
          *puVar4 = (char)((uint)param_4 >> 8);
          puVar4[1] = (char)param_4;
        }
        puVar4 = puVar4 + 2;
        bVar6 = bVar6 << 1;
        uVar3 = uVar2 - 1;
        uVar2 = uVar3 & 0xffff;
        if ((uVar3 & 0xffff) == 0) break;
      }
    }
    uVar7 = arg3 + 1 & 0xffff;
    if (0x27ff < (((uint)(puVar4 + -0x3fcb7da8) & 0xffff) + uVar10 * 2 & 0xffff)) {
      st7789_blit_rectangle_at_4200950e(param_1,param_2,(uVar10 + param_1 & 0xffff) - 1 & 0xffff,arg3,
                       &glyph_pixel_buffer_at_3fcb7da8);
      puVar4 = &glyph_pixel_buffer_at_3fcb7da8;
      param_2 = uVar7;
    }
    uVar9 = uVar9 + 1 & 0xff;
    arg3 = uVar7;
  } while( true );
}
