/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Executable reconstruction: app/settings/settings.c; RGB helpers in
 * app/media/color_convert.c.
 */

// Audit label: application_review; entry: ram:42008552; name: load_settings_and_defaults_at_42008552

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void load_settings_and_defaults_at_42008552(void)

{
  esp_flash_read(0,&enabled_photo_mask_at_3fcb7b9c,0x3e7000,0x1bc);
  if (0x1e < enabled_photo_mask_at_3fcb7b9c) {
    enabled_photo_mask_at_3fcb7b9c = 0x1f;
  }
  if ((ntp_server_at_3fcb7c22 == '\0') || (ntp_server_at_3fcb7c22 == -1)) {
    (*(code *)&SUB_ram_40000488)(&ntp_server_at_3fcb7c22,0,0x41);
    ntp_server_at_3fcb7c22 = s_pool_ntp_org_ram_3c0c29ec[0];
    DAT_ram_3fcb7c22_1 = s_pool_ntp_org_ram_3c0c29ec[1];
    DAT_ram_3fcb7c24._0_1_ = s_pool_ntp_org_ram_3c0c29ec[2];
    DAT_ram_3fcb7c24._1_1_ = s_pool_ntp_org_ram_3c0c29ec[3];
    DAT_ram_3fcb7c26._0_1_ = s_pool_ntp_org_ram_3c0c29ec[4];
    DAT_ram_3fcb7c26._1_1_ = s_pool_ntp_org_ram_3c0c29ec[5];
    DAT_ram_3fcb7c28._0_1_ = s_pool_ntp_org_ram_3c0c29ec[6];
    DAT_ram_3fcb7c28._1_1_ = s_pool_ntp_org_ram_3c0c29ec[7];
    DAT_ram_3fcb7c2a._0_1_ = s_pool_ntp_org_ram_3c0c29ec[8];
    DAT_ram_3fcb7c2a._1_1_ = s_pool_ntp_org_ram_3c0c29ec[9];
    DAT_ram_3fcb7c2c._0_1_ = s_pool_ntp_org_ram_3c0c29ec[10];
    DAT_ram_3fcb7c2c._1_1_ = s_pool_ntp_org_ram_3c0c29ec[0xb];
    DAT_ram_3fcb7c2e = s_pool_ntp_org_ram_3c0c29ec[0xc];
  }
  if ((city_name_at_3fcb7c77 == '\0') || (city_name_at_3fcb7c77 == -1)) {
    (*(code *)&SUB_ram_40000488)(&city_name_at_3fcb7c77,0,0x41);
    city_name_at_3fcb7c77 = s_Shenzhen_ram_3c0c29fc[0];
    DAT_ram_3fcb7c78 = s_Shenzhen_ram_3c0c29fc[1];
    DAT_ram_3fcb7c79 = s_Shenzhen_ram_3c0c29fc[2];
    DAT_ram_3fcb7c7a = s_Shenzhen_ram_3c0c29fc[3];
    DAT_ram_3fcb7c7b = s_Shenzhen_ram_3c0c29fc[4];
    DAT_ram_3fcb7c7c = s_Shenzhen_ram_3c0c29fc[5];
    DAT_ram_3fcb7c7d = s_Shenzhen_ram_3c0c29fc[6];
    DAT_ram_3fcb7c7e = s_Shenzhen_ram_3c0c29fc[7];
    DAT_ram_3fcb7c7f = s_Shenzhen_ram_3c0c29fc[8];
  }
  if ((country_code_at_3fcb7c63 == '\0') || (country_code_at_3fcb7c63 == -1)) {
    (*(code *)&SUB_ram_40000488)(&country_code_at_3fcb7c63,0,0x14);
    country_code_at_3fcb7c63 = 'C';
    DAT_ram_3fcb7c64 = 0x4e;
    DAT_ram_3fcb7c65 = 0;
  }
  if (((overlapping_weather_api_key_at_3fcb7cb8 & 0xff) == 0) || ((overlapping_weather_api_key_at_3fcb7cb8 & 0xff) == 0xff)) {
    (*(code *)&SUB_ram_40000488)(&weather_api_key_at_3fcb7cb8,0,0x41);
    overlapping_weather_api_key_at_3fcb7cb8 = DAT_ram_3c0c2a08;
    DAT_ram_3fcb7cbc = DAT_ram_3c0c2a0c;
    DAT_ram_3fcb7cc0 = DAT_ram_3c0c2a10;
    DAT_ram_3fcb7cc4 = DAT_ram_3c0c2a14;
    DAT_ram_3fcb7cc8 = DAT_ram_3c0c2a18;
    DAT_ram_3fcb7ccc = DAT_ram_3c0c2a1c;
    DAT_ram_3fcb7cd0 = DAT_ram_3c0c2a20;
    DAT_ram_3fcb7cd4 = DAT_ram_3c0c2a24;
    DAT_ram_3fcb7cd8 = DAT_ram_3c0c2a28;
  }
  if (4 < selected_animation_at_3fcb7d00) {
    selected_animation_at_3fcb7d00 = 0;
  }
  if (3 < selected_clock_theme_at_3fcb7d04) {
    selected_clock_theme_at_3fcb7d04 = 0;
  }
  if (1 < fahrenheit_flag_at_3fcb7d08) {
    fahrenheit_flag_at_3fcb7d08 = 0;
  }
  if (1 < hour12_flag_at_3fcb7d0c) {
    hour12_flag_at_3fcb7d0c = 0;
  }
  if (1 < miles_flag_at_3fcb7d10) {
    miles_flag_at_3fcb7d10 = 0;
  }
  if (1 < browser_time_flag_at_3fcb7d14) {
    browser_time_flag_at_3fcb7d14 = 0;
  }
  if (1 < date_format_at_3fcb7d18) {
    date_format_at_3fcb7d18 = 2;
  }
  if (1000 < day_backlight_per_mille_at_3fcb7d1c) {
    day_backlight_per_mille_at_3fcb7d1c = 0;
  }
  if (0xffff < overlapping_clock_hour_color_rgb565_at_3fcb7d20) {
    overlapping_clock_hour_color_rgb565_at_3fcb7d20 = 0xf800;
  }
  if (0xffff < overlapping_clock_minute_color_rgb565_at_3fcb7d24) {
    overlapping_clock_minute_color_rgb565_at_3fcb7d24 = 0xffe0;
  }
  if (0xffff < overlapping_clock_detail_color_rgb565_at_3fcb7d28) {
    overlapping_clock_detail_color_rgb565_at_3fcb7d28 = 0xffff;
  }
  if (1 < night_mode_flag_at_3fcb7d2c) {
    night_mode_flag_at_3fcb7d2c = 0;
  }
  if (5 < night_start_hour_at_3fcb7d30 - 0x12U) {
    night_start_hour_at_3fcb7d30 = 0x16;
  }
  if (7 < night_stop_hour_at_3fcb7d34 - 5U) {
    night_stop_hour_at_3fcb7d34 = 9;
  }
  if (1000 < night_backlight_per_mille_at_3fcb7d38) {
    night_backlight_per_mille_at_3fcb7d38 = 500;
  }
  if (0x3c < photo_interval_seconds_at_3fcb7d3c) {
    photo_interval_seconds_at_3fcb7d3c = 5;
  }
  if (0x1f < slideshow_photo_mask_at_3fcb7d40) {
    slideshow_photo_mask_at_3fcb7d40 = 0x1f;
  }
  if (0x19000 < photo1_size_at_3fcb7d44) {
    photo1_size_at_3fcb7d44 = 0x10fcf;
  }
  if (0x19000 < photo2_size_at_3fcb7d48) {
    photo2_size_at_3fcb7d48 = 0x188af;
  }
  if (0x19000 < photo3_size_at_3fcb7d4c) {
    photo3_size_at_3fcb7d4c = 0x156ce;
  }
  if (0x19000 < photo4_size_at_3fcb7d50) {
    photo4_size_at_3fcb7d50 = 0x10399;
  }
  if (0x19000 < photo5_size_at_3fcb7d54) {
    photo5_size_at_3fcb7d54 = 0x14ecd;
  }
  return;
}

// Audit label: application_review; entry: ram:42008a00; name: save_settings_sector_at_42008a00

void save_settings_sector_at_42008a00(void)

{
  esp_flash_erase_region(0,0x3e7000,0x1000);
  esp_flash_write(0,&enabled_photo_mask_at_3fcb7b9c,0x3e7000,0x1bc);
  return;
}

// Audit label: application_review; entry: ram:42008a34; name: unpack_rgb565_channels_at_42008a34

void unpack_rgb565_channels_at_42008a34(uint color_rgb565,byte *red_out,byte *green_out,byte *blue_out)

{
  uint uVar1;

  uVar1 = color_rgb565 >> 5 & 0x3f;
  *red_out = (byte)(color_rgb565 >> 0xd) | (byte)((color_rgb565 >> 0xb) << 3);
  *green_out = (byte)(uVar1 << 2) | (byte)(uVar1 >> 4);
  *blue_out = (byte)((color_rgb565 & 0x1f) >> 2) | (byte)((color_rgb565 & 0x1f) << 3);
  return;
}

// Audit label: application_review; entry: ram:42008a6a; name: rgb565_to_rgb888_at_42008a6a

uint rgb565_to_rgb888_at_42008a6a(undefined4 color_rgb565)

{
  byte blue_channel;
  byte green_channel;
  byte red_channel [17];

  unpack_rgb565_channels_at_42008a34(color_rgb565,red_channel,&green_channel,&blue_channel);
  return (uint)blue_channel | (uint)red_channel[0] << 0x10 | (uint)green_channel << 8;
}

// Audit label: application_review; entry: ram:42008a96; name: rgb888_to_rgb565_at_42008a96

uint rgb888_to_rgb565_at_42008a96(uint red_channel,uint green_channel,uint blue_channel)

{
  return ((int)(short)((ushort)((red_channel >> 3) << 0xb) | (ushort)((green_channel >> 2) << 5)) |
         blue_channel >> 3) & 0xffff;
}

// Audit label: application_review; entry: ram:42008aae; name: hex_color_to_rgb565_at_42008aae

void hex_color_to_rgb565_at_42008aae(uint color_rgb888)

{
  rgb888_to_rgb565_at_42008a96(color_rgb888 >> 0x10 & 0xff,color_rgb888 >> 8 & 0xff,color_rgb888 & 0xff);
  return;
}

// Audit label: application_review; entry: ram:42008ace; name: parse_hex_byte_at_42008ace

uint parse_hex_byte_at_42008ace(uint high_hex_character,uint low_hex_character)

{
  uint low_nibble;
  uint high_nibble;

  high_nibble = high_hex_character - 0x30 & 0xff;
  if (9 < high_nibble) {
    if ((high_hex_character - 0x41 & 0xff) < 6) {
      high_nibble = high_hex_character - 0x37 & 0xff;
    }
    else {
      high_nibble = high_hex_character;
      if ((high_hex_character - 0x61 & 0xff) < 6) {
        high_nibble = high_hex_character - 0x57 & 0xff;
      }
    }
  }
  low_nibble = low_hex_character - 0x30 & 0xff;
  if (9 < low_nibble) {
    if ((low_hex_character - 0x41 & 0xff) < 6) {
      low_nibble = low_hex_character - 0x37 & 0xff;
    }
    else {
      low_nibble = low_hex_character;
      if ((low_hex_character - 0x61 & 0xff) < 6) {
        low_nibble = low_hex_character - 0x57 & 0xff;
      }
    }
  }
  return low_nibble | (high_nibble & 0xf) << 4;
}

// Audit label: application_review; entry: ram:42008b58; name: parse_hex_color_at_42008b58

uint parse_hex_color_at_42008b58(char *hex_color_text)

{
  char text_length;
  uint parsed_rgb888;
  int red_channel;
  uint green_channel;

  if (hex_color_text == (char *)0x0) {
    parsed_rgb888 = 0;
  }
  else {
    if (*hex_color_text == '#') {
      hex_color_text = hex_color_text + 1;
    }
    text_length = (*(code *)&SUB_ram_400004a8)(hex_color_text);
    if (text_length == '\x06') {
      red_channel = parse_hex_byte_at_42008ace(*hex_color_text,hex_color_text[1]);
      green_channel = parse_hex_byte_at_42008ace(hex_color_text[2],hex_color_text[3]);
      parsed_rgb888 = parse_hex_byte_at_42008ace(hex_color_text[4],hex_color_text[5]);
      parsed_rgb888 = parsed_rgb888 | (green_channel | red_channel << 8) << 8;
    }
    else {
      parsed_rgb888 = 0;
    }
  }
  return parsed_rgb888;
}
