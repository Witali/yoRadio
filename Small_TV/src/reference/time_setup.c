/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Executable reconstruction: app/services/time_sync.c + app/display/clock_ui.c.
 */

// Audit label: application_review; entry: ram:420109de; name: sntp_sync_notification_at_420109de

void sntp_sync_notification_at_420109de(void)

{
  undefined1 auStack_3c [36];
  undefined1 auStack_18 [16];

  DAT_ram_3fcc3ab8 = 1;
  FUN_ram_420aa7e2(auStack_18);
  FUN_ram_420aa5ce(auStack_18,auStack_3c);
  return;
}

// Audit label: application_review; entry: ram:42010a06; name: configure_sntp_and_timezone_at_42010a06

void configure_sntp_and_timezone_at_42010a06(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;

  iVar1 = FUN_ram_42017f44();
  if (iVar1 != 0) {
    FUN_ram_42017f0a();
  }
  posix_timezone_at_3fcbffa8 = 0;
  DAT_ram_3fcbffac = 0;
  DAT_ram_3fcbffb0 = 0;
  DAT_ram_3fcbffb4 = 0;
  DAT_ram_3fcbffb8 = 0;
  DAT_ram_3fcbffbc = 0;
  DAT_ram_3fcbffc0 = 0;
  DAT_ram_3fcbffc4 = 0;
  iVar1 = 0;
  do {
    if ((&PTR_DAT_ram_3c0c3c68_ram_3c0d69b8)[iVar1 * 3] == (undefined *)0x0) {
LAB_ram_42010a9a:
      posix_timezone_at_3fcbffa8 = 0x30544d47;
      DAT_ram_3fcbffac = 0x545342;
      uVar3 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(2,&DAT_ram_3c0c3bc4,
                       "W (%lu) %s: Country not found, using default timezone: GMT0BST\n",uVar3,
                       &DAT_ram_3c0c3bc4);
LAB_ram_42010ade:
      FUN_ram_42017eda(0);
      FUN_ram_42017f22(0,"ntp1.aliyun.com");
      if (ntp_server_at_3fcb7c22 == '\0') {
        FUN_ram_42017f22(1,"cn.pool.ntp.org");
      }
      else {
        FUN_ram_42017f22(1,&ntp_server_at_3fcb7c22);
      }
      FUN_ram_42017f22(2,"pool.ntp.org");
      FUN_ram_42017e90(sntp_sync_notification_at_420109de);
      FUN_ram_42017ef2();
      FUN_ram_420a9340(&DAT_ram_3c0c3c28,&posix_timezone_at_3fcbffa8,1);
      FUN_ram_420aa9c8();
      DAT_ram_3fcc3ab9 = 1;
      DAT_ram_3fcc3ab8 = 0;
      return;
    }
    iVar2 = (*(code *)&SUB_ram_400004a0)
                      ((&PTR_DAT_ram_3c0c3c68_ram_3c0d69b8)[iVar1 * 3],&country_code_at_3fcb7c63);
    if (iVar2 == 0) {
      (*(code *)&SUB_ram_4000049c)
                (&posix_timezone_at_3fcbffa8,(&PTR_s_CST_8_ram_3c0c3c6c_ram_3c0d69bc)[iVar1 * 3],0x1f);
      if ((posix_timezone_at_3fcbffa8 & 0xff) != 0) goto LAB_ram_42010ade;
      goto LAB_ram_42010a9a;
    }
    iVar1 = iVar1 + 1;
  } while( true );
}

// Audit label: application_review; entry: ram:42010b70; name: update_local_time_at_42010b70

void update_local_time_at_42010b70(void)

{
  undefined4 uVar1;
  int iVar2;
  uint uStack_3c;
  undefined1 uStack_38;
  undefined1 uStack_34;
  undefined1 uStack_30;
  char cStack_2c;
  int iStack_28;
  undefined1 uStack_24;
  undefined1 auStack_18 [16];

  if (DAT_ram_3fcc3ab9 == '\0') {
    configure_sntp_and_timezone_at_42010a06();
  }
  else {
    FUN_ram_420aa7e2(auStack_18);
    FUN_ram_420aa5ce(auStack_18,&uStack_3c);
    if (iStack_28 < 0x7d) {
      DAT_ram_3fcc3ab4 = DAT_ram_3fcc3ab4 + 1;
      if (0x14 < DAT_ram_3fcc3ab4) {
        uVar1 = FUN_ram_4038d3b4();
        FUN_ram_4038d2a2(2,&DAT_ram_3c0c3bc4,"W (%lu) %s: Time not synced yet. Current year: %d\n",
                         uVar1,&DAT_ram_3c0c3bc4,iStack_28 + 0x76c);
        DAT_ram_3fcc3ab4 = 0;
        iVar2 = FUN_ram_42017ea0();
        if (iVar2 == 0) {
          DAT_ram_3fcc3ab9 = '\0';
        }
      }
    }
    else {
      DAT_ram_3fcc3ab4 = 0;
      if (local_second_at_3fcbffd0 != uStack_3c) {
        local_year_at_3fcbffc8 = iStack_28 + 0x76c;
        local_month_at_3fcbffcc = cStack_2c + '\x01';
        local_day_at_3fcbffcd = uStack_30;
        local_hour_at_3fcbffce = uStack_34;
        local_minute_at_3fcbffcf = uStack_38;
        local_second_at_3fcbffd0 = (byte)uStack_3c;
        local_weekday_at_3fcbffd1 = uStack_24;
      }
    }
  }
  return;
}

// Audit label: application_review; entry: ram:42010c4e; name: draw_wifi_setup_instructions_at_42010c4e

void draw_wifi_setup_instructions_at_42010c4e(void)

{
  byte bVar1;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  uint uStack_24;
  char acStack_20 [4];
  char acStack_1c [2];
  char cStack_1a;

  if (DAT_ram_3fcc3aba != '\0') {
    return;
  }
  DAT_ram_3fcc3aba = 1;
  clear_display_at_42009a0a(0);
  uStack_2c._0_1_ = s_1_Open_your_phone_ram_3c0c44e4[0];
  uStack_2c._1_1_ = s_1_Open_your_phone_ram_3c0c44e4[1];
  uStack_2c._2_1_ = s_1_Open_your_phone_ram_3c0c44e4[2];
  uStack_2c._3_1_ = s_1_Open_your_phone_ram_3c0c44e4[3];
  uStack_28._0_1_ = s_1_Open_your_phone_ram_3c0c44e4[4];
  uStack_28._1_1_ = s_1_Open_your_phone_ram_3c0c44e4[5];
  uStack_28._2_1_ = s_1_Open_your_phone_ram_3c0c44e4[6];
  uStack_28._3_1_ = s_1_Open_your_phone_ram_3c0c44e4[7];
  uStack_24._0_1_ = s_1_Open_your_phone_ram_3c0c44e4[8];
  uStack_24._1_1_ = s_1_Open_your_phone_ram_3c0c44e4[9];
  uStack_24._2_1_ = s_1_Open_your_phone_ram_3c0c44e4[10];
  uStack_24._3_1_ = s_1_Open_your_phone_ram_3c0c44e4[0xb];
  acStack_20[0] = s_1_Open_your_phone_ram_3c0c44e4[0xc];
  acStack_20[1] = s_1_Open_your_phone_ram_3c0c44e4[0xd];
  acStack_20[2] = s_1_Open_your_phone_ram_3c0c44e4[0xe];
  acStack_20[3] = s_1_Open_your_phone_ram_3c0c44e4[0xf];
  acStack_1c[0] = s_1_Open_your_phone_ram_3c0c44e4[0x10];
  acStack_1c[1] = s_1_Open_your_phone_ram_3c0c44e4[0x11];
  bVar1 = (*(code *)&SUB_ram_400004a8)();
  if (bVar1 < 0x15) {
    if (bVar1 != 0) goto LAB_ram_42010ca8;
  }
  else {
    bVar1 = 0x14;
LAB_ram_42010ca8:
    draw_ascii_text_at_4200abee((int)(0xf0 - (uint)(byte)(bVar1 * '\f')) >> 1 & 0xfe,0x24,&uStack_2c,0x18,
                     0xffff,0);
  }
  uStack_2c._0_1_ = s_2_Setting_>WLAN_ram_3c0c44f8[0];
  uStack_2c._1_1_ = s_2_Setting_>WLAN_ram_3c0c44f8[1];
  uStack_2c._2_1_ = s_2_Setting_>WLAN_ram_3c0c44f8[2];
  uStack_2c._3_1_ = s_2_Setting_>WLAN_ram_3c0c44f8[3];
  uStack_28._0_1_ = s_2_Setting_>WLAN_ram_3c0c44f8[4];
  uStack_28._1_1_ = s_2_Setting_>WLAN_ram_3c0c44f8[5];
  uStack_28._2_1_ = s_2_Setting_>WLAN_ram_3c0c44f8[6];
  uStack_28._3_1_ = s_2_Setting_>WLAN_ram_3c0c44f8[7];
  uStack_24._0_1_ = s_2_Setting_>WLAN_ram_3c0c44f8[8];
  uStack_24._1_1_ = s_2_Setting_>WLAN_ram_3c0c44f8[9];
  uStack_24._2_1_ = s_2_Setting_>WLAN_ram_3c0c44f8[10];
  uStack_24._3_1_ = s_2_Setting_>WLAN_ram_3c0c44f8[0xb];
  acStack_20[0] = s_2_Setting_>WLAN_ram_3c0c44f8[0xc];
  acStack_20[1] = s_2_Setting_>WLAN_ram_3c0c44f8[0xd];
  acStack_20[2] = s_2_Setting_>WLAN_ram_3c0c44f8[0xe];
  acStack_20[3] = s_2_Setting_>WLAN_ram_3c0c44f8[0xf];
  bVar1 = (*(code *)&SUB_ram_400004a8)();
  if (bVar1 < 0x15) {
    if (bVar1 != 0) goto LAB_ram_42010d00;
  }
  else {
    bVar1 = 0x14;
LAB_ram_42010d00:
    draw_ascii_text_at_4200abee((int)(0xf0 - (uint)(byte)(bVar1 * '\f')) >> 1 & 0xfe,0x40,&uStack_2c,0x18,
                     0xffff,0);
  }
  uStack_2c._0_1_ = s_3_Connect_to_wifi__ram_3c0c4508[0];
  uStack_2c._1_1_ = s_3_Connect_to_wifi__ram_3c0c4508[1];
  uStack_2c._2_1_ = s_3_Connect_to_wifi__ram_3c0c4508[2];
  uStack_2c._3_1_ = s_3_Connect_to_wifi__ram_3c0c4508[3];
  uStack_28._0_1_ = s_3_Connect_to_wifi__ram_3c0c4508[4];
  uStack_28._1_1_ = s_3_Connect_to_wifi__ram_3c0c4508[5];
  uStack_28._2_1_ = s_3_Connect_to_wifi__ram_3c0c4508[6];
  uStack_28._3_1_ = s_3_Connect_to_wifi__ram_3c0c4508[7];
  uStack_24._0_1_ = s_3_Connect_to_wifi__ram_3c0c4508[8];
  uStack_24._1_1_ = s_3_Connect_to_wifi__ram_3c0c4508[9];
  uStack_24._2_1_ = s_3_Connect_to_wifi__ram_3c0c4508[10];
  uStack_24._3_1_ = s_3_Connect_to_wifi__ram_3c0c4508[0xb];
  acStack_20[0] = s_3_Connect_to_wifi__ram_3c0c4508[0xc];
  acStack_20[1] = s_3_Connect_to_wifi__ram_3c0c4508[0xd];
  acStack_20[2] = s_3_Connect_to_wifi__ram_3c0c4508[0xe];
  acStack_20[3] = s_3_Connect_to_wifi__ram_3c0c4508[0xf];
  acStack_1c[0] = s_3_Connect_to_wifi__ram_3c0c4508[0x10];
  acStack_1c[1] = s_3_Connect_to_wifi__ram_3c0c4508[0x11];
  cStack_1a = s_3_Connect_to_wifi__ram_3c0c4508[0x12];
  bVar1 = (*(code *)&SUB_ram_400004a8)();
  if (bVar1 < 0x15) {
    if (bVar1 != 0) goto LAB_ram_42010d68;
  }
  else {
    bVar1 = 0x14;
LAB_ram_42010d68:
    draw_ascii_text_at_4200abee((int)(0xf0 - (uint)(byte)(bVar1 * '\f')) >> 1 & 0xfe,0x5c,&uStack_2c,0x18,
                     0xffff,0);
  }
  uStack_2c = 0x6c616d53;
  uStack_28 = 0x56545f6c;
  uStack_24 = uStack_24 & 0xffffff00;
  bVar1 = (*(code *)&SUB_ram_400004a8)();
  if (bVar1 < 0x15) {
    if (bVar1 != 0) goto LAB_ram_42010dc0;
  }
  else {
    bVar1 = 0x14;
LAB_ram_42010dc0:
    draw_ascii_text_at_4200abee((int)(0xf0 - (uint)(byte)(bVar1 * '\f')) >> 1 & 0xfe,0x78,&uStack_2c,0x18,
                     0xffe0,0);
  }
  uStack_2c._0_1_ = s_4_Use_browser_link_ram_3c0c451c[0];
  uStack_2c._1_1_ = s_4_Use_browser_link_ram_3c0c451c[1];
  uStack_2c._2_1_ = s_4_Use_browser_link_ram_3c0c451c[2];
  uStack_2c._3_1_ = s_4_Use_browser_link_ram_3c0c451c[3];
  uStack_28._0_1_ = s_4_Use_browser_link_ram_3c0c451c[4];
  uStack_28._1_1_ = s_4_Use_browser_link_ram_3c0c451c[5];
  uStack_28._2_1_ = s_4_Use_browser_link_ram_3c0c451c[6];
  uStack_28._3_1_ = s_4_Use_browser_link_ram_3c0c451c[7];
  uStack_24._0_1_ = s_4_Use_browser_link_ram_3c0c451c[8];
  uStack_24._1_1_ = s_4_Use_browser_link_ram_3c0c451c[9];
  uStack_24._2_1_ = s_4_Use_browser_link_ram_3c0c451c[10];
  uStack_24._3_1_ = s_4_Use_browser_link_ram_3c0c451c[0xb];
  acStack_20[0] = s_4_Use_browser_link_ram_3c0c451c[0xc];
  acStack_20[1] = s_4_Use_browser_link_ram_3c0c451c[0xd];
  acStack_20[2] = s_4_Use_browser_link_ram_3c0c451c[0xe];
  acStack_20[3] = s_4_Use_browser_link_ram_3c0c451c[0xf];
  acStack_1c[0] = s_4_Use_browser_link_ram_3c0c451c[0x10];
  acStack_1c[1] = s_4_Use_browser_link_ram_3c0c451c[0x11];
  cStack_1a = s_4_Use_browser_link_ram_3c0c451c[0x12];
  bVar1 = (*(code *)&SUB_ram_400004a8)();
  if (bVar1 < 0x15) {
    if (bVar1 == 0) goto LAB_ram_42010e52;
  }
  else {
    bVar1 = 0x14;
  }
  draw_ascii_text_at_4200abee((int)(0xf0 - (uint)(byte)(bVar1 * '\f')) >> 1 & 0xfe,0x94,&uStack_2c,0x18,0xffff,
                   0);
LAB_ram_42010e52:
  uStack_2c = DAT_ram_3c0c2ae8;
  uStack_28 = DAT_ram_3c0c2aec;
  uStack_24 = DAT_ram_3c0c2af0;
  acStack_20[0] = DAT_ram_3c0c2af4;
  bVar1 = (*(code *)&SUB_ram_400004a8)();
  if (bVar1 < 0x15) {
    if (bVar1 == 0) {
      return;
    }
  }
  else {
    bVar1 = 0x14;
  }
  draw_ascii_text_at_4200abee((int)(0xf0 - (uint)(byte)(bVar1 * '\f')) >> 1 & 0xfe,0xb0,&uStack_2c,0x18,0xffe0,
                   0);
  return;
}
