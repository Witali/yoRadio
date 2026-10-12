/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Executable reconstruction: app/display/clock_ui.c.
 */

// Audit label: application_review; entry: ram:42009a38; name: draw_dial_hand_at_42009a38

void draw_dial_hand_at_42009a38(undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  short sVar1;
  short sVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;

  uVar4 = (*(code *)&SUB_ram_40000a54)(param_2);
  uVar3 = (undefined4)((ulonglong)uVar4 >> 0x20);
  uVar5 = (*(code *)&SUB_ram_40000a2c)(param_1);
  uVar6 = FUN_ram_420a7464();
  uVar6 = (*(code *)&SUB_ram_40000a8c)((int)uVar4,uVar3,(int)uVar6,(int)((ulonglong)uVar6 >> 0x20));
  (*(code *)&SUB_ram_40000a18)
            ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d62e8,DAT_ram_3c0d62ec);
  sVar1 = (*(code *)&SUB_ram_40000a34)();
  uVar5 = FUN_ram_420a73e0((int)uVar5,(int)((ulonglong)uVar5 >> 0x20));
  uVar4 = (*(code *)&SUB_ram_40000a8c)((int)uVar4,uVar3,(int)uVar5,(int)((ulonglong)uVar5 >> 0x20));
  (*(code *)&SUB_ram_40000a9c)
            (DAT_ram_3c0d62e8,DAT_ram_3c0d62ec,(int)uVar4,(int)((ulonglong)uVar4 >> 0x20));
  sVar2 = (*(code *)&SUB_ram_40000a34)();
  draw_thick_line_at_42009644(0x78,0x78,(int)sVar1,(int)sVar2,param_3,param_4 & 0xff);
  if (2 < param_4) {
    draw_filled_circle_at_420095c4((int)sVar1,(int)sVar2,param_4 >> 1,param_3);
  }
  return;
}

// Audit label: application_review; entry: ram:42009b32; name: draw_dial_ticks_at_42009b32

void draw_dial_ticks_at_42009b32(void)

{
  uint uVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  undefined8 uVar10;

  for (uVar1 = 0; (int)uVar1 < 0xc; uVar1 = uVar1 + 1) {
    if ((9 < uVar1) || ((0x249U >> (uVar1 & 0x1f) & 1) == 0)) {
      uVar8 = (*(code *)&SUB_ram_40000a54)(uVar1);
      uVar8 = (*(code *)&SUB_ram_40000a8c)
                        ((int)uVar8,(int)((ulonglong)uVar8 >> 0x20),DAT_ram_3c0d62f0,
                         DAT_ram_3c0d62f4);
      (*(code *)&SUB_ram_400008f4)
                ((int)uVar8,(int)((ulonglong)uVar8 >> 0x20),DAT_ram_3c0d62f8,DAT_ram_3c0d62fc);
      (*(code *)&SUB_ram_40000aa4)();
      uVar8 = (*(code *)&SUB_ram_40000a2c)();
      uVar9 = FUN_ram_420a7464();
      uVar6 = (undefined4)((ulonglong)uVar9 >> 0x20);
      uVar10 = (*(code *)&SUB_ram_40000a8c)((int)uVar9,uVar6,DAT_ram_3c0d6300,DAT_ram_3c0d6304);
      (*(code *)&SUB_ram_40000a18)
                ((int)uVar10,(int)((ulonglong)uVar10 >> 0x20),DAT_ram_3c0d62e8,DAT_ram_3c0d62ec);
      sVar2 = (*(code *)&SUB_ram_40000a34)();
      uVar8 = FUN_ram_420a73e0((int)uVar8,(int)((ulonglong)uVar8 >> 0x20));
      uVar7 = (undefined4)((ulonglong)uVar8 >> 0x20);
      uVar10 = (*(code *)&SUB_ram_40000a8c)((int)uVar8,uVar7,DAT_ram_3c0d6300,DAT_ram_3c0d6304);
      (*(code *)&SUB_ram_40000a9c)
                (DAT_ram_3c0d62e8,DAT_ram_3c0d62ec,(int)uVar10,(int)((ulonglong)uVar10 >> 0x20));
      sVar3 = (*(code *)&SUB_ram_40000a34)();
      uVar9 = (*(code *)&SUB_ram_40000a8c)((int)uVar9,uVar6,DAT_ram_3c0d62e8,DAT_ram_3c0d62ec);
      (*(code *)&SUB_ram_40000a18)
                ((int)uVar9,(int)((ulonglong)uVar9 >> 0x20),DAT_ram_3c0d62e8,DAT_ram_3c0d62ec);
      sVar4 = (*(code *)&SUB_ram_40000a34)();
      uVar8 = (*(code *)&SUB_ram_40000a8c)((int)uVar8,uVar7,DAT_ram_3c0d62e8,DAT_ram_3c0d62ec);
      (*(code *)&SUB_ram_40000a9c)
                (DAT_ram_3c0d62e8,DAT_ram_3c0d62ec,(int)uVar8,(int)((ulonglong)uVar8 >> 0x20));
      sVar5 = (*(code *)&SUB_ram_40000a34)();
      draw_thick_line_at_42009644((int)sVar2,(int)sVar3,(int)sVar4,(int)sVar5,0xffff,4);
    }
  }
  return;
}

// Audit label: application_review; entry: ram:42009ccc; name: update_dial_hands_at_42009ccc

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void update_dial_hands_at_42009ccc(void)

{
  undefined1 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  undefined8 uVar6;
  undefined8 uVar7;

  if (DAT_ram_3fcc39f6 != '\0') {
    DAT_ram_3fcc39f6 = '\0';
    uVar5 = (uint)local_hour_at_3fcbffce;
    uVar2 = (*(code *)&SUB_ram_40000a58)(local_minute_at_3fcbffcf);
    uVar2 = (*(code *)&SUB_ram_40000a20)(uVar2,_DAT_ram_3c0d6620);
    uVar3 = (*(code *)&SUB_ram_40000a58)(uVar5 % 0xc);
    (*(code *)&SUB_ram_40000a1c)(uVar3,uVar2);
    uVar6 = (*(code *)&SUB_ram_40000a2c)();
    uVar6 = (*(code *)&SUB_ram_40000a8c)
                      ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d62f0,DAT_ram_3c0d62f4)
    ;
    (*(code *)&SUB_ram_400008f4)
              ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d62f8,DAT_ram_3c0d62fc);
    DAT_ram_3fcc3a0c = (*(code *)&SUB_ram_40000aa4)();
    uVar6 = (*(code *)&SUB_ram_40000a2c)();
    uVar7 = FUN_ram_420a7464();
    uVar7 = (*(code *)&SUB_ram_40000a8c)
                      ((int)uVar7,(int)((ulonglong)uVar7 >> 0x20),DAT_ram_3c0d6308,DAT_ram_3c0d630c)
    ;
    (*(code *)&SUB_ram_40000a18)
              ((int)uVar7,(int)((ulonglong)uVar7 >> 0x20),DAT_ram_3c0d62e8,DAT_ram_3c0d62ec);
    iVar4 = (*(code *)&SUB_ram_40000a34)();
    DAT_ram_3fcb7d90 = iVar4;
    uVar6 = FUN_ram_420a73e0((int)uVar6,(int)((ulonglong)uVar6 >> 0x20));
    uVar6 = (*(code *)&SUB_ram_40000a8c)
                      ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d6308,DAT_ram_3c0d630c)
    ;
    (*(code *)&SUB_ram_40000a9c)
              (DAT_ram_3c0d62e8,DAT_ram_3c0d62ec,(int)uVar6,(int)((ulonglong)uVar6 >> 0x20));
    DAT_ram_3fcb7d94 = (*(code *)&SUB_ram_40000a34)();
    if ((iVar4 != DAT_ram_3fcb7d78) || (DAT_ram_3fcb7d94 != DAT_ram_3fcb7d7c)) {
      draw_dial_hand_at_42009a38(DAT_ram_3fcc3a00,0x32,0,5);
    }
    uVar1 = local_minute_at_3fcbffcf;
    uVar2 = (*(code *)&SUB_ram_40000a58)(local_second_at_3fcbffd0);
    uVar2 = (*(code *)&SUB_ram_40000a20)(uVar2,_DAT_ram_3c0d6620);
    uVar3 = (*(code *)&SUB_ram_40000a58)(uVar1);
    (*(code *)&SUB_ram_40000a1c)(uVar3,uVar2);
    uVar6 = (*(code *)&SUB_ram_40000a2c)();
    uVar6 = (*(code *)&SUB_ram_40000a8c)
                      ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d62f0,DAT_ram_3c0d62f4)
    ;
    (*(code *)&SUB_ram_400008f4)
              ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d6310,DAT_ram_3c0d6314);
    DAT_ram_3fcc3a10 = (*(code *)&SUB_ram_40000aa4)();
    uVar6 = (*(code *)&SUB_ram_40000a2c)();
    uVar7 = FUN_ram_420a7464();
    uVar7 = (*(code *)&SUB_ram_40000a8c)
                      ((int)uVar7,(int)((ulonglong)uVar7 >> 0x20),DAT_ram_3c0d6318,DAT_ram_3c0d631c)
    ;
    (*(code *)&SUB_ram_40000a18)
              ((int)uVar7,(int)((ulonglong)uVar7 >> 0x20),DAT_ram_3c0d62e8,DAT_ram_3c0d62ec);
    iVar4 = (*(code *)&SUB_ram_40000a34)();
    DAT_ram_3fcb7d98 = iVar4;
    uVar6 = FUN_ram_420a73e0((int)uVar6,(int)((ulonglong)uVar6 >> 0x20));
    uVar6 = (*(code *)&SUB_ram_40000a8c)
                      ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d6318,DAT_ram_3c0d631c)
    ;
    (*(code *)&SUB_ram_40000a9c)
              (DAT_ram_3c0d62e8,DAT_ram_3c0d62ec,(int)uVar6,(int)((ulonglong)uVar6 >> 0x20));
    DAT_ram_3fcb7d9c = (*(code *)&SUB_ram_40000a34)();
    if ((iVar4 != DAT_ram_3fcb7d80) || (DAT_ram_3fcb7d9c != DAT_ram_3fcb7d84)) {
      draw_dial_hand_at_42009a38(DAT_ram_3fcc3a04,0x46,0,5);
    }
    uVar6 = (*(code *)&SUB_ram_40000a54)(local_second_at_3fcbffd0);
    uVar6 = (*(code *)&SUB_ram_40000a8c)
                      ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d62f0,DAT_ram_3c0d62f4)
    ;
    (*(code *)&SUB_ram_400008f4)
              ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d6310,DAT_ram_3c0d6314);
    DAT_ram_3fcc3a14 = (*(code *)&SUB_ram_40000aa4)();
    uVar6 = (*(code *)&SUB_ram_40000a2c)();
    uVar7 = FUN_ram_420a7464();
    uVar7 = (*(code *)&SUB_ram_40000a8c)
                      ((int)uVar7,(int)((ulonglong)uVar7 >> 0x20),DAT_ram_3c0d6320,DAT_ram_3c0d6324)
    ;
    (*(code *)&SUB_ram_40000a18)
              ((int)uVar7,(int)((ulonglong)uVar7 >> 0x20),DAT_ram_3c0d62e8,DAT_ram_3c0d62ec);
    iVar4 = (*(code *)&SUB_ram_40000a34)();
    DAT_ram_3fcb7da0 = iVar4;
    uVar6 = FUN_ram_420a73e0((int)uVar6,(int)((ulonglong)uVar6 >> 0x20));
    uVar6 = (*(code *)&SUB_ram_40000a8c)
                      ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d6320,DAT_ram_3c0d6324)
    ;
    (*(code *)&SUB_ram_40000a9c)
              (DAT_ram_3c0d62e8,DAT_ram_3c0d62ec,(int)uVar6,(int)((ulonglong)uVar6 >> 0x20));
    DAT_ram_3fcb7da4 = (*(code *)&SUB_ram_40000a34)();
    if ((iVar4 != DAT_ram_3fcb7d88) || (DAT_ram_3fcb7da4 != DAT_ram_3fcb7d8c)) {
      draw_dial_hand_at_42009a38(DAT_ram_3fcc3a08,0x5a,0,5);
    }
    draw_dial_hand_at_42009a38(DAT_ram_3fcc3a0c,0x32,0xf800,5);
    draw_dial_hand_at_42009a38(DAT_ram_3fcc3a10,0x46,0xffe0,5);
    draw_dial_hand_at_42009a38(DAT_ram_3fcc3a14,0x5a,0xffff,3);
    draw_filled_circle_at_420095c4(0x78,0x78,6,0xffff);
    DAT_ram_3fcc3a08 = DAT_ram_3fcc3a14;
    DAT_ram_3fcc3a04 = DAT_ram_3fcc3a10;
    DAT_ram_3fcc3a00 = DAT_ram_3fcc3a0c;
    DAT_ram_3fcb7d88 = DAT_ram_3fcb7da0;
    DAT_ram_3fcb7d8c = DAT_ram_3fcb7da4;
    DAT_ram_3fcb7d80 = DAT_ram_3fcb7d98;
    DAT_ram_3fcb7d84 = DAT_ram_3fcb7d9c;
    DAT_ram_3fcb7d78 = DAT_ram_3fcb7d90;
    DAT_ram_3fcb7d7c = DAT_ram_3fcb7d94;
    draw_encoded_text_at_4200aa1e(5,0xe1,&DAT_ram_3fcb7b84,0x10,0xffff);
  }
  return;
}

// Audit label: application_review; entry: ram:4200a156; name: initialize_dial_clock_at_4200a156

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void initialize_dial_clock_at_4200a156(void)

{
  byte bVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  undefined1 uStack_48;
  undefined1 uStack_47;
  undefined1 uStack_46;

  DAT_ram_3fcc3a20 = (uint)local_second_at_3fcbffd0;
  DAT_ram_3fcc3a1c = (uint)local_minute_at_3fcbffcf;
  DAT_ram_3fcc3a18 = (uint)local_hour_at_3fcbffce;
  clear_display_at_42009a0a(0);
  draw_dial_ticks_at_42009b32();
  bVar1 = local_second_at_3fcbffd0;
  uVar5 = (*(code *)&SUB_ram_40000a54)(local_second_at_3fcbffd0);
  uVar5 = (*(code *)&SUB_ram_40000a8c)
                    ((int)uVar5,(int)((ulonglong)uVar5 >> 0x20),DAT_ram_3c0d62f0,DAT_ram_3c0d62f4);
  (*(code *)&SUB_ram_400008f4)
            ((int)uVar5,(int)((ulonglong)uVar5 >> 0x20),DAT_ram_3c0d6310,DAT_ram_3c0d6314);
  DAT_ram_3fcc3a14 = (*(code *)&SUB_ram_40000aa4)();
  uVar5 = (*(code *)&SUB_ram_40000a2c)();
  uVar6 = FUN_ram_420a7464();
  uVar6 = (*(code *)&SUB_ram_40000a8c)
                    ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d6320,DAT_ram_3c0d6324);
  (*(code *)&SUB_ram_40000a18)
            ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d62e8,DAT_ram_3c0d62ec);
  DAT_ram_3fcb7da0 = (*(code *)&SUB_ram_40000a34)();
  uVar5 = FUN_ram_420a73e0((int)uVar5,(int)((ulonglong)uVar5 >> 0x20));
  uVar5 = (*(code *)&SUB_ram_40000a8c)
                    ((int)uVar5,(int)((ulonglong)uVar5 >> 0x20),DAT_ram_3c0d6320,DAT_ram_3c0d6324);
  (*(code *)&SUB_ram_40000a9c)
            (DAT_ram_3c0d62e8,DAT_ram_3c0d62ec,(int)uVar5,(int)((ulonglong)uVar5 >> 0x20));
  DAT_ram_3fcb7da4 = (*(code *)&SUB_ram_40000a34)();
  uVar2 = (*(code *)&SUB_ram_40000a58)(local_minute_at_3fcbffcf);
  uVar3 = (*(code *)&SUB_ram_40000a58)(bVar1);
  uVar3 = (*(code *)&SUB_ram_40000a20)(uVar3,_DAT_ram_3c0d6620);
  (*(code *)&SUB_ram_40000a1c)(uVar2,uVar3);
  uVar5 = (*(code *)&SUB_ram_40000a2c)();
  uVar5 = (*(code *)&SUB_ram_40000a8c)
                    ((int)uVar5,(int)((ulonglong)uVar5 >> 0x20),DAT_ram_3c0d62f0,DAT_ram_3c0d62f4);
  (*(code *)&SUB_ram_400008f4)
            ((int)uVar5,(int)((ulonglong)uVar5 >> 0x20),DAT_ram_3c0d6310,DAT_ram_3c0d6314);
  DAT_ram_3fcc3a10 = (*(code *)&SUB_ram_40000aa4)();
  uVar5 = (*(code *)&SUB_ram_40000a2c)();
  uVar6 = FUN_ram_420a7464();
  uVar6 = (*(code *)&SUB_ram_40000a8c)
                    ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d6318,DAT_ram_3c0d631c);
  (*(code *)&SUB_ram_40000a18)
            ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d62e8,DAT_ram_3c0d62ec);
  DAT_ram_3fcb7d98 = (*(code *)&SUB_ram_40000a34)();
  uVar5 = FUN_ram_420a73e0((int)uVar5,(int)((ulonglong)uVar5 >> 0x20));
  uVar5 = (*(code *)&SUB_ram_40000a8c)
                    ((int)uVar5,(int)((ulonglong)uVar5 >> 0x20),DAT_ram_3c0d6318,DAT_ram_3c0d631c);
  (*(code *)&SUB_ram_40000a9c)
            (DAT_ram_3c0d62e8,DAT_ram_3c0d62ec,(int)uVar5,(int)((ulonglong)uVar5 >> 0x20));
  DAT_ram_3fcb7d9c = (*(code *)&SUB_ram_40000a34)();
  uVar4 = (uint)local_hour_at_3fcbffce;
  uVar2 = (*(code *)&SUB_ram_40000a20)(uVar2,_DAT_ram_3c0d6620);
  uVar3 = (*(code *)&SUB_ram_40000a58)(uVar4 % 0xc);
  (*(code *)&SUB_ram_40000a1c)(uVar3,uVar2);
  uVar5 = (*(code *)&SUB_ram_40000a2c)();
  uVar5 = (*(code *)&SUB_ram_40000a8c)
                    ((int)uVar5,(int)((ulonglong)uVar5 >> 0x20),DAT_ram_3c0d62f0,DAT_ram_3c0d62f4);
  (*(code *)&SUB_ram_400008f4)
            ((int)uVar5,(int)((ulonglong)uVar5 >> 0x20),DAT_ram_3c0d62f8,DAT_ram_3c0d62fc);
  uVar2 = (*(code *)&SUB_ram_40000aa4)();
  DAT_ram_3fcc3a0c = uVar2;
  uVar5 = (*(code *)&SUB_ram_40000a2c)();
  uVar6 = FUN_ram_420a7464();
  uVar6 = (*(code *)&SUB_ram_40000a8c)
                    ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d6308,DAT_ram_3c0d630c);
  (*(code *)&SUB_ram_40000a18)
            ((int)uVar6,(int)((ulonglong)uVar6 >> 0x20),DAT_ram_3c0d62e8,DAT_ram_3c0d62ec);
  DAT_ram_3fcb7d90 = (*(code *)&SUB_ram_40000a34)();
  uVar5 = FUN_ram_420a73e0((int)uVar5,(int)((ulonglong)uVar5 >> 0x20));
  uVar5 = (*(code *)&SUB_ram_40000a8c)
                    ((int)uVar5,(int)((ulonglong)uVar5 >> 0x20),DAT_ram_3c0d6308,DAT_ram_3c0d630c);
  (*(code *)&SUB_ram_40000a9c)
            (DAT_ram_3c0d62e8,DAT_ram_3c0d62ec,(int)uVar5,(int)((ulonglong)uVar5 >> 0x20));
  DAT_ram_3fcb7d94 = (*(code *)&SUB_ram_40000a34)();
  draw_dial_hand_at_42009a38(uVar2,0x32,0xf800,5);
  draw_dial_hand_at_42009a38(DAT_ram_3fcc3a10,0x46,0xffe0,5);
  draw_dial_hand_at_42009a38(DAT_ram_3fcc3a14,0x5a,0xffff,3);
  DAT_ram_3fcc3a08 = DAT_ram_3fcc3a14;
  DAT_ram_3fcc3a04 = DAT_ram_3fcc3a10;
  DAT_ram_3fcc3a00 = DAT_ram_3fcc3a0c;
  DAT_ram_3fcb7d88 = DAT_ram_3fcb7da0;
  DAT_ram_3fcb7d8c = DAT_ram_3fcb7da4;
  DAT_ram_3fcb7d80 = DAT_ram_3fcb7d98;
  DAT_ram_3fcb7d84 = DAT_ram_3fcb7d9c;
  DAT_ram_3fcb7d78 = DAT_ram_3fcb7d90;
  DAT_ram_3fcb7d7c = DAT_ram_3fcb7d94;
  uStack_48 = 0x31;
  uStack_47 = 0x32;
  uStack_46 = 0;
  draw_ascii_text_at_4200abee(0x68,0,&uStack_48,0x20,0xffff,0);
  uStack_48 = 0x39;
  uStack_47 = 0;
  uStack_46 = 0;
  draw_ascii_text_at_4200abee(0,0x68,&uStack_48,0x20,0xffff,0);
  uStack_48 = 0x33;
  uStack_47 = 0;
  uStack_46 = 0;
  draw_ascii_text_at_4200abee(0xe0,0x68,&uStack_48,0x20,0xffff,0);
  uStack_48 = 0x36;
  uStack_47 = 0;
  uStack_46 = 0;
  draw_ascii_text_at_4200abee(0x68,0xd0,&uStack_48,0x20,0xffff,0);
  draw_encoded_text_at_4200aa1e(5,0xe1,&DAT_ram_3fcb7b84,0x10,0xffff);
  DAT_ram_3fcc39f7 = 1;
  DAT_ram_3fcc39f6 = 1;
  DAT_ram_3fcc39f5 = 1;
  return;
}

// Audit label: application_review; entry: ram:4200a5b0; name: render_dial_clock_at_4200a5b0

void render_dial_clock_at_4200a5b0(void)

{
  update_dial_hands_at_42009ccc();
  return;
}
