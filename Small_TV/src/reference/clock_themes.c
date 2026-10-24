/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Per-function reconstruction targets: symbol-map.json native_targets.
 */

// Audit label: application_review; entry: ram:4200aebe; name: initialize_classic_clock_at_4200aebe

void initialize_classic_clock_at_4200aebe(void)

{
  DAT_ram_3fcc3a29 = 0xff;
  DAT_ram_3fcc3a28 = 0xff;
  DAT_ram_3fcc3a27 = 0xff;
  DAT_ram_3fcc39f7 = 1;
  DAT_ram_3fcc39f6 = 1;
  DAT_ram_3fcc39f5 = 1;
  DAT_ram_3fcc3a26 = 0;
  return;
}

// Audit label: application_review; entry: ram:4200aefc; name: draw_city_label_at_4200aefc

void draw_city_label_at_4200aefc(void)

{
  char cVar1;

  fill_rectangle_at_42009936(0,0,0xb4,0x18,0);
  cVar1 = (*(code *)&SUB_ram_400004a8)(&city_name_at_3fcb7c77);
  if (cVar1 != '\0') {
    draw_ascii_text_at_4200abee((int)(0xb4 - (uint)(byte)(cVar1 * '\f')) >> 1 & 0xffff,10,&city_name_at_3fcb7c77,
                     0x18,0x7e0,0);
  }
  return;
}

// Audit label: application_review; entry: ram:4200af5e; name: draw_weather_description_at_4200af5e

void draw_weather_description_at_4200af5e(void)

{
  byte bVar1;

  fill_rectangle_at_42009936(0,0x28,0xb4,0x18,0);
  bVar1 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3fcba9b8);
  if (bVar1 < 0x10) {
    if (bVar1 == 0) {
      return;
    }
  }
  else {
    bVar1 = 0xf;
  }
  draw_ascii_text_at_4200abee((int)(0xb4 - (uint)(byte)(bVar1 * '\f')) >> 1 & 0xffff,0x28,&DAT_ram_3fcba9b8,
                   0x18,0xffff,0);
  return;
}

// Audit label: application_review; entry: ram:4200afcc; name: draw_classic_clock_time_at_4200afcc

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void draw_classic_clock_time_at_4200afcc(void)

{
  char cVar1;
  uint uVar2;

  DAT_ram_3fcba9ac = 0;
  DAT_ram_3fcba9b0 = 0;
  DAT_ram_3fcba9b4 = 0;
  DAT_ram_3fcba9b6 = 0;
  uVar2 = (uint)local_hour_at_3fcbffce;
  if ((hour12_flag_at_3fcb7d0c == 1) && (0xc < uVar2)) {
    uVar2 = uVar2 - 0xc & 0xff;
  }
  cVar1 = (char)(uVar2 / 10);
  overlapping_clock_text_buffer_at_3fcba9a8 = CONCAT11((char)uVar2 + cVar1 * -10 + '0',cVar1 + '0');
  overlapping_clock_text_buffer_at_3fcba9a8 = (uint)overlapping_clock_text_buffer_at_3fcba9a8;
  draw_ascii_text_at_4200abee(0,0x50,&clock_text_buffer_at_3fcba9a8,0x40,clock_hour_color_rgb565_at_3fcb7d20,0);
  DAT_ram_3fcba9ac = 0;
  DAT_ram_3fcba9b0 = 0;
  DAT_ram_3fcba9b4 = 0;
  DAT_ram_3fcba9b6 = 0;
  if ((local_second_at_3fcbffd0 & 1) == 0) {
    overlapping_clock_text_buffer_at_3fcba9a8 = 0x3a;
    draw_ascii_text_at_4200abee(0x40,0x50,&clock_text_buffer_at_3fcba9a8,0x40,0xffff,0);
  }
  else {
    overlapping_clock_text_buffer_at_3fcba9a8 = 0x20;
    draw_ascii_text_at_4200abee(0x40,0x50,&clock_text_buffer_at_3fcba9a8,0x40,0,0);
  }
  if ((local_minute_at_3fcbffcf != DAT_ram_3fcc3a28) || (DAT_ram_3fcc3a26 != '\0')) {
    DAT_ram_3fcc39f5 = 1;
    DAT_ram_3fcc3a26 = '\0';
    DAT_ram_3fcba9ac = 0;
    DAT_ram_3fcba9b0 = 0;
    DAT_ram_3fcba9b4 = 0;
    DAT_ram_3fcba9b6 = 0;
    overlapping_clock_text_buffer_at_3fcba9a8 = CONCAT11(local_minute_at_3fcbffcf % 10 + 0x30,local_minute_at_3fcbffcf / 10 + 0x30);
    overlapping_clock_text_buffer_at_3fcba9a8 = (uint)overlapping_clock_text_buffer_at_3fcba9a8;
    draw_ascii_text_at_4200abee(0x60,0x50,&clock_text_buffer_at_3fcba9a8,0x40,clock_minute_color_rgb565_at_3fcb7d24,0);
    overlapping_clock_text_buffer_at_3fcba9a8 = 0;
    DAT_ram_3fcba9ac = 0;
    DAT_ram_3fcba9b0 = 0;
    DAT_ram_3fcba9b4 = 0;
    DAT_ram_3fcba9b6 = 0;
    if (local_weekday_at_3fcbffd1 == '\x01') {
      overlapping_clock_text_buffer_at_3fcba9a8 = 0x6e6f4d;
    }
    else if (local_weekday_at_3fcbffd1 == '\x02') {
      overlapping_clock_text_buffer_at_3fcba9a8 = 0x657554;
    }
    else if (local_weekday_at_3fcbffd1 == '\x03') {
      overlapping_clock_text_buffer_at_3fcba9a8 = 0x646557;
    }
    else if (local_weekday_at_3fcbffd1 == '\x04') {
      overlapping_clock_text_buffer_at_3fcba9a8 = 0x756854;
    }
    else if (local_weekday_at_3fcbffd1 == '\x05') {
      overlapping_clock_text_buffer_at_3fcba9a8 = 0x697246;
    }
    else if (local_weekday_at_3fcbffd1 == '\x06') {
      overlapping_clock_text_buffer_at_3fcba9a8 = 0x746153;
    }
    else if (local_weekday_at_3fcbffd1 == '\0') {
      overlapping_clock_text_buffer_at_3fcba9a8 = 0x6e7553;
    }
    draw_ascii_text_at_4200abee(0xb0,0x6e,&clock_text_buffer_at_3fcba9a8,0x20,clock_detail_color_rgb565_at_3fcb7d28,0);
    overlapping_clock_text_buffer_at_3fcba9a8 = 0;
    DAT_ram_3fcba9ac = 0;
    DAT_ram_3fcba9b0 = 0;
    DAT_ram_3fcba9b4 = 0;
    DAT_ram_3fcba9b6 = 0;
    fill_rectangle_at_42009936(0,0x96,0x78,0x18,0);
    if (date_format_at_3fcb7d18 == 0) {
      (*(code *)&SUB_ram_400006a8)
                (&clock_text_buffer_at_3fcba9a8,"%d/%d/%d",local_month_at_3fcbffcc,local_day_at_3fcbffcd,local_year_at_3fcbffc8);
    }
    else if (date_format_at_3fcb7d18 == 1) {
      (*(code *)&SUB_ram_400006a8)
                (&clock_text_buffer_at_3fcba9a8,"%d/%d/%d",local_day_at_3fcbffcd,local_month_at_3fcbffcc,local_year_at_3fcbffc8);
    }
    else if (date_format_at_3fcb7d18 == 2) {
      (*(code *)&SUB_ram_400006a8)
                (&clock_text_buffer_at_3fcba9a8,"%d/%d/%d",local_year_at_3fcbffc8,local_month_at_3fcbffcc,local_day_at_3fcbffcd);
    }
    draw_ascii_text_at_4200abee(0,0x96,&clock_text_buffer_at_3fcba9a8,0x18,0xffff,0);
  }
  return;
}

// Audit label: application_review; entry: ram:4200b340; name: draw_weather_status_at_4200b340

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void draw_weather_status_at_4200b340(void)

{
  byte bVar1;
  undefined4 uVar2;
  undefined8 uVar3;

  if (DAT_ram_3fcc39d7 != '\0') {
    bVar1 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3fcbff6c);
    if (bVar1 < 7) {
      if (bVar1 == 0) goto LAB_ram_4200b3ac;
    }
    else {
      bVar1 = 6;
    }
    draw_ascii_text_at_4200abee(((int)(0x50 - (uint)(byte)(bVar1 * '\f')) >> 1 & 0xffffU) + 0xa0 & 0xffff,0x53,
                     &DAT_ram_3fcbff6c,0x18,0xffe0,0);
  }
LAB_ram_4200b3ac:
  if (DAT_ram_3fcc3aa8 != 0) {
    draw_weather_bmp_at_42010eca(0xb4,10);
  }
  draw_jpeg_at_flash_offset_at_4200c518(10,0xb4,0x3ba800);
  draw_jpeg_at_flash_offset_at_4200c518(0x28,0xba,0x3c2000);
  overlapping_clock_text_buffer_at_3fcba9a8 = 0;
  DAT_ram_3fcba9ac = 0;
  DAT_ram_3fcba9b0 = 0;
  DAT_ram_3fcba9b4 = 0;
  DAT_ram_3fcba9b6 = 0;
  fill_rectangle_at_42009936(0x50,0xb4,0x48,0x18,0);
  if (DAT_ram_3fcc39d7 == '\0') {
    if (fahrenheit_flag_at_3fcb7d08 == 1) {
      overlapping_clock_text_buffer_at_3fcba9a8 = 0xa82d2d20;
      DAT_ram_3fcba9ac = CONCAT22(DAT_ram_3fcba9ac._2_2_,0x48);
    }
    else {
      overlapping_clock_text_buffer_at_3fcba9a8 = 0xa12d2d20;
      DAT_ram_3fcba9ac = CONCAT22(DAT_ram_3fcba9ac._2_2_,0xe6);
    }
  }
  else {
    uVar3 = (*(code *)&SUB_ram_40000a54)(weather_temperature_c_at_3fcc3a4c);
    uVar2 = (undefined4)((ulonglong)uVar3 >> 0x20);
    if (fahrenheit_flag_at_3fcb7d08 == 1) {
      uVar3 = (*(code *)&SUB_ram_40000a8c)((int)uVar3,uVar2,DAT_ram_3c0d6328,DAT_ram_3c0d632c);
      uVar3 = (*(code *)&SUB_ram_40000a18)
                        ((int)uVar3,(int)((ulonglong)uVar3 >> 0x20),DAT_ram_3c0d6330,
                         DAT_ram_3c0d6334);
      (*(code *)&SUB_ram_400006a8)
                (&clock_text_buffer_at_3fcba9a8,&DAT_ram_3c0c2b8c,(int)uVar3,(int)((ulonglong)uVar3 >> 0x20));
    }
    else {
      (*(code *)&SUB_ram_400006a8)(&clock_text_buffer_at_3fcba9a8,&DAT_ram_3c0c2b9c,(int)uVar3,uVar2);
    }
  }
  draw_ascii_text_at_4200abee(0x50,0xb4,&clock_text_buffer_at_3fcba9a8,0x18,0xffff,0);
  draw_jpeg_at_flash_offset_at_4200c518(0xc,0xd2,0x3be400);
  draw_jpeg_at_flash_offset_at_4200c518(0x28,0xd8,0x3c5c00);
  overlapping_clock_text_buffer_at_3fcba9a8 = 0;
  DAT_ram_3fcba9ac = 0;
  DAT_ram_3fcba9b0 = 0;
  DAT_ram_3fcba9b4 = 0;
  DAT_ram_3fcba9b6 = 0;
  fill_rectangle_at_42009936(0x50,0xd2,0x48,0x18,0);
  if (DAT_ram_3fcc39d7 == '\0') {
    (*(code *)&SUB_ram_400006a8)(&clock_text_buffer_at_3fcba9a8," --%%");
  }
  else {
    (*(code *)&SUB_ram_400006a8)(&clock_text_buffer_at_3fcba9a8," %d%%",weather_humidity_at_3fcc3a48);
  }
  draw_ascii_text_at_4200abee(0x50,0xd2,&clock_text_buffer_at_3fcba9a8,0x18,0xffff,0);
  return;
}

// Audit label: application_review; entry: ram:4200b5cc; name: load_animation_frame_table_at_4200b5cc

void load_animation_frame_table_at_4200b5cc(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;

  (*(code *)&SUB_ram_40000488)(&animation_frame_table_at_3fcba5a8,0,0x400);
  if (selected_animation_at_3fcb7d00 == 3) {
    iVar2 = 0x313000;
  }
  else if (selected_animation_at_3fcb7d00 < 4) {
    if (selected_animation_at_3fcb7d00 == 1) {
      iVar2 = 0x2af000;
    }
    else if (selected_animation_at_3fcb7d00 == 2) {
      iVar2 = 0x2e1000;
    }
    else {
      iVar2 = 0x27d000;
    }
  }
  else if (selected_animation_at_3fcb7d00 == 4) {
    iVar2 = 0x345000;
  }
  else {
    iVar2 = 0x27d000;
  }
  esp_flash_read(0,&animation_frame_table_at_3fcba5a8,iVar2,0x400);
  if (((animation_frame_table_at_3fcba5a8 == 'G') && (DAT_ram_3fcba5a9 == 'I')) && (DAT_ram_3fcba5aa == 'F')) {
    do {
      uVar3 = (uint)DAT_ram_3fcc3a24;
      iVar1 = *(int *)(&DAT_ram_3fcba5b7 + uVar3 * 8);
      DAT_ram_3fcc3a24 = DAT_ram_3fcc3a24 + 1;
      if (*(int *)(&DAT_ram_3fcba5b3 + uVar3 * 8) == 0 && iVar1 == 0) {
        DAT_ram_3fcc3a24 = 0;
      }
      if (0x7e < DAT_ram_3fcc3a24) {
        DAT_ram_3fcc3a24 = 0;
      }
    } while (*(int *)(&DAT_ram_3fcba5b3 + uVar3 * 8) == 0 && iVar1 == 0);
    draw_jpeg_at_flash_offset_at_4200c518(0xa0,0xa0,iVar1 + iVar2);
  }
  return;
}

// Audit label: application_review; entry: ram:4200b738; name: render_classic_clock_at_4200b738

void render_classic_clock_at_4200b738(void)

{
  byte bVar1;
  undefined8 uVar2;

  if (DAT_ram_3fcc39f7 != '\0') {
    DAT_ram_3fcc39f7 = '\0';
    if (DAT_ram_3fcc39d7 == '\0') {
      DAT_ram_3fcba9b8 = s_Getting_Weather_ram_3c0c2b50._0_4_;
      DAT_ram_3fcba9bc = s_Getting_Weather_ram_3c0c2b50._4_4_;
      DAT_ram_3fcba9c0 = s_Getting_Weather_ram_3c0c2b50._8_4_;
      DAT_ram_3fcba9c4 = s_Getting_Weather_ram_3c0c2b50._12_4_;
    }
    else {
      if (DAT_ram_3fcc3a25 == '\0') {
        (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcba9b8,&DAT_ram_3fcb7b84);
      }
      else if (DAT_ram_3fcc3a25 == '\x01') {
        (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcba9b8,&DAT_ram_3fcbff94);
      }
      else if (DAT_ram_3fcc3a25 == '\x02') {
        (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcba9b8,&DAT_ram_3fcb7b84);
      }
      else if (DAT_ram_3fcc3a25 == '\x03') {
        DAT_ram_3fcba9b8 = s_Wind_Speed_ram_3c0c2b60._0_4_;
        DAT_ram_3fcba9bc = s_Wind_Speed_ram_3c0c2b60._4_4_;
        DAT_ram_3fcba9c0._0_3_ =
             CONCAT12(s_Wind_Speed_ram_3c0c2b60[10],s_Wind_Speed_ram_3c0c2b60._8_2_);
      }
      else if (DAT_ram_3fcc3a25 == '\x04') {
        DAT_ram_3fcba9b8._0_1_ = '\0';
        DAT_ram_3fcba9b8._1_1_ = '\0';
        DAT_ram_3fcba9b8._2_1_ = '\0';
        DAT_ram_3fcba9b8._3_1_ = '\0';
        DAT_ram_3fcba9bc._0_1_ = '\0';
        DAT_ram_3fcba9bc._1_1_ = '\0';
        DAT_ram_3fcba9bc._2_1_ = '\0';
        DAT_ram_3fcba9bc._3_1_ = '\0';
        DAT_ram_3fcba9c0._0_1_ = '\0';
        DAT_ram_3fcba9c0._1_1_ = '\0';
        DAT_ram_3fcba9c0._2_1_ = '\0';
        DAT_ram_3fcba9c0._3_1_ = '\0';
        DAT_ram_3fcba9c4._0_1_ = '\0';
        DAT_ram_3fcba9c4._1_1_ = '\0';
        DAT_ram_3fcba9c4._2_1_ = '\0';
        DAT_ram_3fcba9c4._3_1_ = '\0';
        DAT_ram_3fcba9c8 = 0;
        if (miles_flag_at_3fcb7d10 == 1) {
          uVar2 = (*(code *)&SUB_ram_40000a8c)
                            (DAT_ram_3fcc3a40,DAT_ram_3fcc3a44,DAT_ram_3c0d6338,DAT_ram_3c0d633c);
          (*(code *)&SUB_ram_400006a8)
                    (&DAT_ram_3fcba9b8,"%.1fkm/h",(int)uVar2,(int)((ulonglong)uVar2 >> 0x20));
        }
        else {
          uVar2 = (*(code *)&SUB_ram_40000a8c)
                            (DAT_ram_3fcc3a40,DAT_ram_3fcc3a44,DAT_ram_3c0d6340,DAT_ram_3c0d6344);
          (*(code *)&SUB_ram_400006a8)
                    (&DAT_ram_3fcba9b8,"%.1fmile/h",(int)uVar2,(int)((ulonglong)uVar2 >> 0x20));
        }
      }
      else if (DAT_ram_3fcc3a25 == '\x05') {
        (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcba9b8,&DAT_ram_3fcb7b84);
      }
      else if (DAT_ram_3fcc3a25 == '\x06') {
        (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcba9b8,&DAT_ram_3fcbff80);
      }
      else if (DAT_ram_3fcc3a25 == '\a') {
        DAT_ram_3fcba9b8._0_1_ = '\0';
        DAT_ram_3fcba9b8._1_1_ = '\0';
        DAT_ram_3fcba9b8._2_1_ = '\0';
        DAT_ram_3fcba9b8._3_1_ = '\0';
        DAT_ram_3fcba9bc._0_1_ = '\0';
        DAT_ram_3fcba9bc._1_1_ = '\0';
        DAT_ram_3fcba9bc._2_1_ = '\0';
        DAT_ram_3fcba9bc._3_1_ = '\0';
        DAT_ram_3fcba9c0._0_1_ = '\0';
        DAT_ram_3fcba9c0._1_1_ = '\0';
        DAT_ram_3fcba9c0._2_1_ = '\0';
        DAT_ram_3fcba9c0._3_1_ = '\0';
        DAT_ram_3fcba9c4._0_1_ = '\0';
        DAT_ram_3fcba9c4._1_1_ = '\0';
        DAT_ram_3fcba9c4._2_1_ = '\0';
        DAT_ram_3fcba9c4._3_1_ = '\0';
        DAT_ram_3fcba9c8 = 0;
        if (fahrenheit_flag_at_3fcb7d08 == 1) {
          uVar2 = (*(code *)&SUB_ram_40000a8c)
                            (DAT_ram_3fcc3a30,DAT_ram_3fcc3a34,DAT_ram_3c0d6328,DAT_ram_3c0d632c);
          uVar2 = (*(code *)&SUB_ram_40000a18)
                            ((int)uVar2,(int)((ulonglong)uVar2 >> 0x20),DAT_ram_3c0d6330,
                             DAT_ram_3c0d6334);
          (*(code *)&SUB_ram_400006a8)
                    (&DAT_ram_3fcba9b8,&DAT_ram_3c0c2b84,(int)uVar2,(int)((ulonglong)uVar2 >> 0x20))
          ;
        }
        else {
          (*(code *)&SUB_ram_400006a8)
                    (&DAT_ram_3fcba9b8,&DAT_ram_3c0c2b94,DAT_ram_3fcc3a30,DAT_ram_3fcc3a34);
        }
      }
      else if (DAT_ram_3fcc3a25 == '\b') {
        (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcba9b8,&DAT_ram_3fcb7b84);
      }
      else if (DAT_ram_3fcc3a25 == '\t') {
        DAT_ram_3fcba9b8._0_1_ = '\0';
        DAT_ram_3fcba9b8._1_1_ = '\0';
        DAT_ram_3fcba9b8._2_1_ = '\0';
        DAT_ram_3fcba9b8._3_1_ = '\0';
        DAT_ram_3fcba9bc._0_1_ = '\0';
        DAT_ram_3fcba9bc._1_1_ = '\0';
        DAT_ram_3fcba9bc._2_1_ = '\0';
        DAT_ram_3fcba9bc._3_1_ = '\0';
        DAT_ram_3fcba9c0._0_1_ = '\0';
        DAT_ram_3fcba9c0._1_1_ = '\0';
        DAT_ram_3fcba9c0._2_1_ = '\0';
        DAT_ram_3fcba9c0._3_1_ = '\0';
        DAT_ram_3fcba9c4._0_1_ = '\0';
        DAT_ram_3fcba9c4._1_1_ = '\0';
        DAT_ram_3fcba9c4._2_1_ = '\0';
        DAT_ram_3fcba9c4._3_1_ = '\0';
        DAT_ram_3fcba9c8 = 0;
        if (fahrenheit_flag_at_3fcb7d08 == 1) {
          uVar2 = (*(code *)&SUB_ram_40000a8c)
                            (DAT_ram_3fcc3a38,DAT_ram_3fcc3a3c,DAT_ram_3c0d6328,DAT_ram_3c0d632c);
          uVar2 = (*(code *)&SUB_ram_40000a18)
                            ((int)uVar2,(int)((ulonglong)uVar2 >> 0x20),DAT_ram_3c0d6330,
                             DAT_ram_3c0d6334);
          (*(code *)&SUB_ram_400006a8)
                    (&DAT_ram_3fcba9b8,&DAT_ram_3c0c2ba4,(int)uVar2,(int)((ulonglong)uVar2 >> 0x20))
          ;
        }
        else {
          (*(code *)&SUB_ram_400006a8)
                    (&DAT_ram_3fcba9b8,&DAT_ram_3c0c2bb4,DAT_ram_3fcc3a38,DAT_ram_3fcc3a3c);
        }
      }
      bVar1 = DAT_ram_3fcc3a25 + 1;
      DAT_ram_3fcc3a25 = DAT_ram_3fcc3a25 + '\x01';
      if (9 < bVar1) {
        DAT_ram_3fcc3a25 = '\0';
      }
    }
    draw_weather_description_at_4200af5e();
  }
  if (((local_hour_at_3fcbffce != DAT_ram_3fcc3a29) || (local_minute_at_3fcbffcf != DAT_ram_3fcc3a28)) ||
     (local_second_at_3fcbffd0 != DAT_ram_3fcc3a27)) {
    draw_classic_clock_time_at_4200afcc();
    DAT_ram_3fcc3a29 = local_hour_at_3fcbffce;
    DAT_ram_3fcc3a28 = local_minute_at_3fcbffcf;
    DAT_ram_3fcc3a27 = local_second_at_3fcbffd0;
  }
  if (DAT_ram_3fcc39f5 != '\0') {
    DAT_ram_3fcc39f5 = '\0';
    draw_weather_status_at_4200b340();
    draw_city_label_at_4200aefc();
  }
  load_animation_frame_table_at_4200b5cc();
  return;
}

// Audit label: application_review; entry: ram:4200bb20; name: initialize_photo_slideshow_at_4200bb20

void initialize_photo_slideshow_at_4200bb20(void)

{
  DAT_ram_3fcc39d8 = 0;
  DAT_ram_3fcc39f7 = 1;
  DAT_ram_3fcc39f6 = 1;
  DAT_ram_3fcc39f5 = 1;
  DAT_ram_3fcc39f8 = 1;
  return;
}

// Audit label: application_review; entry: ram:4200bb4c; name: draw_next_enabled_photo_at_4200bb4c

void draw_next_enabled_photo_at_4200bb4c(void)

{
  ushort uVar1;
  byte bVar2;
  uint uVar3;

  for (uVar1 = 0; uVar1 < 5; uVar1 = uVar1 + 1) {
    if ((1 << (DAT_ram_3fcc3a51 & 0x1f) & slideshow_photo_mask_at_3fcb7d40) != 0) break;
    uVar3 = DAT_ram_3fcc3a51 + 1;
    DAT_ram_3fcc3a51 = (byte)uVar3;
    if (4 < (uVar3 & 0xff)) {
      DAT_ram_3fcc3a51 = 0;
    }
  }
  if (uVar1 == 5) {
    clear_display_at_42009a0a(0);
  }
  else {
    if (DAT_ram_3fcc3a51 == 0) {
      draw_jpeg_at_flash_offset_at_4200c518(0,0,0x200000);
    }
    else if (DAT_ram_3fcc3a51 == 1) {
      draw_jpeg_at_flash_offset_at_4200c518(0,0,0x219000);
    }
    else if (DAT_ram_3fcc3a51 == 2) {
      draw_jpeg_at_flash_offset_at_4200c518(0,0,0x232000);
    }
    else if (DAT_ram_3fcc3a51 == 3) {
      draw_jpeg_at_flash_offset_at_4200c518(0,0,0x24b000);
    }
    else if (DAT_ram_3fcc3a51 == 4) {
      draw_jpeg_at_flash_offset_at_4200c518(0,0,0x264000);
    }
    bVar2 = DAT_ram_3fcc3a51 + 1;
    DAT_ram_3fcc3a51 = DAT_ram_3fcc3a51 + 1;
    if (4 < bVar2) {
      DAT_ram_3fcc3a51 = 0;
    }
  }
  return;
}

// Audit label: application_review; entry: ram:4200bc36; name: advance_photo_slideshow_at_4200bc36

void advance_photo_slideshow_at_4200bc36(void)

{
  if ((DAT_ram_3fcc39f8 != '\0') && (DAT_ram_3fcc39d8 == '\0')) {
    if (DAT_ram_3fcc3a50 == '\0') {
      set_backlight_duty_at_42008bd2(300);
      DAT_ram_3fcc3a50 = DAT_ram_3fcc3a50 + '\x01';
    }
    else if (DAT_ram_3fcc3a50 == '\x01') {
      set_backlight_duty_at_42008bd2(600);
      DAT_ram_3fcc3a50 = DAT_ram_3fcc3a50 + '\x01';
    }
    else if (DAT_ram_3fcc3a50 == '\x02') {
      set_backlight_duty_at_42008bd2(1000);
      draw_next_enabled_photo_at_4200bb4c();
      draw_encoded_text_at_4200aa1e(5,0xe1,&DAT_ram_3fcb7b84,0x10,0xffff);
      DAT_ram_3fcc3a50 = DAT_ram_3fcc3a50 + '\x01';
    }
    else if (DAT_ram_3fcc3a50 == '\x03') {
      set_backlight_duty_at_42008bd2(600);
      DAT_ram_3fcc3a50 = DAT_ram_3fcc3a50 + '\x01';
    }
    else if (DAT_ram_3fcc3a50 == '\x04') {
      set_backlight_duty_at_42008bd2(300);
      DAT_ram_3fcc3a50 = DAT_ram_3fcc3a50 + '\x01';
    }
    else if (DAT_ram_3fcc3a50 == '\x05') {
      set_backlight_duty_at_42008bd2(0);
      DAT_ram_3fcc3a50 = '\0';
      DAT_ram_3fcc39f8 = '\0';
    }
  }
  return;
}

// Audit label: application_review; entry: ram:4200bd26; name: initialize_simple_clock_at_4200bd26

void initialize_simple_clock_at_4200bd26(void)

{
  draw_encoded_text_at_4200aa1e(5,0xe1,&DAT_ram_3fcb7b84,0x10,0xffff);
  draw_clock_separator_at_4200acae(0,0x46,2,0xc618,0);
  draw_clock_separator_at_4200acae(0x8c,0x46,2,0xc618,0);
  DAT_ram_3fcc39f7 = 1;
  DAT_ram_3fcc39f6 = 1;
  DAT_ram_3fcc39f5 = 1;
  return;
}

// Audit label: application_review; entry: ram:4200bd8c; name: render_simple_clock_at_4200bd8c

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void render_simple_clock_at_4200bd8c(void)

{
  char cVar1;
  byte bVar2;
  uint uVar3;

  if (DAT_ram_3fcc39f6 != '\0') {
    DAT_ram_3fcc39f6 = '\0';
    if ((local_second_at_3fcbffd0 & 1) == 0) {
      DAT_ram_3fcba9d0 = 0;
      DAT_ram_3fcba9d4 = 0;
      DAT_ram_3fcba9d8 = 0;
      DAT_ram_3fcba9da = 0;
      _DAT_ram_3fcba9cc = 0x3a;
      draw_ascii_text_at_4200abee(100,0x50,&DAT_ram_3fcba9cc,0x50,0xffff,0);
    }
    else {
      DAT_ram_3fcba9d0 = 0;
      DAT_ram_3fcba9d4 = 0;
      DAT_ram_3fcba9d8 = 0;
      DAT_ram_3fcba9da = 0;
      _DAT_ram_3fcba9cc = 0x20;
      draw_ascii_text_at_4200abee(100,0x50,&DAT_ram_3fcba9cc,0x50,0,0);
    }
  }
  if (DAT_ram_3fcc39f5 == '\0') {
    return;
  }
  DAT_ram_3fcc39f5 = 0;
  DAT_ram_3fcba9d0 = 0;
  DAT_ram_3fcba9d4 = 0;
  DAT_ram_3fcba9d8 = 0;
  DAT_ram_3fcba9da = 0;
  uVar3 = (uint)local_hour_at_3fcbffce;
  if ((hour12_flag_at_3fcb7d0c == 1) && (0xc < uVar3)) {
    uVar3 = uVar3 - 0xc & 0xff;
  }
  cVar1 = (char)(uVar3 / 10);
  _DAT_ram_3fcba9cc = CONCAT11((char)uVar3 + cVar1 * -10 + '0',cVar1 + '0');
  _DAT_ram_3fcba9cc = (uint)_DAT_ram_3fcba9cc;
  draw_ascii_text_at_4200abee(10,0x50,&DAT_ram_3fcba9cc,0x50,0xffff,0xc618);
  DAT_ram_3fcba9d0 = 0;
  DAT_ram_3fcba9d4 = 0;
  DAT_ram_3fcba9d8 = 0;
  DAT_ram_3fcba9da = 0;
  _DAT_ram_3fcba9cc = CONCAT11(local_minute_at_3fcbffcf % 10 + 0x30,local_minute_at_3fcbffcf / 10 + 0x30);
  _DAT_ram_3fcba9cc = (uint)_DAT_ram_3fcba9cc;
  draw_ascii_text_at_4200abee(0x96,0x50,&DAT_ram_3fcba9cc,0x50,0xffff,0xc618);
  if (date_format_at_3fcb7d18 == 0) {
    (*(code *)&SUB_ram_400006a8)
              (&DAT_ram_3fcba9cc,"%d/%d/%d",local_month_at_3fcbffcc,local_day_at_3fcbffcd,local_year_at_3fcbffc8);
  }
  else if (date_format_at_3fcb7d18 == 1) {
    (*(code *)&SUB_ram_400006a8)
              (&DAT_ram_3fcba9cc,"%d/%d/%d",local_day_at_3fcbffcd,local_month_at_3fcbffcc,local_year_at_3fcbffc8);
  }
  else if (date_format_at_3fcb7d18 == 2) {
    (*(code *)&SUB_ram_400006a8)
              (&DAT_ram_3fcba9cc,"%d/%d/%d",local_year_at_3fcbffc8,local_month_at_3fcbffcc,local_day_at_3fcbffcd);
  }
  bVar2 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3fcba9cc);
  if (bVar2 < 0x15) {
    if (bVar2 == 0) goto LAB_ram_4200bf9c;
  }
  else {
    bVar2 = 0x14;
  }
  draw_ascii_text_at_4200abee((int)(0xf0 - (uint)(byte)(bVar2 * '\f')) >> 1 & 0xffff,0xb4,&DAT_ram_3fcba9cc,
                   0x18,0xffff,0);
LAB_ram_4200bf9c:
  if (local_weekday_at_3fcbffd1 == '\x01') {
    _DAT_ram_3fcba9cc = 0x6e6f4d;
  }
  else if (local_weekday_at_3fcbffd1 == '\x02') {
    _DAT_ram_3fcba9cc = 0x657554;
  }
  else if (local_weekday_at_3fcbffd1 == '\x03') {
    _DAT_ram_3fcba9cc = 0x646557;
  }
  else if (local_weekday_at_3fcbffd1 == '\x04') {
    _DAT_ram_3fcba9cc = 0x756854;
  }
  else if (local_weekday_at_3fcbffd1 == '\x05') {
    _DAT_ram_3fcba9cc = 0x697246;
  }
  else if (local_weekday_at_3fcbffd1 == '\x06') {
    _DAT_ram_3fcba9cc = 0x746153;
  }
  else if (local_weekday_at_3fcbffd1 == '\a') {
    _DAT_ram_3fcba9cc = 0x6e7553;
  }
  draw_ascii_text_at_4200abee(0x66,0xcc,&DAT_ram_3fcba9cc,0x18,0x7e0,0);
  return;
}

// Audit label: application_review; entry: ram:4200c100; name: draw_initial_clock_screen_at_4200c100

void draw_initial_clock_screen_at_4200c100(void)

{
  draw_clock_separator_at_4200acae(0x14,0x8c,3,0xffff,0);
  DAT_ram_3fcc3a56 = 0;
  DAT_ram_3fcc3a55 = 0;
  DAT_ram_3fcc3a54 = 1;
  DAT_ram_3fcc3a53 = 0;
  DAT_ram_3fcc3a52 = 0;
  DAT_ram_3fcba9e8 = 0;
  DAT_ram_3fcba9ec = 0;
  DAT_ram_3fcba9f0 = 0;
  DAT_ram_3fcba9f4 = 0;
  DAT_ram_3fcba9dc = 0x3a726556;
  DAT_ram_3fcba9e0 = 0x2e302e30;
  DAT_ram_3fcba9e4 = 0x32;
  draw_ascii_text_at_4200abee(0x78,0xbe,&DAT_ram_3fcba9dc,0x18,0xffff,0);
  DAT_ram_3fcc39f7 = 1;
  DAT_ram_3fcc39f6 = 1;
  DAT_ram_3fcc39f5 = 1;
  DAT_ram_3fcc39f8 = 1;
  return;
}

// Audit label: application_review; entry: ram:4200c1c8; name: draw_startup_connection_status_at_4200c1c8

void draw_startup_connection_status_at_4200c1c8(void)

{
  if (((wifi_connection_state_at_3fcc3a74 == '\x02') && (DAT_ram_3fcc3a52 == '\0')) && (DAT_ram_3fcb7b84 != '\0')) {
    DAT_ram_3fcba9dc._0_1_ = '\0';
    DAT_ram_3fcba9dc._1_1_ = '\0';
    DAT_ram_3fcba9dc._2_1_ = '\0';
    DAT_ram_3fcba9dc._3_1_ = '\0';
    DAT_ram_3fcba9e0._0_1_ = '\0';
    DAT_ram_3fcba9e0._1_1_ = '\0';
    DAT_ram_3fcba9e0._2_1_ = '\0';
    DAT_ram_3fcba9e0._3_1_ = '\0';
    DAT_ram_3fcba9e4._0_1_ = '\0';
    DAT_ram_3fcba9e4._1_1_ = '\0';
    DAT_ram_3fcba9e4._2_1_ = '\0';
    DAT_ram_3fcba9e4._3_1_ = '\0';
    DAT_ram_3fcba9e8._0_1_ = '\0';
    DAT_ram_3fcba9e8._1_1_ = '\0';
    DAT_ram_3fcba9e8._2_1_ = '\0';
    DAT_ram_3fcba9e8._3_1_ = '\0';
    DAT_ram_3fcba9ec = 0;
    DAT_ram_3fcba9f0 = 0;
    DAT_ram_3fcba9f4 = 0;
    (*(code *)&SUB_ram_400006a8)(&DAT_ram_3fcba9dc,&DAT_ram_3fcb7b84);
    draw_ascii_text_at_4200abee(0x1d,0x72,&DAT_ram_3fcba9dc,0x18,0xffff,0);
  }
  if (DAT_ram_3fcc3a56 != DAT_ram_3fcc3a55) {
    fill_rectangle_at_42009936(0x1d,0x8e,DAT_ram_3fcc3a56,0xb,0xffff);
    draw_clock_separator_at_4200acae(DAT_ram_3fcc3a56 + 0x1d,0x8e,4,0xffff,0);
    DAT_ram_3fcc3a55 = DAT_ram_3fcc3a56;
  }
  if (DAT_ram_3fcc3a54 != DAT_ram_3fcc3a53) {
    fill_rectangle_at_42009936(0,0xa0,0xf0,0x20,0);
    DAT_ram_3fcba9f0 = 0;
    DAT_ram_3fcba9f4 = 0;
    DAT_ram_3fcba9dc._0_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[0];
    DAT_ram_3fcba9dc._1_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[1];
    DAT_ram_3fcba9dc._2_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[2];
    DAT_ram_3fcba9dc._3_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[3];
    DAT_ram_3fcba9e0._0_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[4];
    DAT_ram_3fcba9e0._1_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[5];
    DAT_ram_3fcba9e0._2_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[6];
    DAT_ram_3fcba9e0._3_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[7];
    DAT_ram_3fcba9e4._0_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[8];
    DAT_ram_3fcba9e4._1_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[9];
    DAT_ram_3fcba9e4._2_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[10];
    DAT_ram_3fcba9e4._3_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[0xb];
    DAT_ram_3fcba9e8._0_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[0xc];
    DAT_ram_3fcba9e8._1_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[0xd];
    DAT_ram_3fcba9e8._2_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[0xe];
    DAT_ram_3fcba9e8._3_1_ = s_Connecting_to_WiFi_ram_3c0c2bc4[0xf];
    DAT_ram_3fcba9ec =
         (uint)CONCAT12(s_Connecting_to_WiFi_ram_3c0c2bc4[0x12],
                        s_Connecting_to_WiFi_ram_3c0c2bc4._16_2_);
    draw_ascii_text_at_4200abee(0x14,0xa0,&DAT_ram_3fcba9dc,0x18,0x7e0,0);
    DAT_ram_3fcc3a53 = DAT_ram_3fcc3a54;
  }
  return;
}
