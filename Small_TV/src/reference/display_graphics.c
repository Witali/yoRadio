/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Executable reconstruction: app/display/st7789.c.
 */

// Audit label: application_review; entry: ram:420095c4; name: draw_filled_circle_at_420095c4

void draw_filled_circle_at_420095c4(int center_x,int center_y,int radius,ushort color_rgb565)

{
  int relative_x;
  int relative_y;
  int negative_radius;

  negative_radius = radius * -0x10000 >> 0x10;
  for (relative_y = negative_radius; relative_x = negative_radius, relative_y <= radius; relative_y = (relative_y + 1) * 0x10000 >> 0x10) {
    for (; relative_x <= radius; relative_x = (relative_x + 1) * 0x10000 >> 0x10) {
      if (relative_x * relative_x + relative_y * relative_y <= radius * radius) {
        st7789_draw_pixel_at_4200958a(center_x + relative_x & 0xffff,center_y + relative_y & 0xffff,color_rgb565);
      }
    }
  }
  return;
}

// Audit label: application_review; entry: ram:42009644; name: draw_thick_line_at_42009644

void draw_thick_line_at_42009644(uint x_start,uint y_start,uint x_end,uint y_end,ushort color_rgb565,
                     uint line_width)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  undefined8 uVar13;
  undefined8 uVar14;
  undefined8 uVar15;
  undefined8 uVar16;
  int iStack_88;
  int iStack_80;

  if (line_width == 1) {
    uVar2 = (int)(x_end - x_start) >> 0x1f;
    uVar2 = (uVar2 ^ x_end - x_start) - uVar2;
    if ((int)x_start < (int)x_end) {
      iVar12 = 1;
    }
    else {
      iVar12 = -1;
    }
    uVar3 = (int)(y_end - y_start) >> 0x1f;
    uVar3 = (uVar3 ^ y_end - y_start) - uVar3 & 0xffff;
    if ((int)y_start < (int)y_end) {
      iVar8 = 1;
    }
    else {
      iVar8 = -1;
    }
    uVar9 = uVar2 & 0xffff;
    uVar4 = (int)((uVar9 - uVar3) * 0x10000) >> 0x10;
    while( true ) {
      st7789_draw_pixel_at_4200958a(x_start & 0xffff,y_start & 0xffff,color_rgb565);
      if ((x_start == x_end) && (y_start == y_end)) break;
      iVar6 = (int)((uVar4 & 0xffff) << 0x11) >> 0x10;
      if ((int)(uVar3 * -0x10000) >> 0x10 <= iVar6) {
        uVar4 = (int)(((uVar4 & 0xffff) - uVar3) * 0x10000) >> 0x10;
        x_start = (int)(((x_start & 0xffff) + iVar12) * 0x10000) >> 0x10;
      }
      if (iVar6 <= (int)(uVar2 * 0x10000) >> 0x10) {
        uVar4 = (int)((uVar4 + uVar9) * 0x10000) >> 0x10;
        y_start = (int)(((y_start & 0xffff) + iVar8) * 0x10000) >> 0x10;
      }
    }
  }
  else {
    uVar13 = (*(code *)&SUB_ram_40000a54)(x_end - x_start);
    uVar14 = (*(code *)&SUB_ram_40000a54)(y_end - y_start);
    thunk_FUN_ram_420a7a42
              ((int)uVar14,(int)((ulonglong)uVar14 >> 0x20),(int)uVar13,
               (int)((ulonglong)uVar13 >> 0x20));
    (*(code *)&SUB_ram_40000aa4)();
    uVar13 = (*(code *)&SUB_ram_40000a2c)();
    iStack_80 = (line_width >> 1) * -0x10000;
    while( true ) {
      iStack_80 = iStack_80 >> 0x10;
      if ((int)(line_width >> 1) < iStack_80) break;
      uVar14 = (*(code *)&SUB_ram_40000a54)(iStack_80);
      uVar5 = (undefined4)((ulonglong)uVar14 >> 0x20);
      uVar15 = (*(code *)&SUB_ram_40000a18)
                         ((int)uVar13,(int)((ulonglong)uVar13 >> 0x20),DAT_ram_3c0d62e0,
                          DAT_ram_3c0d62e4);
      uVar16 = FUN_ram_420a7464();
      (*(code *)&SUB_ram_40000a8c)((int)uVar14,uVar5,(int)uVar16,(int)((ulonglong)uVar16 >> 0x20));
      FUN_ram_420a74e6();
      uVar3 = (*(code *)&SUB_ram_40000a34)();
      uVar15 = FUN_ram_420a73e0((int)uVar15,(int)((ulonglong)uVar15 >> 0x20));
      (*(code *)&SUB_ram_40000a8c)((int)uVar14,uVar5,(int)uVar15,(int)((ulonglong)uVar15 >> 0x20));
      FUN_ram_420a74e6();
      uVar4 = (*(code *)&SUB_ram_40000a34)();
      uVar2 = (int)(((uVar3 & 0xffff) + x_start) * 0x10000) >> 0x10;
      uVar9 = (int)(((uVar4 & 0xffff) + y_start) * 0x10000) >> 0x10;
      uVar10 = (int)(((uVar3 & 0xffff) + x_end) * 0x10000) >> 0x10;
      uVar3 = (int)(((uVar4 & 0xffff) + y_end) * 0x10000) >> 0x10;
      uVar4 = (int)(uVar10 - uVar2) >> 0x1f;
      uVar4 = (uVar4 ^ uVar10 - uVar2) - uVar4;
      if ((int)uVar2 < (int)uVar10) {
        iStack_88 = 1;
      }
      else {
        iStack_88 = -1;
      }
      uVar7 = (int)(uVar3 - uVar9) >> 0x1f;
      uVar7 = (uVar7 ^ uVar3 - uVar9) - uVar7 & 0xffff;
      if ((int)uVar9 < (int)uVar3) {
        iVar12 = 1;
      }
      else {
        iVar12 = -1;
      }
      uVar11 = uVar4 & 0xffff;
      uVar1 = (int)((uVar11 - uVar7) * 0x10000) >> 0x10;
      while( true ) {
        st7789_draw_pixel_at_4200958a(uVar2 & 0xffff,uVar9 & 0xffff,color_rgb565);
        if ((uVar2 == uVar10) && (uVar9 == uVar3)) break;
        iVar8 = (int)((uVar1 & 0xffff) << 0x11) >> 0x10;
        if ((int)(uVar7 * -0x10000) >> 0x10 <= iVar8) {
          uVar1 = (int)(((uVar1 & 0xffff) - uVar7) * 0x10000) >> 0x10;
          uVar2 = (int)(((uVar2 & 0xffff) + iStack_88) * 0x10000) >> 0x10;
        }
        if (iVar8 <= (int)(uVar4 * 0x10000) >> 0x10) {
          uVar1 = (int)((uVar1 + uVar11) * 0x10000) >> 0x10;
          uVar9 = (int)(((uVar9 & 0xffff) + iVar12) * 0x10000) >> 0x10;
        }
      }
      iStack_80 = (iStack_80 + 1) * 0x10000;
    }
  }
  return;
}

// Audit label: application_review; entry: ram:42009936; name: fill_rectangle_at_42009936

void fill_rectangle_at_42009936(uint x,uint y,uint width,uint height,undefined4 color_rgb565)

{
  undefined1 uVar1;
  uint uVar2;
  undefined1 auStack_54 [68];

  if ((x < 0xf0) && (y < 0xf0)) {
    if (0xf0 < (int)(x + width)) {
      width = 0xf0 - x & 0xffff;
    }
    if (0xf0 < (int)(y + height)) {
      height = 0xf0 - y & 0xffff;
    }
    st7789_set_window_at_420092d0(x,y,(width + x & 0xffff) - 1 & 0xffff,
                      (height + y & 0xffff) - 1 & 0xffff);
    uVar1 = (undefined1)((uint)color_rgb565 >> 8);
    auStack_54[0x40] = uVar1;
    auStack_54[0x41] = (char)color_rgb565;
    for (uVar2 = 0; uVar2 < 0x40; uVar2 = uVar2 + 2) {
      auStack_54[uVar2] = uVar1;
      auStack_54[uVar2 + 1] = (char)color_rgb565;
    }
    for (uVar2 = 0; uVar2 < width * height >> 5; uVar2 = uVar2 + 1) {
      st7789_write_data_at_4200925a(auStack_54,0x40);
    }
    uVar2 = width * height & 0x1f;
    if (uVar2 != 0) {
      st7789_write_data_at_4200925a(auStack_54,uVar2 << 1);
    }
  }
  return;
}

// Audit label: application_review; entry: ram:42009a0a; name: clear_display_at_42009a0a

void clear_display_at_42009a0a(undefined4 background_rgb565)

{
  fill_rectangle_at_42009936(0,0,0xf0,0xf0,background_rgb565);
  return;
}

// Audit label: application_review; entry: ram:42009a24; name: initialize_display_at_42009a24

void initialize_display_at_42009a24(void)

{
  st7789_initialize_at_4200934a();
  clear_display_at_42009a0a(0);
  return;
}
