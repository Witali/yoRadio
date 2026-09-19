# Generated from accepted linked ASM. Original Opus licensing applies.
# call0 ABI; original 112/48-byte frames, same callees and inline rotation.
# B=1 and 0<K<=32767: |pulse|<=K fits int16. X is halfword-writable DRAM.
# No arena mark/alloc/restore: all remaining callees have no scratch lifetime.
# Fallback leaves the accepted decoder body intact after displaced prologue.
.begin no-transform
.section .text.patch0,"ax",@progbits
 j ip_guard
.section .text.patch1,"ax",@progbits
ip_pool_start:
ip_literal_40211920:
 .word 0x402d5e20
ip_literal_402106c8:
 .word 0x7fff
ip_literal_40211924:
 .word 0x4000e21c
ip_literal_4024f0c8:
 .word 0x402d7594
.align 4
.global inplace_unquant
.type inplace_unquant,@function
inplace_unquant:
.global ip_402493b0
ip_402493b0:
 addi a1, a1, -112
.global ip_402493b3
ip_402493b3:
 or a9, a6, a6
.global ip_402493b6
ip_402493b6:
 l16si a6, a1, 112
.global ip_402493b9
ip_402493b9:
 s32i a9, a1, 68
.global ip_402493bc
ip_402493bc:
 s32i.n a6, a1, 20
.global ip_402493be
ip_402493be:
 s32i a0, a1, 108
.global ip_402493c1
ip_402493c1:
 s32i.n a5, a1, 24
.global ip_402493c3
ip_402493c3:
 s32i a12, a1, 104
.global ip_402493c6
ip_402493c6:
 s32i a13, a1, 100
.global ip_402493c9
ip_402493c9:
 s32i a14, a1, 96
.global ip_402493cc
ip_402493cc:
 s32i a15, a1, 92
.global ip_402493cf
ip_402493cf:
 mov.n a14, a4
.global ip_402493d1
ip_402493d1:
 mov.n a15, a7
.global ip_402493d3
ip_402493d3:
 s32i a3, a1, 16
.global ip_402493d6
ip_402493d6:
 or a12, a2, a2
.global ip_402493d9
ip_402493d9:
.global ip_402493dc
ip_402493dc:
.global ip_402493de
ip_402493de:
.global ip_402493e0
ip_402493e0:
.global ip_402493e2
ip_402493e2:
.global ip_402493e4
ip_402493e4:
.global ip_402493e6
ip_402493e6:
.global ip_402493e9
ip_402493e9:
 l32i.n a3, a1, 16
.global ip_402493eb
ip_402493eb:
 mov.n a5, a15
.global ip_402493ed
ip_402493ed:
 mov.n a4, a14
.global ip_402493ef
ip_402493ef:
 mov.n a13, a12
 mov.n a2, a12
.global ip_402493f1
ip_402493f1:
 call0 inplace_decode16
.global ip_402493f4
ip_402493f4:
 nsau a3, a2
.global ip_402493f7
ip_402493f7:
 movi.n a6, 31
.global ip_402493f9
ip_402493f9:
 sub a6, a6, a3
.global ip_402493fc
ip_402493fc:
 slli a6, a6, 16
.global ip_402493ff
ip_402493ff:
 srai a15, a6, 17
.global ip_40249402
ip_40249402:
 addi a3, a15, -7
.global ip_40249405
ip_40249405:
 slli a3, a3, 1
.global ip_40249408
ip_40249408:
 l32i a9, a1, 68
.global ip_4024940b
ip_4024940b:
 blti a3, 1, ip_4024941a
.global ip_4024940e
ip_4024940e:
 ssr a3
.global ip_40249411
ip_40249411:
 sra a2, a2
.global ip_40249414
ip_40249414:
 j ip_40249429
.global ip_4024941a
ip_4024941a:
 movi a3, 7
.global ip_4024941d
ip_4024941d:
 sub a3, a3, a15
.global ip_40249420
ip_40249420:
 slli a3, a3, 1
.global ip_40249423
ip_40249423:
 ssl a3
.global ip_40249426
ip_40249426:
 sll a2, a2
.global ip_40249429
ip_40249429:
 s32i a9, a1, 68
.global ip_4024942c
ip_4024942c:
 call0 ip_call_40246e54
.global ip_4024942f
ip_4024942f:
 l32i a6, a1, 20
.global ip_40249432
ip_40249432:
 movi a11, 1
.global ip_40249435
ip_40249435:
 mull a10, a6, a2
.global ip_40249438
ip_40249438:
 addi.n a6, a15, 1
.global ip_4024943a
ip_4024943a:
 addmi a10, a10, 0x4000
.global ip_4024943d
ip_4024943d:
 slli a10, a10, 1
.global ip_40249440
ip_40249440:
 ssl a6
.global ip_40249443
ip_40249443:
 sll a11, a11
.global ip_40249446
ip_40249446:
 l32i.n a8, a1, 16
.global ip_40249448
ip_40249448:
 l32i a9, a1, 68
.global ip_4024944b
ip_4024944b:
 srai a10, a10, 16
.global ip_4024944e
ip_4024944e:
 srai a11, a11, 1
.global ip_40249451
ip_40249451:
 mov.n a7, a12
.global ip_40249453
ip_40249453:
 mov.n a5, a12
.global ip_40249455
ip_40249455:
 mov.n a4, a13
.global ip_40249457
ip_40249457:
 movi.n a3, 0
.global ip_40249459
ip_40249459:
 l16si a2, a4, 0
.global ip_4024945b
ip_4024945b:
 addi.n a3, a3, 1
.global ip_4024945d
ip_4024945d:
 mul16s a2, a2, a10
.global ip_40249460
ip_40249460:
 addi.n a4, a4, 2
.global ip_40249462
ip_40249462:
 add.n a2, a2, a11
.global ip_40249464
ip_40249464:
 ssr a6
.global ip_40249467
ip_40249467:
 sra a2, a2
.global ip_4024946a
ip_4024946a:
 s16i a2, a5, 0
.global ip_4024946d
ip_4024946d:
 addi.n a5, a5, 2
.global ip_4024946f
ip_4024946f:
 blt a3, a8, ip_40249459
.global ip_40249472
ip_40249472:
 l32i.n a3, a1, 16
.global ip_40249474
ip_40249474:
 slli a2, a14, 1
.global ip_40249477
ip_40249477:
 bge a2, a3, ip_40249488
.global ip_4024947a
ip_4024947a:
 l32i.n a6, a1, 24
.global ip_4024947c
ip_4024947c:
 movi.n a3, 1
.global ip_4024947e
ip_4024947e:
 movi.n a4, 0
.global ip_40249480
ip_40249480:
 moveqz a4, a3, a6
.global ip_40249483
ip_40249483:
 extui a4, a4, 0, 8
.global ip_40249486
ip_40249486:
 beqz.n a4, ip_40249495
.global ip_40249488
ip_40249488:
 movi.n a12, 1
.global ip_4024948a
ip_4024948a:
.global ip_4024948d
ip_4024948d:
.global ip_40249490
ip_40249490:
 j ip_4024969c
.global ip_40249495
ip_40249495:
 l32r a5, ip_literal_40211920
.global ip_40249498
ip_40249498:
 addi.n a2, a6, -1
.global ip_4024949a
ip_4024949a:
 slli a2, a2, 2
.global ip_4024949d
ip_4024949d:
 add.n a2, a5, a2
.global ip_4024949f
ip_4024949f:
 l32i.n a6, a1, 16
.global ip_402494a1
ip_402494a1:
 l32i.n a2, a2, 0
.global ip_402494a3
ip_402494a3:
 slli a5, a6, 16
.global ip_402494a6
ip_402494a6:
 mull a14, a14, a2
.global ip_402494a9
ip_402494a9:
 srai a5, a5, 16
.global ip_402494ac
ip_402494ac:
 add.n a14, a14, a6
.global ip_402494ae
ip_402494ae:
 slli a11, a5, 15
.global ip_402494b1
ip_402494b1:
 sub a11, a11, a5
.global ip_402494b4
ip_402494b4:
 mov.n a2, a14
.global ip_402494b6
ip_402494b6:
 s32i.n a3, a1, 60
.global ip_402494b8
ip_402494b8:
 s32i a7, a1, 64
.global ip_402494bb
ip_402494bb:
 s32i a9, a1, 68
.global ip_402494be
ip_402494be:
 s32i.n a4, a1, 52
.global ip_402494c0
ip_402494c0:
 s32i.n a11, a1, 56
.global ip_402494c2
ip_402494c2:
 call0 ip_call_40247054
.global ip_402494c5
ip_402494c5:
 mov.n a5, a2
.global ip_402494c7
ip_402494c7:
 mov.n a2, a14
.global ip_402494c9
ip_402494c9:
 s32i.n a5, a1, 48
.global ip_402494cb
ip_402494cb:
 call0 ip_call_40247054
.global ip_402494ce
ip_402494ce:
 mov.n a6, a2
.global ip_402494d0
ip_402494d0:
 mov.n a2, a14
.global ip_402494d2
ip_402494d2:
 s32i.n a6, a1, 44
.global ip_402494d4
ip_402494d4:
 call0 ip_call_40247054
.global ip_402494d7
ip_402494d7:
 l32i.n a11, a1, 56
.global ip_402494d9
ip_402494d9:
 l32i.n a6, a1, 44
.global ip_402494db
ip_402494db:
 l32i.n a5, a1, 48
.global ip_402494dd
ip_402494dd:
 srai a10, a11, 16
.global ip_402494e0
ip_402494e0:
 srai a15, a2, 16
.global ip_402494e3
ip_402494e3:
 extui a11, a11, 0, 16
.global ip_402494e6
ip_402494e6:
 extui a6, a6, 0, 16
.global ip_402494e9
ip_402494e9:
 mull a15, a15, a11
.global ip_402494ec
ip_402494ec:
 mull a6, a6, a10
.global ip_402494ef
ip_402494ef:
 srai a2, a5, 16
.global ip_402494f2
ip_402494f2:
 mull a2, a2, a10
.global ip_402494f5
ip_402494f5:
 srai a5, a6, 15
.global ip_402494f8
ip_402494f8:
 srai a15, a15, 15
.global ip_402494fb
ip_402494fb:
 add.n a15, a15, a5
.global ip_402494fd
ip_402494fd:
 slli a2, a2, 1
.global ip_40249500
ip_40249500:
 add.n a15, a15, a2
.global ip_40249502
ip_40249502:
 mul16s a15, a15, a15
.global ip_40249505
ip_40249505:
 l32i.n a4, a1, 52
.global ip_40249507
ip_40249507:
 srai a15, a15, 16
.global ip_4024950a
ip_4024950a:
 mov.n a2, a15
.global ip_4024950c
ip_4024950c:
 s32i.n a4, a1, 20
.global ip_4024950e
ip_4024950e:
 call0 ip_call_40246f64
.global ip_40249511
ip_40249511:
 mov.n a14, a2
.global ip_40249513
ip_40249513:
 l32r a2, ip_literal_402106c8
.global ip_40249516
ip_40249516:
 sub a2, a2, a15
.global ip_40249519
ip_40249519:
 call0 ip_call_40246f64
.global ip_4024951c
ip_4024951c:
 l32i a9, a1, 68
.global ip_4024951f
ip_4024951f:
 l32i.n a4, a1, 16
.global ip_40249521
ip_40249521:
 mov.n a15, a2
.global ip_40249523
ip_40249523:
 slli a2, a9, 3
.global ip_40249526
ip_40249526:
 l32i.n a3, a1, 60
.global ip_40249528
ip_40249528:
 l32i a7, a1, 64
.global ip_4024952b
ip_4024952b:
 blt a4, a2, ip_4024954d
.global ip_4024952e
ip_4024952e:
 mov.n a8, a4
.global ip_40249530
ip_40249530:
 srai a5, a9, 2
.global ip_40249533
ip_40249533:
 mov.n a4, a9
.global ip_40249535
ip_40249535:
 s32i.n a3, a1, 20
.global ip_40249537
ip_40249537:
 mov.n a6, a3
.global ip_40249539
ip_40249539:
 j ip_4024953f
.global ip_4024953d
ip_4024953d:
 mov.n a6, a3
.global ip_4024953f
ip_4024953f:
 addi.n a3, a6, 1
.global ip_40249541
ip_40249541:
 mull a2, a4, a3
.global ip_40249544
ip_40249544:
 add.n a4, a4, a9
.global ip_40249546
ip_40249546:
 add.n a2, a2, a5
.global ip_40249548
ip_40249548:
 blt a2, a8, ip_4024953d
.global ip_4024954b
ip_4024954b:
 s32i.n a6, a1, 20
.global ip_4024954d
ip_4024954d:
 l32i.n a2, a1, 16
.global ip_4024954f
ip_4024954f:
 mov.n a3, a9
.global ip_40249551
ip_40249551:
 s32i a7, a1, 64
.global ip_40249554
ip_40249554:
 s32i a9, a1, 68
.global ip_40249557
ip_40249557:
 l32r a0, ip_literal_40211924
.global ip_4024955a
ip_4024955a:
 callx0 a0
.global ip_4024955d
ip_4024955d:
 l32i a9, a1, 68
.global ip_40249560
ip_40249560:
 s32i.n a2, a1, 36
.global ip_40249562
ip_40249562:
 l32i a7, a1, 64
.global ip_40249565
ip_40249565:
 bgei a9, 1, ip_4024956b
.global ip_40249568
ip_40249568:
 j ip_4024969a
.global ip_4024956b
ip_4024956b:
 mov.n a6, a2
.global ip_4024956d
ip_4024956d:
 mov.n a3, a2
.global ip_4024956f
ip_4024956f:
 slli a2, a2, 1
.global ip_40249572
ip_40249572:
 addi a2, a2, -6
.global ip_40249575
ip_40249575:
 s32i.n a2, a1, 24
.global ip_40249577
ip_40249577:
 l32i.n a5, a1, 24
.global ip_40249579
ip_40249579:
 addi a10, a12, -2
.global ip_4024957c
ip_4024957c:
 addi.n a11, a5, 6
.global ip_4024957e
ip_4024957e:
 neg a2, a15
.global ip_40249581
ip_40249581:
 add.n a10, a10, a11
.global ip_40249583
ip_40249583:
 slli a2, a2, 16
.global ip_40249586
ip_40249586:
 addi.n a6, a6, -1
.global ip_40249588
ip_40249588:
 addi a3, a3, -3
.global ip_4024958b
ip_4024958b:
 s32i.n a13, a1, 40
.global ip_4024958d
ip_4024958d:
 s32i.n a9, a1, 28
.global ip_4024958f
ip_4024958f:
 mov.n a13, a10
.global ip_40249591
ip_40249591:
 s32i.n a6, a1, 32
.global ip_40249593
ip_40249593:
 srai a12, a2, 16
.global ip_40249596
ip_40249596:
 movi.n a8, 0
.global ip_40249598
ip_40249598:
 mov.n a10, a3
.global ip_4024959a
ip_4024959a:
 mov.n a9, a11
.global ip_4024959c
ip_4024959c:
 l32i a4, a1, 20
.global ip_4024959f
ip_4024959f:
 beqz a4, ip_402495c2
.global ip_402495a2
ip_402495a2:
 l32i a3, a1, 36
.global ip_402495a5
ip_402495a5:
 mov.n a2, a7
.global ip_402495a7
ip_402495a7:
 mov.n a6, a14
.global ip_402495a9
ip_402495a9:
 mov.n a5, a15
.global ip_402495ab
ip_402495ab:
 s32i a7, a1, 64
.global ip_402495ae
ip_402495ae:
 s32i.n a8, a1, 44
.global ip_402495b0
ip_402495b0:
 s32i a9, a1, 68
.global ip_402495b3
ip_402495b3:
 s32i.n a10, a1, 48
.global ip_402495b5
ip_402495b5:
 call0 ip_call_40298b88
.global ip_402495b8
ip_402495b8:
 l32i.n a10, a1, 48
.global ip_402495ba
ip_402495ba:
 l32i a9, a1, 68
.global ip_402495bd
ip_402495bd:
 l32i.n a8, a1, 44
.global ip_402495bf
ip_402495bf:
 l32i a7, a1, 64
.global ip_402495c2
ip_402495c2:
 l32i.n a5, a1, 32
.global ip_402495c4
ip_402495c4:
 bgei a5, 1, ip_402495d1
.global ip_402495c7
ip_402495c7:
 l32i.n a6, a1, 24
.global ip_402495c9
ip_402495c9:
 add.n a4, a6, a7
.global ip_402495cb
ip_402495cb:
 bgez a10, ip_40249618
.global ip_402495ce
ip_402495ce:
 j ip_40249606
.global ip_402495d1
ip_402495d1:
 l16si a2, a7, 0
.global ip_402495d4
ip_402495d4:
 mov.n a4, a7
.global ip_402495d6
ip_402495d6:
 l16si a5, a4, 2
.global ip_402495d9
ip_402495d9:
 mull a11, a2, a15
.global ip_402495dc
ip_402495dc:
 mull a3, a2, a14
.global ip_402495df
ip_402495df:
 mull a6, a5, a14
.global ip_402495e2
ip_402495e2:
 addmi a2, a11, 0x4000
.global ip_402495e5
ip_402495e5:
 mull a5, a5, a12
.global ip_402495e8
ip_402495e8:
 add.n a2, a2, a6
.global ip_402495ea
ip_402495ea:
 addmi a3, a3, 0x4000
.global ip_402495ed
ip_402495ed:
 slli a2, a2, 1
.global ip_402495f0
ip_402495f0:
 add.n a3, a3, a5
.global ip_402495f2
ip_402495f2:
 srai a2, a2, 16
.global ip_402495f5
ip_402495f5:
 srai a3, a3, 15
.global ip_402495f8
ip_402495f8:
 s16i a2, a4, 2
.global ip_402495fb
ip_402495fb:
 s16i a3, a4, 0
.global ip_402495fe
ip_402495fe:
 addi.n a4, a4, 2
.global ip_40249600
ip_40249600:
 bne a13, a4, ip_402495d6
.global ip_40249603
ip_40249603:
 j ip_402495c7
.global ip_40249606
ip_40249606:
 l32i.n a2, a1, 28
.global ip_40249608
ip_40249608:
 addi.n a8, a8, 1
.global ip_4024960a
ip_4024960a:
 add.n a7, a7, a9
.global ip_4024960c
ip_4024960c:
 add.n a13, a13, a9
.global ip_4024960e
ip_4024960e:
 bne a2, a8, ip_4024959c
.global ip_40249611
ip_40249611:
 l32i.n a13, a1, 40
.global ip_40249613
ip_40249613:
 mov.n a9, a2
.global ip_40249615
ip_40249615:
 j ip_40249488
.global ip_40249618
ip_40249618:
 addi a2, a13, -2
.global ip_4024961b
ip_4024961b:
 l16si a2, a2, 0
.global ip_4024961e
ip_4024961e:
 mov.n a6, a10
.global ip_40249620
ip_40249620:
 l16si a5, a4, 0
.global ip_40249623
ip_40249623:
 mull a3, a2, a14
.global ip_40249626
ip_40249626:
 mull a2, a2, a12
.global ip_40249629
ip_40249629:
 mull a11, a5, a15
.global ip_4024962c
ip_4024962c:
 mull a5, a5, a14
.global ip_4024962f
ip_4024962f:
 addmi a3, a3, 0x4000
.global ip_40249632
ip_40249632:
 addmi a2, a2, 0x4000
.global ip_40249635
ip_40249635:
 add.n a3, a3, a11
.global ip_40249637
ip_40249637:
 add.n a2, a2, a5
.global ip_40249639
ip_40249639:
 srai a3, a3, 15
.global ip_4024963c
ip_4024963c:
 slli a2, a2, 1
.global ip_4024963f
ip_4024963f:
 s16i a3, a4, 2
.global ip_40249642
ip_40249642:
 srai a2, a2, 16
.global ip_40249645
ip_40249645:
 addi a4, a4, -2
.global ip_40249648
ip_40249648:
 s16i a2, a4, 2
.global ip_4024964b
ip_4024964b:
 addi.n a6, a6, -1
.global ip_4024964d
ip_4024964d:
 bnei a6, -1, ip_40249620
.global ip_40249650
ip_40249650:
 j ip_40249606
.global ip_40249655
ip_40249655:
.global ip_40249657
ip_40249657:
.global ip_40249659
ip_40249659:
.global ip_4024965c
ip_4024965c:
.global ip_4024965f
ip_4024965f:
.global ip_40249662
ip_40249662:
.global ip_40249664
ip_40249664:
.global ip_40249667
ip_40249667:
.global ip_4024966a
ip_4024966a:
.global ip_4024966c
ip_4024966c:
.global ip_4024966e
ip_4024966e:
.global ip_40249670
ip_40249670:
.global ip_40249672
ip_40249672:
.global ip_40249674
ip_40249674:
.global ip_40249676
ip_40249676:
.global ip_40249678
ip_40249678:
.global ip_4024967a
ip_4024967a:
.global ip_4024967d
ip_4024967d:
.global ip_4024967f
ip_4024967f:
.global ip_40249682
ip_40249682:
.global ip_40249684
ip_40249684:
.global ip_40249687
ip_40249687:
.global ip_4024968a
ip_4024968a:
.global ip_4024968d
ip_4024968d:
.global ip_4024968f
ip_4024968f:
.global ip_40249692
ip_40249692:
.global ip_40249694
ip_40249694:
.global ip_40249697
ip_40249697:
.global ip_4024969a
ip_4024969a:
 movi.n a12, 1
.global ip_4024969c
ip_4024969c:
.global ip_4024969e
ip_4024969e:
.global ip_402496a1
ip_402496a1:
.global ip_402496a4
ip_402496a4:
 l32i a0, a1, 108
.global ip_402496a7
ip_402496a7:
 mov.n a2, a12
.global ip_402496a9
ip_402496a9:
 l32i a13, a1, 100
.global ip_402496ac
ip_402496ac:
 l32i a12, a1, 104
.global ip_402496af
ip_402496af:
 l32i a14, a1, 96
.global ip_402496b2
ip_402496b2:
 l32i a15, a1, 92
.global ip_402496b5
ip_402496b5:
 addi a1, a1, 112
.global ip_402496b8
ip_402496b8:
 ret.n 
.size inplace_unquant,.-inplace_unquant
.align 4
.global inplace_decode16
.type inplace_decode16,@function
inplace_decode16:
.global ip_402531c0
ip_402531c0:
 addi a1, a1, -48
.global ip_402531c3
ip_402531c3:
 s32i.n a12, a1, 40
.global ip_402531c5
ip_402531c5:
 s32i.n a13, a1, 36
.global ip_402531c7
ip_402531c7:
 s32i.n a14, a1, 32
.global ip_402531c9
ip_402531c9:
 mov.n a13, a3
.global ip_402531cb
ip_402531cb:
 s32i.n a2, a1, 4
.global ip_402531cd
ip_402531cd:
 s32i.n a0, a1, 44
.global ip_402531cf
ip_402531cf:
 s32i.n a15, a1, 28
.global ip_402531d1
ip_402531d1:
 mov.n a12, a4
.global ip_402531d3
ip_402531d3:
 mov.n a2, a5
.global ip_402531d5
ip_402531d5:
 l32r a14, ip_literal_4024f0c8
.global ip_402531d8
ip_402531d8:
 mov.n a3, a4
.global ip_402531da
ip_402531da:
 bge a13, a4, ip_402531e0
.global ip_402531dd
ip_402531dd:
 or a3, a13, a13
.global ip_402531e0
ip_402531e0:
 slli a3, a3, 2
.global ip_402531e3
ip_402531e3:
 add.n a3, a14, a3
.global ip_402531e5
ip_402531e5:
 l32i.n a3, a3, 0
.global ip_402531e7
ip_402531e7:
 slli a4, a12, 2
.global ip_402531ea
ip_402531ea:
 bge a12, a13, ip_402531f0
.global ip_402531ed
ip_402531ed:
 slli a4, a13, 2
.global ip_402531f0
ip_402531f0:
 add.n a3, a3, a4
.global ip_402531f2
ip_402531f2:
 addi.n a15, a12, 1
.global ip_402531f4
ip_402531f4:
 l32i.n a3, a3, 0
.global ip_402531f6
ip_402531f6:
 mov.n a4, a15
.global ip_402531f8
ip_402531f8:
 bge a13, a15, ip_402531fd
.global ip_402531fb
ip_402531fb:
 mov.n a4, a13
.global ip_402531fd
ip_402531fd:
 slli a4, a4, 2
.global ip_40253200
ip_40253200:
 add.n a4, a14, a4
.global ip_40253202
ip_40253202:
 l32i.n a4, a4, 0
.global ip_40253204
ip_40253204:
 slli a5, a13, 2
.global ip_40253207
ip_40253207:
 blt a15, a13, ip_4025320d
.global ip_4025320a
ip_4025320a:
 slli a5, a15, 2
.global ip_4025320d
ip_4025320d:
 add.n a4, a4, a5
.global ip_4025320f
ip_4025320f:
 l32i.n a4, a4, 0
.global ip_40253211
ip_40253211:
 add.n a3, a3, a4
.global ip_40253213
ip_40253213:
 call0 ip_call_40246c20
.global ip_40253216
ip_40253216:
 bgei a13, 3, ip_4025321c
.global ip_40253219
ip_40253219:
 j ip_40253520
.global ip_4025321c
ip_4025321c:
 slli a3, a13, 2
.global ip_4025321f
ip_4025321f:
 l32i.n a4, a1, 4
.global ip_40253221
ip_40253221:
 addi a3, a3, -60
.global ip_40253224
ip_40253224:
 s32i.n a3, a1, 8
.global ip_40253226
ip_40253226:
 movi.n a10, 0
.global ip_40253228
ip_40253228:
 s32i.n a4, a1, 0
.global ip_4025322a
ip_4025322a:
 add.n a7, a14, a3
.global ip_4025322c
ip_4025322c:
 slli a9, a12, 16
.global ip_4025322f
ip_4025322f:
 slli a3, a13, 2
.global ip_40253232
ip_40253232:
 srai a5, a9, 16
.global ip_40253235
ip_40253235:
 bge a12, a13, ip_4025323b
.global ip_40253238
ip_40253238:
 j ip_40253384
.global ip_4025323b
ip_4025323b:
 l32i.n a6, a7, 60
.global ip_4025323d
ip_4025323d:
 slli a15, a15, 2
.global ip_40253240
ip_40253240:
 add.n a15, a6, a15
.global ip_40253242
ip_40253242:
 l32i.n a8, a15, 0
.global ip_40253244
ip_40253244:
 movi.n a4, 1
.global ip_40253246
ip_40253246:
 bgeu a2, a8, ip_4025324c
.global ip_40253249
ip_40253249:
 movi a4, 0
.global ip_4025324c
ip_4025324c:
 neg a4, a4
.global ip_4025324f
ip_4025324f:
 add.n a11, a6, a3
.global ip_40253251
ip_40253251:
 and a8, a4, a8
.global ip_40253254
ip_40253254:
 l32i.n a11, a11, 0
.global ip_40253256
ip_40253256:
 sub a2, a2, a8
.global ip_40253259
ip_40253259:
 bltu a2, a11, ip_4025325f
.global ip_4025325c
ip_4025325c:
 j ip_40253329
.global ip_4025325f
ip_4025325f:
 l32i.n a6, a7, 56
.global ip_40253261
ip_40253261:
 addi.n a12, a13, -1
.global ip_40253263
ip_40253263:
 add.n a6, a6, a3
.global ip_40253265
ip_40253265:
 l32i.n a8, a6, 0
.global ip_40253267
ip_40253267:
 mov.n a6, a12
.global ip_40253269
ip_40253269:
 bltu a2, a8, ip_4025326f
.global ip_4025326c
ip_4025326c:
 j ip_40253354
.global ip_4025326f
ip_4025326f:
 l32i.n a8, a7, 52
.global ip_40253271
ip_40253271:
 addi a12, a13, -2
.global ip_40253274
ip_40253274:
 add.n a8, a8, a3
.global ip_40253276
ip_40253276:
 l32i.n a8, a8, 0
.global ip_40253278
ip_40253278:
 bltu a2, a8, ip_4025327e
.global ip_4025327b
ip_4025327b:
 j ip_40253354
.global ip_4025327e
ip_4025327e:
 l32i.n a8, a7, 48
.global ip_40253280
ip_40253280:
 addi a12, a13, -3
.global ip_40253283
ip_40253283:
 add.n a8, a8, a3
.global ip_40253285
ip_40253285:
 l32i.n a8, a8, 0
.global ip_40253287
ip_40253287:
 bltu a2, a8, ip_4025328d
.global ip_4025328a
ip_4025328a:
 j ip_40253354
.global ip_4025328d
ip_4025328d:
 l32i.n a8, a7, 44
.global ip_4025328f
ip_4025328f:
 addi a12, a13, -4
.global ip_40253292
ip_40253292:
 add.n a8, a8, a3
.global ip_40253294
ip_40253294:
 l32i.n a8, a8, 0
.global ip_40253296
ip_40253296:
 bltu a2, a8, ip_4025329c
.global ip_40253299
ip_40253299:
 j ip_40253354
.global ip_4025329c
ip_4025329c:
 l32i.n a8, a7, 40
.global ip_4025329e
ip_4025329e:
 addi a12, a13, -5
.global ip_402532a1
ip_402532a1:
 add.n a8, a8, a3
.global ip_402532a3
ip_402532a3:
 l32i.n a8, a8, 0
.global ip_402532a5
ip_402532a5:
 bltu a2, a8, ip_402532ab
.global ip_402532a8
ip_402532a8:
 j ip_40253354
.global ip_402532ab
ip_402532ab:
 l32i.n a8, a7, 36
.global ip_402532ad
ip_402532ad:
 addi a12, a13, -6
.global ip_402532b0
ip_402532b0:
 add.n a8, a8, a3
.global ip_402532b2
ip_402532b2:
 l32i.n a8, a8, 0
.global ip_402532b4
ip_402532b4:
 bltu a2, a8, ip_402532ba
.global ip_402532b7
ip_402532b7:
 j ip_40253354
.global ip_402532ba
ip_402532ba:
 l32i.n a8, a7, 32
.global ip_402532bc
ip_402532bc:
 addi a12, a13, -7
.global ip_402532bf
ip_402532bf:
 add.n a8, a8, a3
.global ip_402532c1
ip_402532c1:
 l32i.n a8, a8, 0
.global ip_402532c3
ip_402532c3:
 bltu a2, a8, ip_402532c9
.global ip_402532c6
ip_402532c6:
 j ip_40253354
.global ip_402532c9
ip_402532c9:
 l32i.n a8, a7, 28
.global ip_402532cb
ip_402532cb:
 addi a12, a13, -8
.global ip_402532ce
ip_402532ce:
 add.n a8, a8, a3
.global ip_402532d0
ip_402532d0:
 l32i.n a8, a8, 0
.global ip_402532d2
ip_402532d2:
 bgeu a2, a8, ip_40253354
.global ip_402532d5
ip_402532d5:
 l32i.n a8, a7, 24
.global ip_402532d7
ip_402532d7:
 addi a12, a13, -9
.global ip_402532da
ip_402532da:
 add.n a8, a8, a3
.global ip_402532dc
ip_402532dc:
 l32i.n a8, a8, 0
.global ip_402532de
ip_402532de:
 bgeu a2, a8, ip_40253354
.global ip_402532e1
ip_402532e1:
 l32i.n a8, a7, 20
.global ip_402532e3
ip_402532e3:
 addi a12, a13, -10
.global ip_402532e6
ip_402532e6:
 add.n a8, a8, a3
.global ip_402532e8
ip_402532e8:
 l32i.n a8, a8, 0
.global ip_402532ea
ip_402532ea:
 bgeu a2, a8, ip_40253354
.global ip_402532ed
ip_402532ed:
 l32i.n a8, a7, 16
.global ip_402532ef
ip_402532ef:
 addi a12, a13, -11
.global ip_402532f2
ip_402532f2:
 add.n a8, a8, a3
.global ip_402532f4
ip_402532f4:
 l32i.n a8, a8, 0
.global ip_402532f6
ip_402532f6:
 bgeu a2, a8, ip_40253354
.global ip_402532f9
ip_402532f9:
 l32i.n a8, a7, 12
.global ip_402532fb
ip_402532fb:
 addi a12, a13, -12
.global ip_402532fe
ip_402532fe:
 add.n a8, a8, a3
.global ip_40253300
ip_40253300:
 l32i.n a8, a8, 0
.global ip_40253302
ip_40253302:
 bgeu a2, a8, ip_40253354
.global ip_40253305
ip_40253305:
 l32i.n a8, a7, 8
.global ip_40253307
ip_40253307:
 addi a12, a13, -13
.global ip_4025330a
ip_4025330a:
 add.n a8, a8, a3
.global ip_4025330c
ip_4025330c:
 l32i.n a8, a8, 0
.global ip_4025330e
ip_4025330e:
 bgeu a2, a8, ip_40253354
.global ip_40253311
ip_40253311:
 l32i.n a8, a7, 4
.global ip_40253313
ip_40253313:
 addi a12, a13, -14
.global ip_40253316
ip_40253316:
 add.n a8, a8, a3
.global ip_40253318
ip_40253318:
 l32i.n a8, a8, 0
.global ip_4025331a
ip_4025331a:
 bgeu a2, a8, ip_40253354
.global ip_4025331d
ip_4025331d:
 l32i.n a8, a7, 0
.global ip_4025331f
ip_4025331f:
 addi a12, a13, -15
.global ip_40253322
ip_40253322:
 add.n a3, a8, a3
.global ip_40253324
ip_40253324:
 l32i.n a8, a3, 0
.global ip_40253326
ip_40253326:
 j ip_40253354
.global ip_40253329
ip_40253329:
 addi a15, a15, -4
.global ip_4025332c
ip_4025332c:
 l32i.n a8, a15, 0
.global ip_4025332e
ip_4025332e:
 bgeu a2, a8, ip_4025335d
.global ip_40253331
ip_40253331:
 addi a6, a15, -4
.global ip_40253334
ip_40253334:
 l32i.n a8, a6, 0
.global ip_40253336
ip_40253336:
 addi a6, a6, -4
.global ip_40253339
ip_40253339:
 addi.n a12, a12, -1
.global ip_4025333b
ip_4025333b:
 bltu a2, a8, ip_40253334
.global ip_4025333e
ip_4025333e:
 mov.n a3, a12
.global ip_40253340
ip_40253340:
 slli a9, a3, 16
.global ip_40253343
ip_40253343:
 srai a11, a9, 16
.global ip_40253346
ip_40253346:
 addi.n a6, a13, -1
.global ip_40253348
ip_40253348:
 j ip_40253361
.global ip_40253354
ip_40253354:
 slli a9, a12, 16
.global ip_40253357
ip_40253357:
 srai a11, a9, 16
.global ip_4025335a
ip_4025335a:
 j ip_40253361
.global ip_4025335d
ip_4025335d:
 mov.n a11, a5
.global ip_4025335f
ip_4025335f:
 addi.n a6, a13, -1
.global ip_40253361
ip_40253361:
 slli a4, a4, 16
.global ip_40253364
ip_40253364:
 srai a4, a4, 16
.global ip_40253367
ip_40253367:
 add.n a3, a4, a5
.global ip_40253369
ip_40253369:
 sub a3, a3, a11
.global ip_4025336c
ip_4025336c:
 xor a3, a4, a3
.global ip_4025336f
ip_4025336f:
 slli a3, a3, 16
.global ip_40253372
ip_40253372:
 srai a3, a3, 16
.global ip_40253375
ip_40253375:
 mull a4, a3, a3
.global ip_40253378
ip_40253378:
 l32i.n a5, a1, 0
.global ip_4025337a
ip_4025337a:
 sub a2, a2, a8
.global ip_4025337d
ip_4025337d:
 s16i a3, a5, 0
.global ip_4025337f
ip_4025337f:
 add.n a10, a10, a4
.global ip_40253381
ip_40253381:
 j ip_40253501
.global ip_40253384
ip_40253384:
 slli a4, a12, 2
.global ip_40253387
ip_40253387:
 add.n a4, a14, a4
.global ip_40253389
ip_40253389:
 l32i.n a6, a4, 0
.global ip_4025338b
ip_4025338b:
 slli a15, a15, 2
.global ip_4025338e
ip_4025338e:
 add.n a15, a14, a15
.global ip_40253390
ip_40253390:
 add.n a6, a6, a3
.global ip_40253392
ip_40253392:
 l32i.n a4, a15, 0
.global ip_40253394
ip_40253394:
 l32i.n a6, a6, 0
.global ip_40253396
ip_40253396:
 add.n a4, a4, a3
.global ip_40253398
ip_40253398:
 l32i.n a4, a4, 0
.global ip_4025339a
ip_4025339a:
 bltu a2, a6, ip_402533b2
.global ip_4025339d
ip_4025339d:
 bgeu a2, a4, ip_402533b2
.global ip_402533a0
ip_402533a0:
 l32i.n a3, a1, 0
.global ip_402533a2
ip_402533a2:
 movi.n a4, 0
.global ip_402533a4
ip_402533a4:
 sub a2, a2, a6
.global ip_402533a7
ip_402533a7:
 mov.n a11, a5
.global ip_402533a9
ip_402533a9:
 s16i a4, a3, 0
.global ip_402533ab
ip_402533ab:
 addi.n a6, a13, -1
.global ip_402533ad
ip_402533ad:
 mov.n a5, a3
.global ip_402533af
ip_402533af:
 j ip_40253501
.global ip_402533b2
ip_402533b2:
 movi.n a6, 1
.global ip_402533b4
ip_402533b4:
 bgeu a2, a4, ip_402533b9
.global ip_402533b7
ip_402533b7:
 movi.n a6, 0
.global ip_402533b9
ip_402533b9:
 addi.n a8, a12, -1
.global ip_402533bb
ip_402533bb:
 slli a9, a8, 2
.global ip_402533be
ip_402533be:
 add.n a9, a14, a9
.global ip_402533c0
ip_402533c0:
 l32i.n a11, a9, 0
.global ip_402533c2
ip_402533c2:
 neg a6, a6
.global ip_402533c5
ip_402533c5:
 add.n a11, a11, a3
.global ip_402533c7
ip_402533c7:
 and a9, a6, a4
.global ip_402533ca
ip_402533ca:
 l32i.n a4, a11, 0
.global ip_402533cc
ip_402533cc:
 sub a2, a2, a9
.global ip_402533cf
ip_402533cf:
 bltu a2, a4, ip_402533d5
.global ip_402533d2
ip_402533d2:
 j ip_402534d5
.global ip_402533d5
ip_402533d5:
 addi a8, a12, -2
.global ip_402533d8
ip_402533d8:
 slli a4, a8, 2
.global ip_402533db
ip_402533db:
 add.n a4, a14, a4
.global ip_402533dd
ip_402533dd:
 l32i.n a4, a4, 0
.global ip_402533df
ip_402533df:
 add.n a4, a4, a3
.global ip_402533e1
ip_402533e1:
 l32i.n a4, a4, 0
.global ip_402533e3
ip_402533e3:
 bltu a2, a4, ip_402533e9
.global ip_402533e6
ip_402533e6:
 j ip_402534d5
.global ip_402533e9
ip_402533e9:
 addi a8, a12, -3
.global ip_402533ec
ip_402533ec:
 slli a4, a8, 2
.global ip_402533ef
ip_402533ef:
 add.n a4, a14, a4
.global ip_402533f1
ip_402533f1:
 l32i.n a4, a4, 0
.global ip_402533f3
ip_402533f3:
 add.n a4, a4, a3
.global ip_402533f5
ip_402533f5:
 l32i.n a4, a4, 0
.global ip_402533f7
ip_402533f7:
 bltu a2, a4, ip_402533fd
.global ip_402533fa
ip_402533fa:
 j ip_402534d5
.global ip_402533fd
ip_402533fd:
 addi a8, a12, -4
.global ip_40253400
ip_40253400:
 slli a4, a8, 2
.global ip_40253403
ip_40253403:
 add.n a4, a14, a4
.global ip_40253405
ip_40253405:
 l32i.n a4, a4, 0
.global ip_40253407
ip_40253407:
 add.n a4, a4, a3
.global ip_40253409
ip_40253409:
 l32i.n a4, a4, 0
.global ip_4025340b
ip_4025340b:
 bltu a2, a4, ip_40253411
.global ip_4025340e
ip_4025340e:
 j ip_402534d5
.global ip_40253411
ip_40253411:
 addi a8, a12, -5
.global ip_40253414
ip_40253414:
 slli a4, a8, 2
.global ip_40253417
ip_40253417:
 add.n a4, a14, a4
.global ip_40253419
ip_40253419:
 l32i.n a4, a4, 0
.global ip_4025341b
ip_4025341b:
 add.n a4, a4, a3
.global ip_4025341d
ip_4025341d:
 l32i.n a4, a4, 0
.global ip_4025341f
ip_4025341f:
 bltu a2, a4, ip_40253425
.global ip_40253422
ip_40253422:
 j ip_402534d5
.global ip_40253425
ip_40253425:
 addi a8, a12, -6
.global ip_40253428
ip_40253428:
 slli a4, a8, 2
.global ip_4025342b
ip_4025342b:
 add.n a4, a14, a4
.global ip_4025342d
ip_4025342d:
 l32i.n a4, a4, 0
.global ip_4025342f
ip_4025342f:
 add.n a4, a4, a3
.global ip_40253431
ip_40253431:
 l32i.n a4, a4, 0
.global ip_40253433
ip_40253433:
 bltu a2, a4, ip_40253439
.global ip_40253436
ip_40253436:
 j ip_402534d5
.global ip_40253439
ip_40253439:
 addi a8, a12, -7
.global ip_4025343c
ip_4025343c:
 slli a4, a8, 2
.global ip_4025343f
ip_4025343f:
 add.n a4, a14, a4
.global ip_40253441
ip_40253441:
 l32i.n a4, a4, 0
.global ip_40253443
ip_40253443:
 add.n a4, a4, a3
.global ip_40253445
ip_40253445:
 l32i.n a4, a4, 0
.global ip_40253447
ip_40253447:
 bltu a2, a4, ip_4025344d
.global ip_4025344a
ip_4025344a:
 j ip_402534d5
.global ip_4025344d
ip_4025344d:
 addi a8, a12, -8
.global ip_40253450
ip_40253450:
 slli a4, a8, 2
.global ip_40253453
ip_40253453:
 add.n a4, a14, a4
.global ip_40253455
ip_40253455:
 l32i.n a4, a4, 0
.global ip_40253457
ip_40253457:
 add.n a4, a4, a3
.global ip_40253459
ip_40253459:
 l32i.n a4, a4, 0
.global ip_4025345b
ip_4025345b:
 bgeu a2, a4, ip_402534d5
.global ip_4025345e
ip_4025345e:
 addi a8, a12, -9
.global ip_40253461
ip_40253461:
 slli a4, a8, 2
.global ip_40253464
ip_40253464:
 add.n a4, a14, a4
.global ip_40253466
ip_40253466:
 l32i.n a4, a4, 0
.global ip_40253468
ip_40253468:
 add.n a4, a4, a3
.global ip_4025346a
ip_4025346a:
 l32i.n a4, a4, 0
.global ip_4025346c
ip_4025346c:
 bgeu a2, a4, ip_402534d5
.global ip_4025346f
ip_4025346f:
 addi a8, a12, -10
.global ip_40253472
ip_40253472:
 slli a4, a8, 2
.global ip_40253475
ip_40253475:
 add.n a4, a14, a4
.global ip_40253477
ip_40253477:
 l32i.n a4, a4, 0
.global ip_40253479
ip_40253479:
 add.n a4, a4, a3
.global ip_4025347b
ip_4025347b:
 l32i.n a4, a4, 0
.global ip_4025347d
ip_4025347d:
 bgeu a2, a4, ip_402534d5
.global ip_40253480
ip_40253480:
 addi a8, a12, -11
.global ip_40253483
ip_40253483:
 slli a4, a8, 2
.global ip_40253486
ip_40253486:
 add.n a4, a14, a4
.global ip_40253488
ip_40253488:
 l32i.n a4, a4, 0
.global ip_4025348a
ip_4025348a:
 add.n a4, a4, a3
.global ip_4025348c
ip_4025348c:
 l32i.n a4, a4, 0
.global ip_4025348e
ip_4025348e:
 bgeu a2, a4, ip_402534d5
.global ip_40253491
ip_40253491:
 addi a8, a12, -12
.global ip_40253494
ip_40253494:
 slli a4, a8, 2
.global ip_40253497
ip_40253497:
 add.n a4, a14, a4
.global ip_40253499
ip_40253499:
 l32i.n a4, a4, 0
.global ip_4025349b
ip_4025349b:
 add.n a4, a4, a3
.global ip_4025349d
ip_4025349d:
 l32i.n a4, a4, 0
.global ip_4025349f
ip_4025349f:
 bgeu a2, a4, ip_402534d5
.global ip_402534a2
ip_402534a2:
 addi a8, a12, -13
.global ip_402534a5
ip_402534a5:
 slli a4, a8, 2
.global ip_402534a8
ip_402534a8:
 add.n a4, a14, a4
.global ip_402534aa
ip_402534aa:
 l32i.n a4, a4, 0
.global ip_402534ac
ip_402534ac:
 add.n a4, a4, a3
.global ip_402534ae
ip_402534ae:
 l32i.n a4, a4, 0
.global ip_402534b0
ip_402534b0:
 bgeu a2, a4, ip_402534d5
.global ip_402534b3
ip_402534b3:
 addi a8, a12, -14
.global ip_402534b6
ip_402534b6:
 slli a4, a8, 2
.global ip_402534b9
ip_402534b9:
 add.n a4, a14, a4
.global ip_402534bb
ip_402534bb:
 l32i.n a4, a4, 0
.global ip_402534bd
ip_402534bd:
 add.n a4, a4, a3
.global ip_402534bf
ip_402534bf:
 l32i.n a4, a4, 0
.global ip_402534c1
ip_402534c1:
 bgeu a2, a4, ip_402534d5
.global ip_402534c4
ip_402534c4:
 addi a12, a12, -15
.global ip_402534c7
ip_402534c7:
 slli a4, a12, 2
.global ip_402534ca
ip_402534ca:
 add.n a4, a14, a4
.global ip_402534cc
ip_402534cc:
 l32i.n a4, a4, 0
.global ip_402534ce
ip_402534ce:
 add.n a3, a4, a3
.global ip_402534d0
ip_402534d0:
 l32i.n a4, a3, 0
.global ip_402534d2
ip_402534d2:
 j ip_402534d7
.global ip_402534d5
ip_402534d5:
 mov.n a12, a8
.global ip_402534d7
ip_402534d7:
 slli a3, a6, 16
.global ip_402534da
ip_402534da:
 srai a3, a3, 16
.global ip_402534dd
ip_402534dd:
 slli a9, a12, 16
.global ip_402534e0
ip_402534e0:
 add.n a5, a3, a5
.global ip_402534e2
ip_402534e2:
 srai a11, a9, 16
.global ip_402534e5
ip_402534e5:
 sub a5, a5, a11
.global ip_402534e8
ip_402534e8:
 xor a3, a3, a5
.global ip_402534eb
ip_402534eb:
 slli a3, a3, 16
.global ip_402534ee
ip_402534ee:
 srai a3, a3, 16
.global ip_402534f1
ip_402534f1:
 mull a5, a3, a3
.global ip_402534f4
ip_402534f4:
 sub a2, a2, a4
.global ip_402534f7
ip_402534f7:
 l32i.n a4, a1, 0
.global ip_402534f9
ip_402534f9:
 add.n a10, a10, a5
.global ip_402534fb
ip_402534fb:
 s16i a3, a4, 0
.global ip_402534fd
ip_402534fd:
 addi.n a6, a13, -1
.global ip_402534ff
ip_402534ff:
 mov.n a5, a4
.global ip_40253501
ip_40253501:
 addi.n a5, a5, 2
.global ip_40253503
ip_40253503:
 s32i.n a5, a1, 0
.global ip_40253505
ip_40253505:
 mov.n a13, a6
.global ip_40253507
ip_40253507:
 addi a7, a7, -4
.global ip_4025350a
ip_4025350a:
 beqi a6, 2, ip_40253512
.global ip_4025350d
ip_4025350d:
 addi.n a15, a12, 1
.global ip_4025350f
ip_4025350f:
 j ip_4025322f
.global ip_40253512
ip_40253512:
 l32i.n a4, a1, 8
.global ip_40253514
ip_40253514:
 addi a3, a4, 52
 srli a3, a3, 1
.global ip_40253517
ip_40253517:
 l32i.n a4, a1, 4
.global ip_40253519
ip_40253519:
 add.n a4, a4, a3
.global ip_4025351b
ip_4025351b:
 s32i.n a4, a1, 4
.global ip_4025351d
ip_4025351d:
 j ip_40253528
.global ip_40253520
ip_40253520:
 slli a11, a12, 16
.global ip_40253523
ip_40253523:
 srai a11, a11, 16
.global ip_40253526
ip_40253526:
 movi.n a10, 0
.global ip_40253528
ip_40253528:
 slli a12, a12, 1
.global ip_4025352b
ip_4025352b:
 addi.n a12, a12, 1
.global ip_4025352d
ip_4025352d:
 movi.n a4, 1
.global ip_4025352f
ip_4025352f:
 bgeu a2, a12, ip_40253534
.global ip_40253532
ip_40253532:
 movi.n a4, 0
.global ip_40253534
ip_40253534:
 neg a4, a4
.global ip_40253537
ip_40253537:
 and a12, a4, a12
.global ip_4025353a
ip_4025353a:
 sub a12, a2, a12
.global ip_4025353d
ip_4025353d:
 addi a2, a12, 1
.global ip_40253540
ip_40253540:
 srli a3, a2, 1
.global ip_40253543
ip_40253543:
 beqz a3, ip_4025354c
.global ip_40253546
ip_40253546:
 slli a12, a3, 1
.global ip_40253549
ip_40253549:
 sub a12, a2, a12
.global ip_4025354c
ip_4025354c:
 slli a4, a4, 16
.global ip_4025354f
ip_4025354f:
 srai a4, a4, 16
.global ip_40253552
ip_40253552:
 slli a3, a3, 16
.global ip_40253555
ip_40253555:
 srai a3, a3, 16
.global ip_40253558
ip_40253558:
 add.n a11, a4, a11
.global ip_4025355a
ip_4025355a:
 neg a12, a12
.global ip_4025355d
ip_4025355d:
 sub a11, a11, a3
.global ip_40253560
ip_40253560:
 slli a12, a12, 16
.global ip_40253563
ip_40253563:
 srai a12, a12, 16
.global ip_40253566
ip_40253566:
 xor a4, a4, a11
.global ip_40253569
ip_40253569:
 add.n a3, a3, a12
.global ip_4025356b
ip_4025356b:
 slli a4, a4, 16
.global ip_4025356e
ip_4025356e:
 xor a3, a12, a3
.global ip_40253571
ip_40253571:
 srai a4, a4, 16
.global ip_40253574
ip_40253574:
 mull a5, a4, a4
.global ip_40253577
ip_40253577:
 slli a3, a3, 16
.global ip_4025357a
ip_4025357a:
 srai a3, a3, 16
.global ip_4025357d
ip_4025357d:
 add.n a10, a5, a10
.global ip_4025357f
ip_4025357f:
 mull a2, a3, a3
.global ip_40253582
ip_40253582:
 l32i.n a5, a1, 4
.global ip_40253584
ip_40253584:
 l32i.n a0, a1, 44
.global ip_40253586
ip_40253586:
 add.n a2, a2, a10
.global ip_40253588
ip_40253588:
 l32i.n a12, a1, 40
.global ip_4025358a
ip_4025358a:
 l32i.n a13, a1, 36
.global ip_4025358c
ip_4025358c:
 l32i.n a14, a1, 32
.global ip_4025358e
ip_4025358e:
 l32i.n a15, a1, 28
.global ip_40253590
ip_40253590:
 s16i a4, a5, 0
.global ip_40253592
ip_40253592:
 s16i a3, a5, 2
.global ip_40253594
ip_40253594:
 addi a1, a1, 48
.global ip_40253597
ip_40253597:
 ret.n 
.size inplace_decode16,.-inplace_decode16
.global ip_used_end
ip_used_end:
.space 1788-(.-ip_pool_start),0
.section .text.patch2,"ax",@progbits
.global ip_guard
ip_guard:
 bnei a6,1,ip_fallback
 blti a4,1,ip_fallback
 srli a8,a4,15
 bnez a8,ip_fallback
 j inplace_unquant
.global ip_fallback
ip_fallback:
 addi a1,a1,-112
 j ip_resume
.global ip_guard_end
ip_guard_end:
.space 94-(.-ip_guard),0
.end no-transform
