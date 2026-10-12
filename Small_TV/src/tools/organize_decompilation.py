"""Categorize a Ghidra export and apply evidence-backed names, retaining addresses.

Reference output remains pseudocode, excluded from the native ESP-IDF build.
Run only when intentionally updating the reverse-engineering reference snapshot.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
NAMES = {
    "4200807e":"dev_null_close", "420080b4":"dev_null_read", "420080e8":"dev_null_write",
    "4200811c":"dev_null_seek", "42008166":"dev_null_open", "4200819c":"dev_null_stat",
    "420081f4":"dev_null_fstat", "4200823a":"register_dev_null", "4200825c":"initialize_dev_null",
    "4200826a":"system_timer_alarm_callback", "420083b6":"initialize_system_timer",
    "42008552":"load_settings_and_defaults", "42008a00":"save_settings_sector",
    "42008a34":"unpack_rgb565_channels", "42008a6a":"rgb565_to_rgb888", "42008a96":"rgb888_to_rgb565",
    "42008aae":"hex_color_to_rgb565", "42008ace":"parse_hex_byte", "42008b58":"parse_hex_color",
    "42008bd2":"set_backlight_duty", "42008c4c":"update_day_night_backlight", "42008d62":"initialize_backlight_pwm",
    "42008e08":"initialize_selected_clock_theme", "42008e56":"application_main",
    "4200917c":"st7789_spi_dc_callback", "42009192":"st7789_delay_ms", "420091b2":"st7789_reset",
    "420091e4":"st7789_write_command", "4200925a":"st7789_write_data", "420092d0":"st7789_set_window",
    "4200934a":"st7789_initialize", "4200950e":"st7789_blit_rectangle", "4200958a":"st7789_draw_pixel",
    "420095c4":"draw_filled_circle", "42009644":"draw_thick_line", "42009936":"fill_rectangle",
    "42009a0a":"clear_display", "42009a24":"initialize_display", "42009a38":"draw_dial_hand",
    "42009b32":"draw_dial_ticks", "42009ccc":"update_dial_hands", "4200a156":"initialize_dial_clock",
    "4200a5b0":"render_dial_clock", "4200a5be":"draw_glyph_with_background", "4200a81e":"draw_glyph_transparent",
    "4200aa1e":"draw_encoded_text", "4200aae0":"draw_large_digit", "4200abee":"draw_ascii_text",
    "4200acae":"draw_clock_separator", "4200aebe":"initialize_classic_clock", "4200aefc":"draw_city_label",
    "4200af5e":"draw_weather_description", "4200afcc":"draw_classic_clock_time", "4200b340":"draw_weather_status",
    "4200b5cc":"load_animation_frame_table", "4200b738":"render_classic_clock", "4200bb20":"initialize_photo_slideshow",
    "4200bb4c":"draw_next_enabled_photo", "4200bc36":"advance_photo_slideshow", "4200bd26":"initialize_simple_clock",
    "4200bd8c":"render_simple_clock", "4200c100":"draw_initial_clock_screen", "4200c1c8":"draw_startup_connection_status",
    "4200c33e":"jpeg_input_callback", "4200c374":"jpeg_output_callback", "4200c4ac":"decode_jpeg",
    "4200c518":"draw_jpeg_at_flash_offset", "4200c578":"stop_wifi_http_server", "4200c5ec":"start_wifi_http_server",
    "4200c602":"wifi_station_event_handler", "4200c6e2":"wifi_ap_event_handler", "4200c74e":"captive_dns_task",
    "4200c956":"inspect_netif_dhcp_state", "4200c9e0":"scan_wifi_access_points", "4200ca30":"initialize_wifi_station",
    "4200ce40":"update_wifi_connection_mode", "4200ce9e":"configure_softap_network", "4200d06e":"initialize_wifi_softap",
    "4200d394":"send_http_json_number", "4200d4be":"http_captive_redirect", "4200daaa":"find_multipart_bytes",
    "4200db12":"parse_multipart_upload_body", "4200eefe":"parse_json_switch_value", "4200f764":"parse_photo_interval",
    "4200f85c":"parse_night_start_hour", "4200f972":"parse_night_stop_hour", "4200fa88":"start_http_server",
    "4200fcbe":"stop_http_server", "4200fccc":"weather_http_event_handler", "42010864":"fetch_current_weather",
    "420109de":"sntp_sync_notification", "42010a06":"configure_sntp_and_timezone", "42010b70":"update_local_time",
    "42010c4e":"draw_wifi_setup_instructions", "42010eca":"draw_weather_bmp",
}
GLOBALS = {
    "3fcb7b9c":"enabled_photo_mask", "3fcb7ba0":"wifi_ssid", "3fcb7be1":"wifi_password",
    "3fcb7c22":"ntp_server", "3fcb7c63":"country_code", "3fcb7c77":"city_name", "3fcb7cb8":"weather_api_key",
    "3fcb7d00":"selected_animation", "3fcb7d04":"selected_clock_theme", "3fcb7d08":"fahrenheit_flag",
    "3fcb7d0c":"hour12_flag", "3fcb7d10":"miles_flag", "3fcb7d14":"browser_time_flag", "3fcb7d18":"date_format",
    "3fcb7d1c":"day_backlight_per_mille", "3fcb7d20":"clock_hour_color_rgb565", "3fcb7d24":"clock_minute_color_rgb565",
    "3fcb7d28":"clock_detail_color_rgb565", "3fcb7d2c":"night_mode_flag", "3fcb7d30":"night_start_hour",
    "3fcb7d34":"night_stop_hour", "3fcb7d38":"night_backlight_per_mille", "3fcb7d3c":"photo_interval_seconds",
    "3fcb7d40":"photo1_size", "3fcb7d44":"photo2_size", "3fcb7d48":"photo3_size", "3fcb7d4c":"photo4_size", "3fcb7d50":"photo5_size",
    "3fcb7da8":"glyph_pixel_buffer", "3fcba5a8":"animation_frame_table", "3fcba9a8":"clock_text_buffer",
    "3fcbffc8":"local_year", "3fcbffcc":"local_month", "3fcbffcd":"local_day", "3fcbffce":"local_hour",
    "3fcbffcf":"local_minute", "3fcbffd0":"local_second", "3fcbffd1":"local_weekday", "3fcbffa8":"posix_timezone",
    "3fcc3a48":"weather_humidity", "3fcc3a4c":"weather_temperature_c", "3fcc3a70":"wifi_http_server_handle", "3fcc3a74":"wifi_connection_state",
}
LOCALS = {
    "42008a34":{"param_1":"color_rgb565","param_2":"red_out","param_3":"green_out","param_4":"blue_out"},
    "42008a6a":{"param_1":"color_rgb565","abStack_11":"red_channel","bStack_12":"green_channel","bStack_13":"blue_channel"},
    "42008a96":{"param_1":"red_channel","param_2":"green_channel","param_3":"blue_channel"},
    "42008aae":{"param_1":"color_rgb888"},
    "42008ace":{"param_1":"high_hex_character","param_2":"low_hex_character","uVar2":"high_nibble","uVar1":"low_nibble"},
    "42008b58":{"param_1":"hex_color_text","cVar1":"text_length","iVar3":"red_channel","uVar4":"green_channel","uVar2":"parsed_rgb888"},
    "42008bd2":{"arg0":"duty_per_mille","iVar1":"ledc_result"},
    "4200917c":{"arg0":"transaction"}, "42009192":{"arg0":"milliseconds"},
    "420091e4":{"arg0":"command","iVar1":"spi_result","sStack_38":"transaction","auStack_41":"command_storage"},
    "4200925a":{"arg0":"data","arg1":"byte_count","iVar1":"spi_result","sStack_38":"transaction"},
    "420092d0":{"arg0":"x_start","arg1":"y_start","arg2":"x_end","arg3":"y_end",
                "uStack_24":"x_start_high","uStack_23":"x_start_low","uStack_22":"x_end_high","uStack_21":"x_end_low",
                "uStack_28":"y_start_high","uStack_27":"y_start_low","uStack_26":"y_end_high","uStack_25":"y_end_low"},
    "4200934a":{"iVar1":"initialization_result","local_90":"spi_device_config","sStack_60":"spi_bus_config","gStack_28":"gpio_config"},
    "4200950e":{"arg0":"x_start","arg1":"y_start","arg2":"x_end","arg3":"y_end","arg4":"pixel_data"},
    "4200958a":{"arg0":"x","arg1":"y","arg2":"color_rgb565"},
    "420095c4":{"param_1":"center_x","param_2":"center_y","param_3":"radius","param_4":"color_rgb565",
                "iVar1":"relative_x","iVar2":"relative_y","iVar3":"negative_radius"},
    "42009644":{"param_1":"x_start","param_2":"y_start","param_3":"x_end","param_4":"y_end","param_5":"color_rgb565","param_6":"line_width"},
    "42009936":{"param_1":"x","param_2":"y","param_3":"width","param_4":"height","param_5":"color_rgb565"},
    "42009a0a":{"param_1":"background_rgb565"},
    "4200c33e":{"param_1":"decoder","param_2":"read_buffer","param_3":"requested_bytes","piVar1":"flash_read_position"},
    "4200c374":{"param_1":"decoder","param_2":"decoded_pixels","param_3":"output_rectangle","arg4":"stripe_buffer"},
    "4200c518":{"param_1":"x","param_2":"y","param_3":"flash_offset"},
    "4200c602":{"param_1":"event_context","param_2":"event_base","param_3":"event_id","param_4":"event_data"},
    "4200c6e2":{"param_1":"event_context","param_2":"event_base","param_3":"event_id","param_4":"event_data"},
    "4200eefe":{"param_1":"json_text","param_2":"field_name"},
    "4200f764":{"param_1":"interval_text"}, "4200f85c":{"param_1":"start_hour_text"}, "4200f972":{"param_1":"stop_hour_text"},
}


def category(address: str, name: str) -> str:
    value=int(address,16)
    if name.startswith("uri_"):
        return "http_photos" if any(token in name for token in ("upload", "Photo_File", "checkbox", "display_time", "photo")) else "http_settings"
    if value<0x4200826a or value>=0x42011000: return "sdk_platform"
    if value<0x42008552: return "application"
    if value<0x42008bd2: return "settings_colors"
    if value<0x42008e08: return "backlight"
    if value<0x4200917c: return "application"
    if value<0x420095c4: return "display_spi"
    if value<0x42009a38: return "display_graphics"
    if value<0x4200a5be: return "clock_dial"
    if value<0x4200aebe: return "display_fonts"
    if value<0x4200c33e: return "clock_themes"
    if value<0x4200c578 or address=="42010eca": return "media_images"
    if value<0x4200d34a: return "wifi_dns"
    if value<0x4200fcbe: return "http_server"
    if value<0x420109de: return "weather"
    return "time_setup"


def native_module(group: str) -> str:
    return {"application":"app/app_main.c", "settings_colors":"app/settings/settings.c", "backlight":"app/display/backlight.c",
            "display_spi":"app/display/st7789.c", "display_graphics":"app/display/st7789.c", "clock_dial":"app/display/clock_ui.c",
            "display_fonts":"app/display/st7789.c", "clock_themes":"app/display/clock_ui.c", "media_images":"app/media/assets.c",
            "wifi_dns":"app/network/wifi.c + app/network/dns.c", "http_photos":"app/web/photo_api.c + app/media/photo_upload.c",
            "http_settings":"app/web/settings_api.c", "http_server":"app/web/server.c", "weather":"app/services/weather.c",
            "time_setup":"app/services/time_sync.c + app/display/clock_ui.c", "sdk_platform":"ESP-IDF / libc (not ported)"}[group]


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("export",type=Path); args=parser.parse_args()
    source=args.export.read_text(encoding="utf-8")
    blocks=[]; names={}; symbols=[]
    for block in re.split(r"(?=// Audit label:)",source):
        match=re.match(r"// Audit label: ([^;]+); entry: ram:([0-9a-f]+); name: (\w+)",block)
        if not match: continue
        label,address,original=match.groups(); group=category(address,original)
        semantic=NAMES.get(address)
        if original.startswith("uri_"): semantic="http_"+original[4:]
        if semantic:
            renamed=semantic+"_at_"+address
        elif not original.startswith("FUN_"): renamed=original
        else: renamed="sdk_"+re.sub(r"[^a-z0-9_]","_",label)+"_at_"+address
        names[original]=renamed; blocks.append((group,address,block))
        symbols.append({"address":"0x"+address,"original":original,"logical_name":renamed,"category":group,
                        "native_module":native_module(group),"name_basis":"registered URI" if original.startswith("uri_") else ("inferred from body / callers" if semantic else "SDK symbol or reference relationship")})
    replacements=names.copy()
    for address,name in GLOBALS.items():
        replacements["DAT_ram_"+address]=name+"_at_"+address
        replacements["_DAT_ram_"+address]="overlapping_"+name+"_at_"+address
    pattern=re.compile(r"\b("+"|".join(re.escape(name) for name in sorted(replacements,key=len,reverse=True))+r")\b")
    output=ROOT/"reference"; output.mkdir(exist_ok=True)
    grouped={}; redacted=0; local_symbols=[]
    for group,address,block in blocks:
        local_names=LOCALS.get(address,{}).copy()
        if re.search(r"name: uri_",block): local_names["param_1"]="http_request"
        used={old:new for old,new in local_names.items() if re.search(r"\b"+re.escape(old)+r"\b",block)}
        if used:
            local_pattern=re.compile(r"\b("+"|".join(map(re.escape,used))+r")\b")
            block=local_pattern.sub(lambda m:used[m[0]],block)
            local_symbols.append({"function_address":"0x"+address,"names":used,"basis":"parameter position and observed use"})
        block=pattern.sub(lambda m:replacements[m[0]],block)
        # Never materialize a factory credential from RAM/rodata into new source.
        block,count=re.subn(r'"[0-9a-fA-F]{32}"','"[redacted factory credential]"',block); redacted+=count
        grouped.setdefault(group,[]).append("\n".join(line.rstrip() for line in block.splitlines()).rstrip()+"\n")
    for group,parts in grouped.items():
        header="/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.\n * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.\n * Executable reconstruction: "+native_module(group)+".\n */\n\n"
        (output/(group+".c")).write_text(header+"\n".join(parts),encoding="utf-8",newline="\n")
    (ROOT/"symbol-map.json").write_text(json.dumps({"source_export_sha256":hashlib.sha256(args.export.read_bytes()).hexdigest(),
        "source_dump_sha256":"5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4",
        "functions":symbols,"globals":[{"address":"0x"+address,"logical_name":name,"basis":"observed read/write and API use"} for address,name in GLOBALS.items()],
        "locals":local_symbols,"credential_literals_redacted":redacted},indent=2)+"\n",encoding="utf-8",newline="\n")
    print(f"Organized {len(blocks)} functions into {len(grouped)} modules; named {len(GLOBALS)} globals and {sum(len(s['names']) for s in local_symbols)} local/parameter aliases")


if __name__=="__main__": main()
