# Experimental decoder-only clt_compute_allocation, accepted GCC ASM.
# LX106 call0 ABI; original192-byte frame, callee saves and all integer arithmetic.
# encode=0 follows the checked private native decoder contract, not bitrate.
# C and original saved GCC remain unchanged. RAM/stack/layout do not grow.
# Removed encoder instructions remain documented at their original labels.
.section .text.patch0,"ax",@progbits
.begin no-transform
pc402482b0:
movi a9, 192 # original0x402482b0
pc402482b3:
sub a1, a1, a9 # original0x402482b3
pc402482b6:
s32i a12, a1, 184 # original0x402482b6
pc402482b9:
s32i a13, a1, 180 # original0x402482b9
pc402482bc:
s32i a5, a1, 120 # original0x402482bc
pc402482bf:
l32i a13, a1, 200 # original0x402482bf
pc402482c2:
s32i a0, a1, 188 # original0x402482c2
pc402482c5:
s32i a14, a1, 176 # original0x402482c5
pc402482c8:
s32i a15, a1, 172 # original0x402482c8
pc402482cb:
s32i.n a2, a1, 36 # original0x402482cb
pc402482cd:
s32i.n a3, a1, 32 # original0x402482cd
pc402482cf:
s32i.n a4, a1, 56 # original0x402482cf
pc402482d1:
s32i a6, a1, 84 # original0x402482d1
pc402482d4:
mov.n a12, a7 # original0x402482d4
pc402482d6:
call0 fixed_402428c4 # original0x402482d6
pc402482d9:
l32i.n a8, a1, 36 # original0x402482d9
pc402482db:
s32i.n a2, a1, 8 # original0x402482db
pc402482dd:
movi.n a2, 0 # original0x402482dd
pc402482df:
mov.n a5, a2 # original0x402482df
pc402482e1:
l32i.n a8, a8, 8 # original0x402482e1
pc402482e3:
movgez a5, a13, a13 # original0x402482e3
pc402482e6:
s32i.n a3, a1, 12 # original0x402482e6
pc402482e8:
s32i.n a5, a1, 44 # original0x402482e8
pc402482ea:
s32i.n a8, a1, 52 # original0x402482ea
pc402482ec:
s32i a2, a1, 124 # original0x402482ec
pc402482ef:
blti a13, 8, pc402482fc # original0x402482ef
pc402482f2:
addi a5, a5, -8 # original0x402482f2
pc402482f5:
movi.n a14, 8 # original0x402482f5
pc402482f7:
s32i.n a5, a1, 44 # original0x402482f7
pc402482f9:
s32i a14, a1, 124 # original0x402482f9
pc402482fc:
movi.n a5, 0 # original0x402482fc
pc402482fe:
l32i a7, a1, 220 # original0x402482fe
pc40248301:
s32i a5, a1, 112 # original0x40248301
pc40248304:
s32i a5, a1, 96 # original0x40248304
pc40248307:
bnei a7, 2, pc4024833e # original0x40248307
pc4024830a:
l32i.n a8, a1, 56 # original0x4024830a
pc4024830c:
l32i.n a14, a1, 32 # original0x4024830c
pc4024830e:
l32r a2, fixed_4021191c # original0x4024830e
pc40248311:
sub a3, a8, a14 # original0x40248311
pc40248314:
add.n a2, a2, a3 # original0x40248314
pc40248316:
l8ui a2, a2, 0 # original0x40248316
pc40248319:
l32i.n a5, a1, 44 # original0x40248319
pc4024831b:
s32i a2, a1, 96 # original0x4024831b
pc4024831e:
blt a5, a2, pc40248338 # original0x4024831e
pc40248321:
sub a5, a5, a2 # original0x40248321
pc40248324:
s32i.n a5, a1, 44 # original0x40248324
pc40248326:
blti a5, 8, pc4024833e # original0x40248326
pc40248329:
addi a5, a5, -8 # original0x40248329
pc4024832c:
movi.n a7, 8 # original0x4024832c
pc4024832e:
s32i.n a5, a1, 44 # original0x4024832e
pc40248330:
s32i a7, a1, 112 # original0x40248330
pc40248333:
j pc4024833e # original0x40248333
pc40248338:
l32i a8, a1, 112 # original0x40248338
pc4024833b:
s32i a8, a1, 96 # original0x4024833b
pc4024833e:
l32i.n a2, a1, 52 # original0x4024833e
pc40248340:
movi.n a4, 1 # original0x40248340
pc40248342:
movi.n a3, 4 # original0x40248342
pc40248344:
call0 fixed_402428ec # original0x40248344
pc40248347:
s32i.n a2, a1, 16 # original0x40248347
pc40248349:
l32i.n a2, a1, 52 # original0x40248349
pc4024834b:
movi.n a4, 1 # original0x4024834b
pc4024834d:
movi a3, 4 # original0x4024834d
pc40248350:
call0 fixed_402428ec # original0x40248350
pc40248353:
s32i a2, a1, 104 # original0x40248353
pc40248356:
l32i.n a2, a1, 52 # original0x40248356
pc40248358:
movi.n a4, 1 # original0x40248358
pc4024835a:
movi a3, 4 # original0x4024835a
pc4024835d:
call0 fixed_402428ec # original0x4024835d
pc40248360:
s32i a2, a1, 100 # original0x40248360
pc40248363:
l32i.n a2, a1, 52 # original0x40248363
pc40248365:
movi.n a4, 1 # original0x40248365
pc40248367:
movi.n a3, 4 # original0x40248367
pc40248369:
call0 fixed_402428ec # original0x40248369
pc4024836c:
l32i a14, a1, 220 # original0x4024836c
pc4024836f:
l32i.n a5, a1, 56 # original0x4024836f
pc40248371:
slli a14, a14, 3 # original0x40248371
pc40248374:
s32i.n a14, a1, 24 # original0x40248374
pc40248376:
addi.n a5, a5, -1 # original0x40248376
pc40248378:
l32i.n a8, a1, 32 # original0x40248378
pc4024837a:
l32i.n a14, a1, 56 # original0x4024837a
pc4024837c:
s32i a2, a1, 108 # original0x4024837c
pc4024837f:
s32i.n a5, a1, 60 # original0x4024837f
pc40248381:
blt a8, a14, pc402483d9 # original0x40248381
pc40248384:
slli a5, a8, 1 # original0x40248384
pc40248387:
s32i a5, a1, 64 # original0x40248387
pc4024838a:
l32i.n a8, a1, 36 # original0x4024838a
pc4024838c:
l32i.n a4, a1, 60 # original0x4024838c
pc4024838e:
l32i.n a8, a8, 40 # original0x4024838e
pc40248390:
movi.n a2, 1 # original0x40248390
pc40248392:
addi.n a3, a8, -1 # original0x40248392
pc40248394:
l32i.n a14, a1, 60 # original0x40248394
pc40248396:
s32i.n a2, a1, 28 # original0x40248396
pc40248398:
ssl a2 # original0x40248398
pc4024839b:
sll a4, a4 # original0x4024839b
pc4024839e:
s32i a8, a1, 116 # original0x4024839e
pc402483a1:
s32i.n a3, a1, 48 # original0x402483a1
pc402483a3:
l32i a5, a1, 84 # original0x402483a3
pc402483a6:
l32i a7, a1, 120 # original0x402483a6
pc402483a9:
l32i a8, a1, 100 # original0x402483a9
pc402483ac:
l32i a2, a1, 108 # original0x402483ac
pc402483af:
l32i a3, a1, 64 # original0x402483af
pc402483b2:
slli a14, a14, 2 # original0x402483b2
pc402483b5:
add.n a5, a5, a14 # original0x402483b5
pc402483b7:
add.n a7, a7, a14 # original0x402483b7
pc402483b9:
add.n a8, a8, a14 # original0x402483b9
pc402483bb:
s32i a14, a1, 72 # original0x402483bb
pc402483be:
addi a3, a3, -2 # original0x402483be
pc402483c1:
add.n a14, a2, a14 # original0x402483c1
pc402483c3:
s32i a4, a1, 92 # original0x402483c3
pc402483c6:
s32i a5, a1, 88 # original0x402483c6
pc402483c9:
s32i a7, a1, 76 # original0x402483c9
pc402483cc:
s32i.n a8, a1, 20 # original0x402483cc
pc402483ce:
s32i a14, a1, 68 # original0x402483ce
pc402483d1:
s32i a3, a1, 80 # original0x402483d1
pc402483d4:
l32i.n a15, a1, 28 # original0x402483d4
pc402483d6:
j pc40248469 # original0x402483d6
pc402483d9:
l32i.n a8, a1, 36 # original0x402483d9
pc402483db:
mov.n a14, a5 # original0x402483db
pc402483dd:
l32i a5, a1, 224 # original0x402483dd
pc402483e0:
mov.n a3, a2 # original0x402483e0
pc402483e2:
addi a9, a12, -5 # original0x402483e2
pc402483e5:
l32i.n a2, a8, 24 # original0x402483e5
pc402483e7:
l32i a7, a1, 220 # original0x402483e7
pc402483ea:
l32i.n a8, a1, 32 # original0x402483ea
pc402483ec:
sub a9, a9, a5 # original0x402483ec
pc402483ef:
slli a6, a8, 2 # original0x402483ef
pc402483f2:
mull a9, a9, a7 # original0x402483f2
pc402483f5:
sub a7, a14, a8 # original0x402483f5
pc402483f8:
slli a14, a8, 1 # original0x402483f8
pc402483fb:
l32i.n a8, a1, 56 # original0x402483fb
pc402483fd:
s32i a14, a1, 64 # original0x402483fd
pc40248400:
addi.n a11, a5, 3 # original0x40248400
pc40248402:
add.n a5, a2, a14 # original0x40248402
pc40248404:
l32i a14, a1, 100 # original0x40248404
pc40248407:
slli a10, a8, 1 # original0x40248407
pc4024840a:
mull a7, a7, a9 # original0x4024840a
pc4024840d:
l32i.n a12, a1, 24 # original0x4024840d
pc4024840f:
l32i a4, a1, 224 # original0x4024840f
pc40248412:
add.n a8, a14, a6 # original0x40248412
pc40248414:
add.n a10, a2, a10 # original0x40248414
pc40248416:
add.n a6, a3, a6 # original0x40248416
pc40248418:
call0 fixed_4024dd48 # original0x40248418
pc4024841b:
nop  # original0x4024841b
pc4024841e:
sub a3, a3, a2 # original0x4024841e
pc40248421:
slli a2, a3, 1 # original0x40248421
pc40248424:
add.n a2, a2, a3 # original0x40248424
pc40248426:
ssl a4 # original0x40248426
pc40248429:
sll a2, a2 # original0x40248429
pc4024842c:
mull a13, a7, a3 # original0x4024842c
pc4024842f:
slli a2, a2, 3 # original0x4024842f
pc40248432:
srai a2, a2, 4 # original0x40248432
pc40248435:
ssl a11 # original0x40248435
pc40248438:
sll a13, a13 # original0x40248438
pc4024843b:
ssl a4 # original0x4024843b
pc4024843e:
sll a3, a3 # original0x4024843e
pc40248441:
bge a2, a12, pc40248446 # original0x40248441
pc40248444:
mov.n a2, a12 # original0x40248444
pc40248446:
s32i.n a2, a8, 0 # original0x40248446
pc40248448:
srai a2, a13, 6 # original0x40248448
pc4024844b:
bnei a3, 1, pc40248456 # original0x4024844b
pc4024844e:
sub a2, a2, a12 # original0x4024844e
pc40248451:
s32i.n a2, a6, 0 # original0x40248451
pc40248453:
j pc40248458 # original0x40248453
pc40248456:
s32i.n a2, a6, 0 # original0x40248456
pc40248458:
addi.n a5, a5, 2 # original0x40248458
pc4024845a:
addi.n a8, a8, 4 # original0x4024845a
pc4024845c:
sub a7, a7, a9 # original0x4024845c
pc4024845f:
addi.n a6, a6, 4 # original0x4024845f
pc40248461:
bne a10, a5, pc40248418 # original0x40248461
pc40248464:
j pc4024838a # original0x40248464
pc40248469:
l32i.n a4, a1, 28 # original0x40248469
pc4024846b:
l32i.n a5, a1, 48 # original0x4024846b
pc4024846d:
l32i.n a7, a1, 52 # original0x4024846d
pc4024846f:
add.n a2, a4, a5 # original0x4024846f
pc40248471:
srai a2, a2, 1 # original0x40248471
pc40248474:
l32i.n a8, a1, 32 # original0x40248474
pc40248476:
l32i.n a14, a1, 56 # original0x40248476
pc40248478:
s32i.n a2, a1, 40 # original0x40248478
pc4024847a:
mull a2, a7, a2 # original0x4024847a
pc4024847d:
blt a8, a14, pc40248483 # original0x4024847d
pc40248480:
j pc40248510 # original0x40248480
pc40248483:
l32i.n a8, a1, 36 # original0x40248483
pc40248485:
l32i a7, a1, 80 # original0x40248485
pc40248488:
l32i.n a13, a8, 24 # original0x40248488
pc4024848a:
l32i.n a14, a1, 60 # original0x4024848a
pc4024848c:
l32i a4, a1, 92 # original0x4024848c
pc4024848f:
l32i.n a5, a8, 44 # original0x4024848f
pc40248491:
add.n a2, a2, a14 # original0x40248491
pc40248493:
movi.n a10, 0 # original0x40248493
pc40248495:
add.n a3, a13, a4 # original0x40248495
pc40248497:
l32i a9, a1, 68 # original0x40248497
pc4024849a:
add.n a13, a13, a7 # original0x4024849a
pc4024849c:
l32i a6, a1, 76 # original0x4024849c
pc4024849f:
l32i.n a7, a1, 20 # original0x4024849f
pc402484a1:
l32i a8, a1, 88 # original0x402484a1
pc402484a4:
add.n a5, a5, a2 # original0x402484a4
pc402484a6:
mov.n a12, a10 # original0x402484a6
pc402484a8:
l32i a14, a1, 220 # original0x402484a8
pc402484ab:
call0 fixed_4024dd90 # original0x402484ab
pc402484ae:
call0 fixed_4024dcc4 # original0x402484ae
pc402484b1:
nop  # original0x402484b1
pc402484b4:
mull a4, a4, a14 # original0x402484b4
pc402484b7:
sub a2, a2, a11 # original0x402484b7
pc402484ba:
mull a4, a2, a4 # original0x402484ba
pc402484bd:
l32i a14, a1, 224 # original0x402484bd
pc402484c0:
ssl a14 # original0x402484c0
pc402484c3:
sll a4, a4 # original0x402484c3
pc402484c6:
srai a4, a4, 2 # original0x402484c6
pc402484c9:
blti a4, 1, pc402484d5 # original0x402484c9
pc402484cc:
l32i.n a2, a9, 0 # original0x402484cc
pc402484ce:
add.n a4, a4, a2 # original0x402484ce
pc402484d0:
movi.n a2, 0 # original0x402484d0
pc402484d2:
movltz a4, a2, a4 # original0x402484d2
pc402484d5:
l32i.n a2, a6, 0 # original0x402484d5
pc402484d7:
l32i.n a11, a7, 0 # original0x402484d7
pc402484d9:
add.n a4, a4, a2 # original0x402484d9
pc402484db:
bge a4, a11, pc402484e0 # original0x402484db
pc402484de:
beqz.n a12, pc402484ee # original0x402484de
pc402484e0:
l32i.n a2, a8, 0 # original0x402484e0
pc402484e2:
mov.n a12, a15 # original0x402484e2
pc402484e4:
bge a4, a2, pc402484e9 # original0x402484e4
pc402484e7:
mov.n a2, a4 # original0x402484e7
pc402484e9:
add.n a10, a10, a2 # original0x402484e9
pc402484eb:
j pc402484f8 # original0x402484eb
pc402484ee:
l32i.n a14, a1, 24 # original0x402484ee
pc402484f0:
movi.n a12, 0 # original0x402484f0
pc402484f2:
blt a4, a14, pc402484f8 # original0x402484f2
pc402484f5:
add a10, a10, a14 # original0x402484f5
pc402484f8:
addi a3, a3, -2 # original0x402484f8
pc402484fb:
addi.n a5, a5, -1 # original0x402484fb
pc402484fd:
addi a8, a8, -4 # original0x402484fd
pc40248500:
addi a6, a6, -4 # original0x40248500
pc40248503:
addi a7, a7, -4 # original0x40248503
pc40248506:
addi a9, a9, -4 # original0x40248506
pc40248509:
bne a13, a3, pc402484a8 # original0x40248509
pc4024850c:
j pc40248512 # original0x4024850c
pc40248510:
movi.n a10, 0 # original0x40248510
pc40248512:
l32i.n a5, a1, 44 # original0x40248512
pc40248514:
bge a5, a10, pc40248528 # original0x40248514
pc40248517:
l32i.n a7, a1, 40 # original0x40248517
pc40248519:
l32i.n a8, a1, 28 # original0x40248519
pc4024851b:
addi.n a7, a7, -1 # original0x4024851b
pc4024851d:
s32i.n a7, a1, 48 # original0x4024851d
pc4024851f:
blt a7, a8, pc40248525 # original0x4024851f
pc40248522:
j pc40248469 # original0x40248522
pc40248525:
j pc40248536 # original0x40248525
pc40248528:
l32i.n a14, a1, 40 # original0x40248528
pc4024852a:
l32i.n a2, a1, 48 # original0x4024852a
pc4024852c:
addi.n a14, a14, 1 # original0x4024852c
pc4024852e:
s32i.n a14, a1, 28 # original0x4024852e
pc40248530:
blt a2, a14, pc40248536 # original0x40248530
pc40248533:
j pc40248469 # original0x40248533
pc40248536:
l32i.n a3, a1, 28 # original0x40248536
pc40248538:
l32i.n a8, a1, 32 # original0x40248538
pc4024853a:
l32i.n a14, a1, 56 # original0x4024853a
pc4024853c:
addi.n a13, a3, -1 # original0x4024853c
pc4024853e:
blt a8, a14, pc40248544 # original0x4024853e
pc40248541:
j pc4024861a # original0x40248541
pc40248544:
l32i.n a5, a1, 52 # original0x40248544
pc40248546:
mov.n a4, a8 # original0x40248546
pc40248548:
l32i.n a8, a1, 36 # original0x40248548
pc4024854a:
mull a14, a5, a13 # original0x4024854a
pc4024854d:
l32i.n a5, a8, 24 # original0x4024854d
pc4024854f:
l32i.n a8, a1, 32 # original0x4024854f
pc40248551:
l32i.n a7, a1, 52 # original0x40248551
pc40248553:
slli a6, a8, 2 # original0x40248553
pc40248556:
l32i.n a8, a1, 36 # original0x40248556
pc40248558:
add.n a15, a14, a7 # original0x40248558
pc4024855a:
l32i.n a12, a8, 44 # original0x4024855a
pc4024855c:
l32i a8, a1, 64 # original0x4024855c
pc4024855f:
l32i.n a7, a1, 16 # original0x4024855f
pc40248561:
add.n a5, a5, a8 # original0x40248561
pc40248563:
l32i a2, a1, 120 # original0x40248563
pc40248566:
l32i a8, a1, 104 # original0x40248566
pc40248569:
l32i a3, a1, 108 # original0x40248569
pc4024856c:
s32i.n a15, a1, 52 # original0x4024856c
pc4024856e:
s32i.n a13, a1, 48 # original0x4024856e
pc40248570:
l32i a15, a1, 116 # original0x40248570
pc40248573:
l32i a13, a1, 224 # original0x40248573
pc40248576:
add.n a9, a8, a6 # original0x40248576
pc40248578:
add.n a10, a7, a6 # original0x40248578
pc4024857a:
add.n a8, a2, a6 # original0x4024857a
pc4024857c:
s32i.n a4, a1, 40 # original0x4024857c
pc4024857e:
add.n a6, a3, a6 # original0x4024857e
pc40248580:
movi.n a11, 0 # original0x40248580
pc40248582:
s32i a14, a1, 68 # original0x40248582
pc40248585:
call0 fixed_4024dd6c # original0x40248585
pc40248588:
l32i a14, a1, 68 # original0x40248588
pc4024858b:
nop  # original0x4024858b
pc4024858e:
add.n a3, a14, a4 # original0x4024858e
pc40248590:
sub a2, a7, a2 # original0x40248590
pc40248593:
l32i a7, a1, 220 # original0x40248593
pc40248596:
add.n a3, a12, a3 # original0x40248596
pc40248598:
mull a2, a2, a7 # original0x40248598
pc4024859b:
l8ui a3, a3, 0 # original0x4024859b
pc4024859e:
l32i.n a14, a1, 28 # original0x4024859e
pc402485a0:
mull a3, a3, a2 # original0x402485a0
pc402485a3:
ssl a13 # original0x402485a3
pc402485a6:
sll a3, a3 # original0x402485a6
pc402485a9:
srai a3, a3, 2 # original0x402485a9
pc402485ac:
blt a14, a15, pc402485be # original0x402485ac
pc402485af:
l32i a14, a1, 84 # original0x402485af
pc402485b2:
slli a2, a4, 2 # original0x402485b2
pc402485b5:
add.n a2, a14, a2 # original0x402485b5
pc402485b7:
l32i.n a2, a2, 0 # original0x402485b7
pc402485b9:
j pc402485d3 # original0x402485b9
pc402485be:
l32i.n a7, a1, 52 # original0x402485be
pc402485c0:
add.n a14, a7, a4 # original0x402485c0
pc402485c2:
add.n a7, a12, a14 # original0x402485c2
pc402485c4:
l8ui a7, a7, 0 # original0x402485c4
pc402485c7:
mull a2, a7, a2 # original0x402485c7
pc402485ca:
ssl a13 # original0x402485ca
pc402485cd:
sll a2, a2 # original0x402485cd
pc402485d0:
srai a2, a2, 2 # original0x402485d0
pc402485d3:
blti a3, 1, pc402485dd # original0x402485d3
pc402485d6:
l32i.n a7, a6, 0 # original0x402485d6
pc402485d8:
add.n a3, a3, a7 # original0x402485d8
pc402485da:
movltz a3, a11, a3 # original0x402485da
pc402485dd:
blti a2, 1, pc402485e8 # original0x402485dd
pc402485e0:
l32i.n a7, a6, 0 # original0x402485e0
pc402485e2:
add a2, a2, a7 # original0x402485e2
pc402485e5:
movltz a2, a11, a2 # original0x402485e5
pc402485e8:
l32i.n a14, a1, 48 # original0x402485e8
pc402485ea:
l32i.n a7, a8, 0 # original0x402485ea
pc402485ec:
blti a14, 1, pc402485f1 # original0x402485ec
pc402485ef:
add.n a3, a3, a7 # original0x402485ef
pc402485f1:
add.n a2, a2, a7 # original0x402485f1
pc402485f3:
blti a7, 1, pc402485f8 # original0x402485f3
pc402485f6:
s32i.n a4, a1, 40 # original0x402485f6
pc402485f8:
sub a2, a2, a3 # original0x402485f8
pc402485fb:
s32i.n a3, a10, 0 # original0x402485fb
pc402485fd:
movltz a2, a11, a2 # original0x402485fd
pc40248600:
l32i.n a14, a1, 56 # original0x40248600
pc40248602:
s32i.n a2, a9, 0 # original0x40248602
pc40248604:
addi.n a4, a4, 1 # original0x40248604
pc40248606:
addi.n a5, a5, 2 # original0x40248606
pc40248608:
addi.n a10, a10, 4 # original0x40248608
pc4024860a:
addi.n a9, a9, 4 # original0x4024860a
pc4024860c:
addi.n a8, a8, 4 # original0x4024860c
pc4024860e:
addi.n a6, a6, 4 # original0x4024860e
pc40248610:
beq a14, a4, pc4024861c # original0x40248610
pc40248613:
l32i.n a14, a1, 36 # original0x40248613
pc40248615:
l32i.n a15, a14, 40 # original0x40248615
pc40248617:
j pc40248585 # original0x40248617
pc4024861a:
s32i.n a8, a1, 40 # original0x4024861a
pc4024861c:
call0 fixed_402428c4 # original0x4024861c
pc4024861f:
movi a14, 1 # original0x4024861f
pc40248622:
l32i a5, a1, 220 # original0x40248622
pc40248625:
s32i a2, a1, 0 # original0x40248625
pc40248628:
s32i a3, a1, 4 # original0x40248628
pc4024862b:
s32i a14, a1, 76 # original0x4024862b
pc4024862e:
bgei a5, 2, pc40248636 # original0x4024862e
pc40248631:
movi.n a7, 0 # original0x40248631
pc40248633:
s32i a7, a1, 76 # original0x40248633
pc40248636:
l32i.n a8, a1, 32 # original0x40248636
pc40248638:
l32i a14, a1, 224 # original0x40248638
pc4024863b:
movi.n a13, 0 # original0x4024863b
pc4024863d:
slli a14, a14, 3 # original0x4024863d
pc40248640:
slli a2, a8, 2 # original0x40248640
pc40248643:
addi a2, a2, -4 # original0x40248643
pc40248646:
s32i a14, a1, 68 # original0x40248646
pc40248649:
movi.n a4, 6 # original0x40248649
pc4024864b:
movi.n a14, 64 # original0x4024864b
pc4024864d:
mov.n a12, a13 # original0x4024864d
pc4024864f:
s32i.n a13, a1, 48 # original0x4024864f
pc40248651:
l32i a10, a1, 104 # original0x40248651
pc40248654:
l32i a13, a1, 100 # original0x40248654
pc40248657:
l32i a15, a1, 84 # original0x40248657
pc4024865a:
s32i.n a14, a1, 52 # original0x4024865a
pc4024865c:
s32i a2, a1, 80 # original0x4024865c
pc4024865f:
movi.n a11, 1 # original0x4024865f
pc40248661:
mov.n a14, a2 # original0x40248661
pc40248663:
s32i.n a4, a1, 28 # original0x40248663
pc40248665:
l32i.n a2, a1, 48 # original0x40248665
pc40248667:
l32i.n a3, a1, 52 # original0x40248667
pc40248669:
l32i.n a8, a1, 32 # original0x40248669
pc4024866b:
add.n a9, a2, a3 # original0x4024866b
pc4024866d:
l32i.n a2, a1, 56 # original0x4024866d
pc4024866f:
srai a9, a9, 1 # original0x4024866f
pc40248672:
movi.n a5, 0 # original0x40248672
pc40248674:
bge a8, a2, pc402486b7 # original0x40248674
pc40248677:
l32i a3, a1, 72 # original0x40248677
pc4024867a:
mov.n a8, a5 # original0x4024867a
pc4024867c:
add.n a2, a10, a3 # original0x4024867c
pc4024867e:
l32i.n a7, a1, 16 # original0x4024867e
pc40248680:
l32i.n a2, a2, 0 # original0x40248680
pc40248682:
add.n a6, a7, a3 # original0x40248682
pc40248684:
mull a2, a9, a2 # original0x40248684
pc40248687:
add.n a4, a13, a3 # original0x40248687
pc40248689:
l32i.n a6, a6, 0 # original0x40248689
pc4024868b:
srai a2, a2, 6 # original0x4024868b
pc4024868e:
l32i.n a4, a4, 0 # original0x4024868e
pc40248690:
add.n a2, a2, a6 # original0x40248690
pc40248692:
add.n a7, a15, a3 # original0x40248692
pc40248694:
bge a2, a4, pc40248699 # original0x40248694
pc40248697:
beqz.n a8, pc402486a8 # original0x40248697
pc40248699:
l32i.n a4, a7, 0 # original0x40248699
pc4024869b:
mov.n a8, a11 # original0x4024869b
pc4024869d:
bge a2, a4, pc402486a2 # original0x4024869d
pc402486a0:
mov.n a4, a2 # original0x402486a0
pc402486a2:
add.n a5, a5, a4 # original0x402486a2
pc402486a4:
j pc402486b1 # original0x402486a4
pc402486a8:
l32i.n a7, a1, 24 # original0x402486a8
pc402486aa:
mov.n a8, a12 # original0x402486aa
pc402486ac:
blt a2, a7, pc402486b1 # original0x402486ac
pc402486af:
add.n a5, a5, a7 # original0x402486af
pc402486b1:
addi a3, a3, -4 # original0x402486b1
pc402486b4:
bne a14, a3, pc4024867c # original0x402486b4
pc402486b7:
l32i.n a8, a1, 44 # original0x402486b7
pc402486b9:
bge a8, a5, pc402486c1 # original0x402486b9
pc402486bc:
s32i.n a9, a1, 52 # original0x402486bc
pc402486be:
j pc402486c3 # original0x402486be
pc402486c1:
s32i.n a9, a1, 48 # original0x402486c1
pc402486c3:
l32i.n a2, a1, 28 # original0x402486c3
pc402486c5:
addi.n a2, a2, -1 # original0x402486c5
pc402486c7:
s32i.n a2, a1, 28 # original0x402486c7
pc402486c9:
bnez a2, pc40248665 # original0x402486c9
pc402486cc:
l32i.n a8, a1, 32 # original0x402486cc
pc402486ce:
l32i.n a14, a1, 56 # original0x402486ce
pc402486d0:
l32i.n a13, a1, 48 # original0x402486d0
pc402486d2:
bge a8, a14, pc40248744 # original0x402486d2
pc402486d5:
l32i a7, a1, 72 # original0x402486d5
pc402486d8:
l32i.n a5, a1, 16 # original0x402486d8
pc402486da:
l32i a8, a1, 104 # original0x402486da
pc402486dd:
add.n a6, a5, a7 # original0x402486dd
pc402486df:
l32i a5, a1, 208 # original0x402486df
pc402486e2:
add.n a9, a8, a7 # original0x402486e2
pc402486e4:
add.n a8, a5, a7 # original0x402486e4
pc402486e6:
l32i.n a7, a1, 16 # original0x402486e6
pc402486e8:
l32i a5, a1, 80 # original0x402486e8
pc402486eb:
l32i a4, a1, 88 # original0x402486eb
pc402486ee:
add.n a3, a7, a5 # original0x402486ee
pc402486f0:
l32i.n a7, a1, 20 # original0x402486f0
pc402486f2:
mov.n a14, a2 # original0x402486f2
pc402486f4:
mov.n a10, a2 # original0x402486f4
pc402486f6:
movi.n a11, 1 # original0x402486f6
pc402486f8:
mov.n a12, a2 # original0x402486f8
pc402486fa:
l32i.n a2, a9, 0 # original0x402486fa
pc402486fc:
l32i.n a15, a6, 0 # original0x402486fc
pc402486fe:
mull a2, a13, a2 # original0x402486fe
pc40248701:
l32i.n a5, a7, 0 # original0x40248701
pc40248703:
srai a2, a2, 6 # original0x40248703
pc40248706:
add.n a2, a2, a15 # original0x40248706
pc40248708:
bge a2, a5, pc4024871a # original0x40248708
pc4024870b:
bbsi a10, 0, pc4024871a # original0x4024870b
pc4024870e:
l32i.n a5, a1, 24 # original0x4024870e
pc40248710:
blt a2, a5, pc40248720 # original0x40248710
pc40248713:
mov.n a2, a5 # original0x40248713
pc40248715:
mov.n a10, a12 # original0x40248715
pc40248717:
j pc40248724 # original0x40248717
pc4024871a:
mov.n a10, a11 # original0x4024871a
pc4024871c:
j pc40248724 # original0x4024871c
pc40248720:
mov.n a2, a12 # original0x40248720
pc40248722:
movi.n a10, 0 # original0x40248722
pc40248724:
l32i.n a15, a4, 0 # original0x40248724
pc40248726:
addi a6, a6, -4 # original0x40248726
pc40248729:
bge a2, a15, pc4024872e # original0x40248729
pc4024872c:
mov.n a15, a2 # original0x4024872c
pc4024872e:
s32i.n a15, a8, 0 # original0x4024872e
pc40248730:
add.n a14, a14, a15 # original0x40248730
pc40248732:
addi a9, a9, -4 # original0x40248732
pc40248735:
addi a7, a7, -4 # original0x40248735
pc40248738:
addi a4, a4, -4 # original0x40248738
pc4024873b:
addi a8, a8, -4 # original0x4024873b
pc4024873e:
bne a3, a6, pc402486fa # original0x4024873e
pc40248741:
j pc40248746 # original0x40248741
pc40248744:
mov.n a14, a2 # original0x40248744
pc40248746:
l32i.n a7, a1, 40 # original0x40248746
pc40248748:
l32i.n a8, a1, 60 # original0x40248748
pc4024874a:
blt a7, a8, pc40248796 # original0x4024874a
pc4024874d:
j pc4024876a # original0x4024874d
pc40248750:
l32i.n a5, a1, 20 # original0x40248750
pc40248752:
movi.n a2, 0 # original0x40248752
pc40248754:
addi a5, a5, -4 # original0x40248754
pc40248757:
l32i.n a7, a1, 40 # original0x40248757
pc40248759:
s32i.n a2, a14, 0 # original0x40248759
pc4024875b:
s32i.n a5, a1, 20 # original0x4024875b
pc4024875d:
addi.n a2, a12, -1 # original0x4024875d
pc4024875f:
addi a14, a14, -4 # original0x4024875f
pc40248762:
bge a7, a2, pc4024877c # original0x40248762
pc40248765:
mov.n a12, a2 # original0x40248765
pc40248767:
j pc402487ad # original0x40248767
pc4024876a:
l32i a8, a1, 92 # original0x4024876a
pc4024876d:
addi.n a8, a8, 2 # original0x4024876d
pc4024876f:
s32i.n a8, a1, 16 # original0x4024876f
pc40248771:
l32i.n a8, a1, 56 # original0x40248771
pc40248773:
s32i.n a8, a1, 60 # original0x40248773
pc40248775:
l32i a8, a1, 96 # original0x40248775
pc40248778:
j pc40248785 # original0x40248778
pc4024877c:
mov.n a14, a6 # original0x4024877c
pc4024877e:
s32i a13, a1, 96 # original0x4024877e
pc40248781:
s32i.n a12, a1, 60 # original0x40248781
pc40248783:
mov.n a8, a13 # original0x40248783
pc40248785:
l32i.n a5, a1, 44 # original0x40248785
pc40248787:
l32i a7, a1, 124 # original0x40248787
pc4024878a:
add.n a5, a5, a7 # original0x4024878a
pc4024878c:
s32i.n a5, a1, 44 # original0x4024878c
pc4024878e:
bnez a8, pc40248908 # original0x4024878e
pc40248791:
j pc40248965 # original0x40248791
pc40248796:
mov.n a12, a8 # original0x40248796
pc40248798:
l32i a7, a1, 208 # original0x40248798
pc4024879b:
l32i a8, a1, 72 # original0x4024879b
pc4024879e:
l32i.n a5, a1, 24 # original0x4024879e
pc402487a0:
add.n a13, a7, a8 # original0x402487a0
pc402487a2:
addi.n a5, a5, 8 # original0x402487a2
pc402487a4:
mov.n a6, a14 # original0x402487a4
pc402487a6:
mov.n a14, a13 # original0x402487a6
pc402487a8:
l32i a13, a1, 96 # original0x402487a8
pc402487ab:
s32i.n a5, a1, 28 # original0x402487ab
pc402487ad:
l32i.n a8, a1, 36 # original0x402487ad
pc402487af:
addi.n a5, a12, 1 # original0x402487af
pc402487b1:
l32i.n a7, a8, 24 # original0x402487b1
pc402487b3:
l32i a8, a1, 64 # original0x402487b3
pc402487b6:
slli a11, a5, 1 # original0x402487b6
pc402487b9:
add.n a3, a7, a11 # original0x402487b9
pc402487bb:
add.n a2, a7, a8 # original0x402487bb
pc402487bd:
l32i.n a8, a1, 44 # original0x402487bd
pc402487bf:
l16si a9, a2, 0 # original0x402487bf
pc402487c2:
l16si a4, a3, 0 # original0x402487c2
pc402487c5:
sub a15, a8, a6 # original0x402487c5
pc402487c8:
sub a3, a4, a9 # original0x402487c8
pc402487cb:
addi a8, a11, -2 # original0x402487cb
pc402487ce:
mov.n a2, a15 # original0x402487ce
pc402487d0:
s32i.n a8, a1, 16 # original0x402487d0
pc402487d2:
s32i a4, a1, 136 # original0x402487d2
pc402487d5:
s32i a5, a1, 140 # original0x402487d5
pc402487d8:
s32i a6, a1, 148 # original0x402487d8
pc402487db:
s32i a7, a1, 128 # original0x402487db
pc402487de:
s32i a9, a1, 132 # original0x402487de
pc402487e1:
s32i a11, a1, 144 # original0x402487e1
pc402487e4:
l32r a0, fixed_402101b8 # original0x402487e4
pc402487e7:
callx0 a0 # original0x402487e7
pc402487ea:
l32i.n a8, a1, 16 # original0x402487ea
pc402487ec:
l32i a7, a1, 128 # original0x402487ec
pc402487ef:
l32i a9, a1, 132 # original0x402487ef
pc402487f2:
add.n a7, a7, a8 # original0x402487f2
pc402487f4:
l32i a4, a1, 136 # original0x402487f4
pc402487f7:
l16si a7, a7, 0 # original0x402487f7
pc402487fa:
sub a3, a9, a4 # original0x402487fa
pc402487fd:
add.n a15, a15, a9 # original0x402487fd
pc402487ff:
mull a3, a3, a2 # original0x402487ff
pc40248802:
sub a4, a4, a7 # original0x40248802
pc40248805:
sub a15, a15, a7 # original0x40248805
pc40248808:
l32i.n a7, a1, 20 # original0x40248808
pc4024880a:
l32i.n a9, a14, 0 # original0x4024880a
pc4024880c:
mull a2, a2, a4 # original0x4024880c
pc4024880f:
add.n a15, a3, a15 # original0x4024880f
pc40248811:
movi.n a8, 0 # original0x40248811
pc40248813:
l32i.n a3, a7, 0 # original0x40248813
pc40248815:
l32i.n a7, a1, 28 # original0x40248815
pc40248817:
movltz a15, a8, a15 # original0x40248817
pc4024881a:
add.n a2, a2, a9 # original0x4024881a
pc4024881c:
add.n a15, a15, a2 # original0x4024881c
pc4024881e:
l32i a5, a1, 140 # original0x4024881e
pc40248821:
l32i a6, a1, 148 # original0x40248821
pc40248824:
l32i a11, a1, 144 # original0x40248824
pc40248827:
bge a3, a7, pc4024882c # original0x40248827
pc4024882a:
mov.n a3, a7 # original0x4024882a
pc4024882c:
bge a15, a3, pc40248832 # original0x4024882c
pc4024882f:
j pc402488cd # original0x4024882f
pc40248832:
l32i a8, a1, 232 # original0x40248832
pc40248835:
# decoder-unreachable/check: beqz a8, 402488a9 <clt_compute_allocation+1529>
pc40248838:
# decoder-unreachable/check: movi a3, 17
pc4024883a:
# decoder-unreachable/check: movi a2, 0
pc4024883c:
# decoder-unreachable/check: bge a3, a5, 4024884a <clt_compute_allocation+1434>
pc4024883f:
# decoder-unreachable/check: l32i a7, a1, 236
pc40248842:
# decoder-unreachable/check: movi a2, 7
pc40248844:
# decoder-unreachable/check: blt a12, a7, 4024884a <clt_compute_allocation+1434>
pc40248847:
# decoder-unreachable/check: movi a2, 9
pc4024884a:
# decoder-unreachable/check: l32i a8, a1, 32
pc4024884c:
# decoder-unreachable/check: addi a3, a8, 2
pc4024884f:
# decoder-unreachable/check: bge a3, a5, 4024886d <clt_compute_allocation+1469>
pc40248852:
# decoder-unreachable/check: mull a2, a4, a2
pc40248855:
# decoder-unreachable/check: l32i a7, a1, 224
pc40248858:
# decoder-unreachable/check: ssl a7
pc4024885b:
# decoder-unreachable/check: sll a2, a2
pc4024885e:
# decoder-unreachable/check: slli a2, a2, 3
pc40248861:
# decoder-unreachable/check: srai a2, a2, 4
pc40248864:
# decoder-unreachable/check: bge a2, a15, 40248894 <clt_compute_allocation+1508>
pc40248867:
# decoder-unreachable/check: l32i a8, a1, 240
pc4024886a:
# decoder-unreachable/check: blt a8, a12, 40248894 <clt_compute_allocation+1508>
pc4024886d:
# decoder-unreachable/check: movi a4, 1
pc40248870:
# decoder-unreachable/check: l32i a2, a1, 228
pc40248873:
# decoder-unreachable/check: or a3, a4, a4
pc40248876:
# decoder-unreachable/check: s32i a5, a1, 140
pc40248879:
# decoder-unreachable/check: or a14, a6, a6
pc4024887c:
# decoder-unreachable/check: mov a12, a11
pc4024887e:
# decoder-unreachable/check: s32i a13, a1, 96
pc40248881:
# decoder-unreachable/check: call0 402536a0 <ec_enc_bit_logp>
pc40248884:
# decoder-unreachable/check: l32i a7, a1, 96
pc40248887:
# decoder-unreachable/check: l32i a5, a1, 140
pc4024888a:
# decoder-unreachable/check: bnez a7, 40248911 <clt_compute_allocation+1633>
pc4024888d:
# decoder-unreachable/check: s32i a12, a1, 16
pc4024888f:
# decoder-unreachable/check: s32i a5, a1, 60
pc40248891:
# decoder-unreachable/check: j 40248965 <clt_compute_allocation+1717>
pc40248894:
# decoder-unreachable/check: l32i a2, a1, 228
pc40248897:
# decoder-unreachable/check: movi a4, 1
pc40248899:
# decoder-unreachable/check: movi a3, 0
pc4024889b:
# decoder-unreachable/check: s32i a6, a1, 148
pc4024889e:
# decoder-unreachable/check: call0 402536a0 <ec_enc_bit_logp>
pc402488a1:
# decoder-unreachable/check: l32i a6, a1, 148
pc402488a4:
# decoder-unreachable/check: j 402488c6 <clt_compute_allocation+1558>
pc402488a9:
l32i a2, a1, 228 # original0x402488a9
pc402488ac:
movi.n a3, 1 # original0x402488ac
pc402488ae:
s32i a5, a1, 140 # original0x402488ae
pc402488b1:
s32i a6, a1, 148 # original0x402488b1
pc402488b4:
s32i a11, a1, 144 # original0x402488b4
pc402488b7:
call0 fixed_40246a88 # original0x402488b7
pc402488ba:
l32i a5, a1, 140 # original0x402488ba
pc402488bd:
l32i a6, a1, 148 # original0x402488bd
pc402488c0:
l32i a11, a1, 144 # original0x402488c0
pc402488c3:
bnez a2, pc40248c5c # original0x402488c3
pc402488c6:
l32i.n a9, a14, 0 # original0x402488c6
pc402488c8:
addi.n a6, a6, 8 # original0x402488c8
pc402488ca:
addi a15, a15, -8 # original0x402488ca
pc402488cd:
sub a6, a6, a13 # original0x402488cd
pc402488d0:
sub a6, a6, a9 # original0x402488d0
pc402488d3:
beqz.n a13, pc402488e4 # original0x402488d3
pc402488d5:
l32i.n a8, a1, 32 # original0x402488d5
pc402488d7:
l32r a3, fixed_4021191c # original0x402488d7
pc402488da:
sub a2, a12, a8 # original0x402488da
pc402488dd:
add.n a2, a2, a3 # original0x402488dd
pc402488df:
l8ui a13, a2, 0 # original0x402488df
pc402488e2:
add.n a6, a6, a13 # original0x402488e2
pc402488e4:
l32i.n a5, a1, 24 # original0x402488e4
pc402488e6:
bge a15, a5, pc402488ec # original0x402488e6
pc402488e9:
j pc40248750 # original0x402488e9
pc402488ec:
l32i.n a7, a1, 20 # original0x402488ec
pc402488ee:
l32i.n a8, a1, 40 # original0x402488ee
pc402488f0:
addi a7, a7, -4 # original0x402488f0
pc402488f3:
s32i.n a5, a14, 0 # original0x402488f3
pc402488f5:
addi.n a2, a12, -1 # original0x402488f5
pc402488f7:
s32i.n a7, a1, 20 # original0x402488f7
pc402488f9:
add.n a6, a6, a5 # original0x402488f9
pc402488fb:
addi a14, a14, -4 # original0x402488fb
pc402488fe:
bge a8, a2, pc40248904 # original0x402488fe
pc40248901:
j pc40248765 # original0x40248901
pc40248904:
j pc4024877c # original0x40248904
pc40248908:
l32i a5, a1, 232 # original0x40248908
pc4024890b:
# decoder-unreachable/check: beqz a5, 40248947 <clt_compute_allocation+1687>
pc4024890d:
# decoder-unreachable/check: l32i a12, a1, 16
pc4024890f:
# decoder-unreachable/check: l32i a5, a1, 60
pc40248911:
# decoder-unreachable/check: l32i a7, a1, 192
pc40248914:
# decoder-unreachable/check: l32i a3, a7, 0
pc40248917:
# decoder-unreachable/check: bge a5, a3, 4024891d <clt_compute_allocation+1645>
pc4024891a:
# decoder-unreachable/check: or a3, a5, a5
pc4024891d:
# decoder-unreachable/check: l32i a8, a1, 32
pc40248920:
# decoder-unreachable/check: l32i a7, a1, 192
pc40248923:
# decoder-unreachable/check: sub a4, a5, a8
pc40248926:
# decoder-unreachable/check: l32i a2, a1, 228
pc40248929:
# decoder-unreachable/check: s32i a3, a7, 0
pc4024892c:
# decoder-unreachable/check: addi a4, a4, 1
pc4024892f:
# decoder-unreachable/check: sub a3, a3, a8
pc40248932:
# decoder-unreachable/check: s32i a5, a1, 140
pc40248935:
# decoder-unreachable/check: call0 40253774 <ec_enc_uint>
pc40248938:
# decoder-unreachable/check: l32i a8, a1, 192
pc4024893b:
# decoder-unreachable/check: l32i a5, a1, 140
pc4024893e:
# decoder-unreachable/check: s32i a12, a1, 16
pc40248940:
# decoder-unreachable/check: l32i a2, a8, 0
pc40248942:
# decoder-unreachable/check: s32i a5, a1, 60
pc40248944:
# decoder-unreachable/check: j 4024896c <clt_compute_allocation+1724>
pc40248947:
l32i a5, a1, 60 # original0x40248947
pc4024894a:
l32i a8, a1, 32 # original0x4024894a
pc4024894d:
l32i a2, a1, 228 # original0x4024894d
pc40248950:
sub a3, a5, a8 # original0x40248950
pc40248953:
addi a3, a3, 1 # original0x40248953
pc40248956:
call0 fixed_40246c20 # original0x40248956
pc40248959:
l32i.n a8, a1, 32 # original0x40248959
pc4024895b:
l32i a5, a1, 192 # original0x4024895b
pc4024895e:
add.n a2, a2, a8 # original0x4024895e
pc40248960:
s32i.n a2, a5, 0 # original0x40248960
pc40248962:
j pc4024896c # original0x40248962
pc40248965:
l32i a7, a1, 192 # original0x40248965
pc40248968:
movi.n a2, 0 # original0x40248968
pc4024896a:
s32i.n a2, a7, 0 # original0x4024896a
pc4024896c:
l32i.n a8, a1, 32 # original0x4024896c
pc4024896e:
blt a8, a2, pc4024897d # original0x4024896e
pc40248971:
l32i.n a5, a1, 44 # original0x40248971
pc40248973:
l32i a7, a1, 112 # original0x40248973
pc40248976:
add.n a5, a5, a7 # original0x40248976
pc40248978:
s32i.n a5, a1, 44 # original0x40248978
pc4024897a:
j pc402489ac # original0x4024897a
pc4024897d:
l32i a8, a1, 112 # original0x4024897d
pc40248980:
beqz.n a8, pc402489ac # original0x40248980
pc40248982:
l32i a5, a1, 232 # original0x40248982
pc40248985:
# decoder-unreachable/check: beqz a5, 40248999 <clt_compute_allocation+1769>
pc40248987:
# decoder-unreachable/check: l32i a7, a1, 196
pc4024898a:
# decoder-unreachable/check: l32i a2, a1, 228
pc4024898d:
# decoder-unreachable/check: l32i a3, a7, 0
pc4024898f:
# decoder-unreachable/check: movi a4, 1
pc40248991:
# decoder-unreachable/check: call0 402536a0 <ec_enc_bit_logp>
pc40248994:
# decoder-unreachable/check: j 402489b3 <clt_compute_allocation+1795>
pc40248999:
l32i a2, a1, 228 # original0x40248999
pc4024899c:
movi.n a3, 1 # original0x4024899c
pc4024899e:
call0 fixed_40246a88 # original0x4024899e
pc402489a1:
l32i a8, a1, 196 # original0x402489a1
pc402489a4:
s32i.n a2, a8, 0 # original0x402489a4
pc402489a6:
j pc402489b3 # original0x402489a6
pc402489ac:
l32i a5, a1, 196 # original0x402489ac
pc402489af:
movi.n a2, 0 # original0x402489af
pc402489b1:
s32i.n a2, a5, 0 # original0x402489b1
pc402489b3:
l32i.n a8, a1, 36 # original0x402489b3
pc402489b5:
l32i.n a7, a1, 16 # original0x402489b5
pc402489b7:
l32i.n a15, a8, 24 # original0x402489b7
pc402489b9:
l32i a8, a1, 64 # original0x402489b9
pc402489bc:
l32i.n a5, a1, 44 # original0x402489bc
pc402489be:
add.n a13, a15, a7 # original0x402489be
pc402489c0:
add.n a12, a15, a8 # original0x402489c0
pc402489c2:
sub a14, a5, a14 # original0x402489c2
pc402489c5:
l16si a5, a13, 0 # original0x402489c5
pc402489c8:
l16si a13, a12, 0 # original0x402489c8
pc402489cb:
mov.n a2, a14 # original0x402489cb
pc402489cd:
sub a3, a5, a13 # original0x402489cd
pc402489d0:
s32i a5, a1, 140 # original0x402489d0
pc402489d3:
l32r a0, fixed_402101b8 # original0x402489d3
pc402489d6:
callx0 a0 # original0x402489d6
pc402489d9:
l32i a5, a1, 140 # original0x402489d9
pc402489dc:
l32i.n a7, a1, 60 # original0x402489dc
pc402489de:
sub a5, a13, a5 # original0x402489de
pc402489e1:
mull a5, a5, a2 # original0x402489e1
pc402489e4:
add.n a5, a5, a14 # original0x402489e4
pc402489e6:
l32i.n a14, a1, 32 # original0x402489e6
pc402489e8:
blt a14, a7, pc402489ee # original0x402489e8
pc402489eb:
j pc40248c04 # original0x402489eb
pc402489ee:
l32i a8, a1, 80 # original0x402489ee
pc402489f1:
l32i a7, a1, 208 # original0x402489f1
pc402489f4:
addi.n a9, a8, 4 # original0x402489f4
pc402489f6:
l32i.n a8, a1, 60 # original0x402489f6
pc402489f8:
add.n a14, a7, a9 # original0x402489f8
pc402489fa:
slli a3, a8, 1 # original0x402489fa
pc402489fd:
mov.n a6, a12 # original0x402489fd
pc402489ff:
add.n a15, a15, a3 # original0x402489ff
pc40248a01:
mov.n a4, a12 # original0x40248a01
pc40248a03:
mov.n a7, a14 # original0x40248a03
pc40248a05:
call0 fixed_4024dcf0 # original0x40248a05
pc40248a08:
nop  # original0x40248a08
pc40248a0b:
l32i.n a8, a7, 0 # original0x40248a0b
pc40248a0d:
sub a3, a3, a10 # original0x40248a0d
pc40248a10:
mull a3, a3, a2 # original0x40248a10
pc40248a13:
addi.n a4, a4, 2 # original0x40248a13
pc40248a15:
add.n a3, a8, a3 # original0x40248a15
pc40248a17:
s32i.n a3, a7, 0 # original0x40248a17
pc40248a19:
addi.n a7, a7, 4 # original0x40248a19
pc40248a1b:
bne a4, a15, pc40248a05 # original0x40248a1b
pc40248a1e:
or a3, a14, a14 # original0x40248a1e
pc40248a21:
call0 fixed_4024ddb4 # original0x40248a21
pc40248a24:
nop  # original0x40248a24
pc40248a27:
addi.n a12, a12, 2 # original0x40248a27
pc40248a29:
sub a2, a2, a4 # original0x40248a29
pc40248a2c:
bge a5, a2, pc40248a31 # original0x40248a2c
pc40248a2f:
mov.n a2, a5 # original0x40248a2f
pc40248a31:
l32i.n a4, a3, 0 # original0x40248a31
pc40248a33:
sub a5, a5, a2 # original0x40248a33
pc40248a36:
add.n a2, a4, a2 # original0x40248a36
pc40248a38:
s32i.n a2, a3, 0 # original0x40248a38
pc40248a3a:
addi.n a3, a3, 4 # original0x40248a3a
pc40248a3c:
bne a12, a15, pc40248a21 # original0x40248a3c
pc40248a3f:
l32i a5, a1, 220 # original0x40248a3f
pc40248a42:
l32i a8, a1, 212 # original0x40248a42
pc40248a45:
addi a2, a5, -2 # original0x40248a45
pc40248a48:
movi.n a4, 0 # original0x40248a48
pc40248a4a:
movi.n a7, 1 # original0x40248a4a
pc40248a4c:
s32i.n a4, a1, 20 # original0x40248a4c
pc40248a4e:
add.n a15, a8, a9 # original0x40248a4e
pc40248a50:
moveqz a4, a7, a2 # original0x40248a50
pc40248a53:
l32i a5, a1, 216 # original0x40248a53
pc40248a56:
l32i a8, a1, 76 # original0x40248a56
pc40248a59:
mov.n a2, a4 # original0x40248a59
pc40248a5b:
add.n a7, a5, a9 # original0x40248a5b
pc40248a5d:
extui a2, a2, 0, 8 # original0x40248a5d
pc40248a60:
addi.n a8, a8, 3 # original0x40248a60
pc40248a62:
l32i.n a11, a1, 20 # original0x40248a62
pc40248a64:
l32i.n a4, a1, 32 # original0x40248a64
pc40248a66:
s32i.n a8, a1, 44 # original0x40248a66
pc40248a68:
s32i.n a2, a1, 32 # original0x40248a68
pc40248a6a:
mov.n a10, a7 # original0x40248a6a
pc40248a6c:
call0 fixed_4024dcb4 # original0x40248a6c
pc40248a6f:
nop  # original0x40248a6f
pc40248a72:
l32i a8, a1, 224 # original0x40248a72
pc40248a75:
sub a7, a7, a2 # original0x40248a75
pc40248a78:
l32i.n a5, a14, 0 # original0x40248a78
pc40248a7a:
ssl a8 # original0x40248a7a
pc40248a7d:
sll a7, a7 # original0x40248a7d
pc40248a80:
l32i.n a8, a1, 20 # original0x40248a80
pc40248a82:
slli a3, a4, 1 # original0x40248a82
pc40248a85:
add.n a2, a8, a5 # original0x40248a85
pc40248a87:
bgei a7, 2, pc40248a8d # original0x40248a87
pc40248a8a:
j pc40248b99 # original0x40248a8a
pc40248a8d:
l32i a8, a1, 84 # original0x40248a8d
pc40248a90:
slli a5, a4, 2 # original0x40248a90
pc40248a93:
add.n a5, a8, a5 # original0x40248a93
pc40248a95:
l32i.n a8, a1, 36 # original0x40248a95
pc40248a97:
l32i.n a12, a5, 0 # original0x40248a97
pc40248a99:
l32i.n a5, a8, 48 # original0x40248a99
pc40248a9b:
l32i a8, a1, 220 # original0x40248a9b
pc40248a9e:
add.n a3, a5, a3 # original0x40248a9e
pc40248aa0:
l16si a5, a3, 0 # original0x40248aa0
pc40248aa3:
sub a12, a2, a12 # original0x40248aa3
pc40248aa6:
mull a3, a8, a7 # original0x40248aa6
pc40248aa9:
l32i a8, a1, 68 # original0x40248aa9
pc40248aac:
movltz a12, a11, a12 # original0x40248aac
pc40248aaf:
sub a2, a2, a12 # original0x40248aaf
pc40248ab2:
add.n a5, a5, a8 # original0x40248ab2
pc40248ab4:
l32i.n a8, a1, 32 # original0x40248ab4
pc40248ab6:
s32i.n a2, a14, 0 # original0x40248ab6
pc40248ab8:
beqz.n a8, pc40248ad9 # original0x40248ab8
pc40248aba:
blti a7, 3, pc40248ad9 # original0x40248aba
pc40248abd:
l32i a8, a1, 196 # original0x40248abd
pc40248ac0:
l32i.n a7, a8, 0 # original0x40248ac0
pc40248ac2:
bnez a7, pc40248c6b # original0x40248ac2
pc40248ac5:
l32i a7, a1, 192 # original0x40248ac5
pc40248ac8:
l32i.n a8, a7, 0 # original0x40248ac8
pc40248aca:
movi.n a7, 1 # original0x40248aca
pc40248acc:
blt a4, a8, pc40248ad1 # original0x40248acc
pc40248acf:
mov.n a7, a11 # original0x40248acf
pc40248ad1:
add.n a3, a3, a7 # original0x40248ad1
pc40248ad3:
j pc40248c6b # original0x40248ad3
pc40248ad9:
slli a8, a3, 28 # original0x40248ad9
pc40248adc:
sub a8, a8, a3 # original0x40248adc
pc40248adf:
slli a8, a8, 2 # original0x40248adf
pc40248ae2:
sub a8, a8, a3 # original0x40248ae2
pc40248ae5:
mull a5, a3, a5 # original0x40248ae5
pc40248ae8:
slli a13, a8, 2 # original0x40248ae8
pc40248aeb:
sub a8, a13, a3 # original0x40248aeb
pc40248aee:
srai a9, a5, 1 # original0x40248aee
pc40248af1:
add.n a13, a9, a8 # original0x40248af1
pc40248af3:
slli a8, a3, 3 # original0x40248af3
pc40248af6:
s32i.n a8, a1, 16 # original0x40248af6
pc40248af8:
bnei a7, 2, pc40248b00 # original0x40248af8
pc40248afb:
srai a7, a8, 2 # original0x40248afb
pc40248afe:
add.n a13, a13, a7 # original0x40248afe
pc40248b00:
add.n a8, a2, a13 # original0x40248b00
pc40248b02:
slli a7, a3, 4 # original0x40248b02
pc40248b05:
slli a9, a3, 1 # original0x40248b05
pc40248b08:
bge a8, a7, pc40248b14 # original0x40248b08
pc40248b0b:
srai a5, a5, 2 # original0x40248b0b
pc40248b0e:
add.n a13, a13, a5 # original0x40248b0e
pc40248b10:
j pc40248b21 # original0x40248b10
pc40248b14:
add.n a9, a9, a3 # original0x40248b14
pc40248b16:
slli a9, a9, 3 # original0x40248b16
pc40248b19:
bge a8, a9, pc40248b21 # original0x40248b19
pc40248b1c:
srai a5, a5, 3 # original0x40248b1c
pc40248b1f:
add.n a13, a13, a5 # original0x40248b1f
pc40248b21:
slli a5, a3, 2 # original0x40248b21
pc40248b24:
add.n a2, a5, a2 # original0x40248b24
pc40248b26:
add.n a2, a2, a13 # original0x40248b26
pc40248b28:
movltz a2, a11, a2 # original0x40248b28
pc40248b2b:
s32i a4, a1, 136 # original0x40248b2b
pc40248b2e:
s32i a6, a1, 148 # original0x40248b2e
pc40248b31:
s32i a10, a1, 128 # original0x40248b31
pc40248b34:
s32i a11, a1, 144 # original0x40248b34
pc40248b37:
l32r a0, fixed_402101b8 # original0x40248b37
pc40248b3a:
callx0 a0 # original0x40248b3a
pc40248b3d:
srli a2, a2, 3 # original0x40248b3d
pc40248b40:
l32i a7, a1, 220 # original0x40248b40
pc40248b43:
s32i.n a2, a15, 0 # original0x40248b43
pc40248b45:
l32i a3, a14, 0 # original0x40248b45
pc40248b48:
mull a5, a7, a2 # original0x40248b48
pc40248b4b:
srai a7, a3, 3 # original0x40248b4b
pc40248b4e:
l32i a4, a1, 136 # original0x40248b4e
pc40248b51:
l32i a6, a1, 148 # original0x40248b51
pc40248b54:
l32i a10, a1, 128 # original0x40248b54
pc40248b57:
l32i a11, a1, 144 # original0x40248b57
pc40248b5a:
bge a7, a5, pc40248b69 # original0x40248b5a
pc40248b5d:
l32i a8, a1, 76 # original0x40248b5d
pc40248b60:
ssr a8 # original0x40248b60
pc40248b63:
sra a2, a3 # original0x40248b63
pc40248b66:
srai a2, a2, 3 # original0x40248b66
pc40248b69:
movi.n a3, 8 # original0x40248b69
pc40248b6b:
bge a3, a2, pc40248b70 # original0x40248b6b
pc40248b6e:
mov.n a2, a3 # original0x40248b6e
pc40248b70:
s32i.n a2, a15, 0 # original0x40248b70
pc40248b72:
l32i.n a5, a1, 16 # original0x40248b72
pc40248b74:
l32i.n a3, a14, 0 # original0x40248b74
pc40248b76:
mull a8, a2, a5 # original0x40248b76
pc40248b79:
add.n a13, a13, a3 # original0x40248b79
pc40248b7b:
movi.n a2, 1 # original0x40248b7b
pc40248b7d:
bge a8, a13, pc40248b82 # original0x40248b7d
pc40248b80:
mov.n a2, a11 # original0x40248b80
pc40248b82:
s32i.n a2, a10, 0 # original0x40248b82
pc40248b84:
l32i.n a2, a15, 0 # original0x40248b84
pc40248b86:
l32i a7, a1, 220 # original0x40248b86
pc40248b89:
l32i.n a3, a14, 0 # original0x40248b89
pc40248b8b:
mull a2, a7, a2 # original0x40248b8b
pc40248b8e:
slli a2, a2, 3 # original0x40248b8e
pc40248b91:
sub a2, a3, a2 # original0x40248b91
pc40248b94:
s32i.n a2, a14, 0 # original0x40248b94
pc40248b96:
j pc40248bac # original0x40248b96
pc40248b99:
l32i.n a8, a1, 24 # original0x40248b99
pc40248b9b:
sub a12, a2, a8 # original0x40248b9b
pc40248b9e:
movltz a12, a11, a12 # original0x40248b9e
pc40248ba1:
sub a2, a2, a12 # original0x40248ba1
pc40248ba4:
s32i.n a2, a14, 0 # original0x40248ba4
pc40248ba6:
s32i.n a11, a15, 0 # original0x40248ba6
pc40248ba8:
movi.n a2, 1 # original0x40248ba8
pc40248baa:
s32i.n a2, a10, 0 # original0x40248baa
pc40248bac:
beqz.n a12, pc40248be8 # original0x40248bac
pc40248bae:
l32i.n a3, a15, 0 # original0x40248bae
pc40248bb0:
l32i a7, a1, 44 # original0x40248bb0
pc40248bb3:
movi.n a8, 8 # original0x40248bb3
pc40248bb5:
ssr a7 # original0x40248bb5
pc40248bb8:
sra a5, a12 # original0x40248bb8
pc40248bbb:
sub a2, a8, a3 # original0x40248bbb
pc40248bbe:
bge a2, a5, pc40248bc4 # original0x40248bbe
pc40248bc1:
or a5, a2, a2 # original0x40248bc1
pc40248bc4:
l32i a7, a1, 220 # original0x40248bc4
pc40248bc7:
l32i.n a8, a1, 20 # original0x40248bc7
pc40248bc9:
mull a2, a7, a5 # original0x40248bc9
pc40248bcc:
add.n a3, a3, a5 # original0x40248bcc
pc40248bce:
s32i.n a3, a15, 0 # original0x40248bce
pc40248bd0:
slli a2, a2, 3 # original0x40248bd0
pc40248bd3:
sub a5, a12, a8 # original0x40248bd3
pc40248bd6:
movi.n a3, 1 # original0x40248bd6
pc40248bd8:
bge a2, a5, pc40248bdd # original0x40248bd8
pc40248bdb:
mov.n a3, a11 # original0x40248bdb
pc40248bdd:
sub a2, a12, a2 # original0x40248bdd
pc40248be0:
s32i.n a3, a10, 0 # original0x40248be0
pc40248be2:
s32i.n a2, a1, 20 # original0x40248be2
pc40248be4:
j pc40248bea # original0x40248be4
pc40248be8:
s32i.n a11, a1, 20 # original0x40248be8
pc40248bea:
l32i.n a5, a1, 60 # original0x40248bea
pc40248bec:
addi.n a4, a4, 1 # original0x40248bec
pc40248bee:
addi.n a6, a6, 2 # original0x40248bee
pc40248bf0:
addi.n a14, a14, 4 # original0x40248bf0
pc40248bf2:
addi.n a15, a15, 4 # original0x40248bf2
pc40248bf4:
addi.n a10, a10, 4 # original0x40248bf4
pc40248bf6:
beq a4, a5, pc40248bfc # original0x40248bf6
pc40248bf9:
j pc40248a6c # original0x40248bf9
pc40248bfc:
s32i.n a5, a1, 32 # original0x40248bfc
pc40248bfe:
mov.n a14, a5 # original0x40248bfe
pc40248c00:
j pc40248c08 # original0x40248c00
pc40248c04:
movi.n a7, 0 # original0x40248c04
pc40248c06:
s32i.n a7, a1, 20 # original0x40248c06
pc40248c08:
l32i.n a8, a1, 20 # original0x40248c08
pc40248c0a:
l32i a2, a1, 204 # original0x40248c0a
pc40248c0d:
s32i.n a8, a2, 0 # original0x40248c0d
pc40248c0f:
l32i.n a8, a1, 56 # original0x40248c0f
pc40248c11:
bge a14, a8, pc40248c8e # original0x40248c11
pc40248c14:
l32i a8, a1, 72 # original0x40248c14
pc40248c17:
slli a5, a14, 2 # original0x40248c17
pc40248c1a:
addi.n a7, a8, 4 # original0x40248c1a
pc40248c1c:
l32i a14, a1, 208 # original0x40248c1c
pc40248c1f:
l32i a8, a1, 212 # original0x40248c1f
pc40248c22:
add.n a3, a14, a5 # original0x40248c22
pc40248c24:
add.n a4, a8, a5 # original0x40248c24
pc40248c26:
l32i a14, a1, 216 # original0x40248c26
pc40248c29:
l32i a8, a1, 208 # original0x40248c29
pc40248c2c:
l32i a9, a1, 76 # original0x40248c2c
pc40248c2f:
add.n a7, a8, a7 # original0x40248c2f
pc40248c31:
add.n a5, a14, a5 # original0x40248c31
pc40248c33:
movi.n a8, 0 # original0x40248c33
pc40248c35:
l32i.n a2, a3, 0 # original0x40248c35
pc40248c37:
ssr a9 # original0x40248c37
pc40248c3a:
sra a2, a2 # original0x40248c3a
pc40248c3d:
srai a2, a2, 3 # original0x40248c3d
pc40248c40:
s32i.n a2, a4, 0 # original0x40248c40
pc40248c42:
s32i.n a8, a3, 0 # original0x40248c42
pc40248c44:
l32i.n a6, a4, 0 # original0x40248c44
pc40248c46:
addi.n a3, a3, 4 # original0x40248c46
pc40248c48:
addi.n a2, a6, -1 # original0x40248c48
pc40248c4a:
or a2, a2, a6 # original0x40248c4a
pc40248c4d:
extui a2, a2, 31, 1 # original0x40248c4d
pc40248c50:
s32i.n a2, a5, 0 # original0x40248c50
pc40248c52:
addi.n a4, a4, 4 # original0x40248c52
pc40248c54:
addi.n a5, a5, 4 # original0x40248c54
pc40248c56:
bne a3, a7, pc40248c35 # original0x40248c56
pc40248c59:
j pc40248c8e # original0x40248c59
pc40248c5c:
s32i a13, a1, 96 # original0x40248c5c
pc40248c5f:
s32i.n a11, a1, 16 # original0x40248c5f
pc40248c61:
s32i.n a5, a1, 60 # original0x40248c61
pc40248c63:
mov.n a14, a6 # original0x40248c63
pc40248c65:
bnez a13, pc40248947 # original0x40248c65
pc40248c68:
j pc40248965 # original0x40248c68
pc40248c6b:
slli a7, a3, 28 # original0x40248c6b
pc40248c6e:
sub a7, a7, a3 # original0x40248c6e
pc40248c71:
slli a7, a7, 2 # original0x40248c71
pc40248c74:
sub a13, a7, a3 # original0x40248c74
pc40248c77:
mull a5, a5, a3 # original0x40248c77
pc40248c7a:
slli a13, a13, 2 # original0x40248c7a
pc40248c7d:
srai a7, a5, 1 # original0x40248c7d
pc40248c80:
sub a13, a13, a3 # original0x40248c80
pc40248c83:
add.n a13, a13, a7 # original0x40248c83
pc40248c85:
slli a7, a3, 3 # original0x40248c85
pc40248c88:
s32i.n a7, a1, 16 # original0x40248c88
pc40248c8a:
j pc40248b00 # original0x40248c8a
pc40248c8e:
l32i.n a2, a1, 0 # original0x40248c8e
pc40248c90:
l32i.n a3, a1, 4 # original0x40248c90
pc40248c92:
call0 fixed_402428d8 # original0x40248c92
pc40248c95:
l32i.n a2, a1, 8 # original0x40248c95
pc40248c97:
l32i.n a3, a1, 12 # original0x40248c97
pc40248c99:
call0 fixed_402428d8 # original0x40248c99
pc40248c9c:
l32i a0, a1, 188 # original0x40248c9c
pc40248c9f:
movi a9, 192 # original0x40248c9f
pc40248ca2:
l32i.n a2, a1, 60 # original0x40248ca2
pc40248ca4:
l32i a12, a1, 184 # original0x40248ca4
pc40248ca7:
l32i a13, a1, 180 # original0x40248ca7
pc40248caa:
l32i a14, a1, 176 # original0x40248caa
pc40248cad:
l32i a15, a1, 172 # original0x40248cad
pc40248cb0:
add.n a1, a1, a9 # original0x40248cb0
pc40248cb2:
ret.n  # original0x40248cb2
allocation_live_end:
.space 2564 - (. - pc402482b0), 0
.end no-transform
