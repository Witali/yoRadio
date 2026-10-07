set pagination off
set confirm off
set remotetimeout 10
target remote localhost:1237
break aac_pointer_audit_report
continue
delete 1
set $frames=0
set $extensions=0
set $reads=0
break *sbr_extract_extended_data
commands
silent
set $extensions=$extensions+1
if $extensions<6
printf "EXT call=%u ps=%p\n",$extensions,$a1
end
continue
end
break *__wrap_ps_read_data
commands
silent
set $reads=$reads+1
continue
end
break *aac_pointer_audit_frame
commands
silent
if $a4==0
set $frames=$frames+1
set $core=(aac_analysis_core_t*)$a0
set $owner=(aac_high_owner_t*)$core->sbr
if $frames<31
printf "FRAME frame=%u sync=%d init_ps=%d ps_detected=%d core_ps=%d core_ch=%d element_id=%d payload=%d extensions=%u ps_reads=%u\n",$frames,$owner->channel[0].sync_state,$owner->initialize_ps,$owner->ps->detected,$core->mc.ps_present,$core->mc.channels,$core->sbr_stream->element[0].element_id,$core->sbr_stream->element[0].payload_bytes,$extensions,$reads
end
if $frames==32
printf "SUMMARY frames=%u extensions=%u ps_reads=%u\n",$frames,$extensions,$reads
detach
quit
end
end
continue
end
continue

