import difflib,hashlib,importlib.util,json,pathlib,re,sys
sys.dont_write_bytecode=True
root=pathlib.Path.cwd();out=root/'.build/cyd-memory-transfer-audit-01';report=json.loads((out/'report.json').read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('extract',root/'tests/run-network-runtime-baseline.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
helper=root/'tests/run-network-runtime-baseline.py';target=out/'sources/tests/run-network-runtime-baseline.py';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(helper.read_bytes());report['source_sha256']['tests/run-network-runtime-baseline.py']=hashlib.sha256(helper.read_bytes()).hexdigest()
groups={
 'http':('components/esp_http_client/esp_http_client.c',['http_client_prepare_first_line','esp_http_client_request_send','esp_http_client_cleanup','esp_http_client_prepare','esp_http_client_fetch_headers','esp_http_client_read']),
 'tls-rx':('components/mbedtls/port/dynamic/esp_mbedtls_dynamic_impl.c',['esp_mbedtls_dynamic_set_rx_buf_static','esp_mbedtls_reset_add_rx_buffer','esp_mbedtls_add_rx_buffer','esp_mbedtls_free_rx_buffer','esp_mbedtls_free_buf']),
 'tls-memory':('components/mbedtls/port/esp_mem.c',['esp_mbedtls_mem_calloc','esp_mbedtls_mem_free'])}
comparisons={}
for group,(relative,names) in groups.items():
    a=(out/'sdk/v6.0.2'/relative).read_text();b=(out/'sdk/v6.1-9a97f6c54ec6'/relative).read_text();comparisons[group]={}
    complete=''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='CYD-SDK6.0.2',tofile='C3-SDK6.1'))
    (out/(group+'-whole.diff')).write_text(complete,encoding='utf-8')
    for name in names:
        def extract(text):
            match=re.search(r'^(?:static[ \t]+)?[A-Za-z_]\w*[ \t*]+'+re.escape(name)+r'\s*\([^;{}]*\)\s*\{',text,re.M)
            assert match,name
            return module.function(text[match.start():],name)[0]
        try:x=extract(a);y=extract(b)
        except (IndexError,ValueError) as error:
            comparisons[group][name]={'span_extraction_unavailable':True,'reason':'Conditional preprocessor braces require configuration-aware inspection; complete frozen source/diff retained.','error':type(error).__name__};continue
        comparisons[group][name]={'equal_normalized_source':x==y,'cyd_sha256':hashlib.sha256(x.encode()).hexdigest(),'c3_sha256':hashlib.sha256(y.encode()).hexdigest()}
        if x!=y:(out/(group+'-'+name+'.diff')).write_text(''.join(difflib.unified_diff(x.splitlines(True),y.splitlines(True),fromfile='CYD-SDK6.0.2',tofile='C3-SDK6.1')),encoding='utf-8')
maps={};symbols=['esp_mbedtls_mem_calloc','esp_mbedtls_mem_free','__wrap_esp_mbedtls_mem_calloc','__wrap_esp_mbedtls_mem_free','esp_mbedtls_dynamic_set_rx_buf_static','yoradio_http_client_release_request_buffer','yoradio_tls_rx_calloc']
for board,path in [('cyd',root/'idf/esp32-cyd2usb-native/build-c3-transfer/yoradio_cyd2usb_native.map'),('c3',root/'idf/esp32c3-oled-native/build-c3-transfer/yoradio_esp32c3_oled_native.map')]:
    text=path.read_text();selected={symbol:[line for line in text.splitlines() if re.match(r'^\s*0x[0-9a-fA-F]+\s+'+re.escape(symbol)+r'\s*$',line)] for symbol in symbols}
    maps[board]={'path':str(path),'map_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'actual_symbol_address_rows':selected}
    (out/(board+'-map-symbols.json')).write_text(json.dumps(maps[board],indent=2)+'\n',encoding='utf-8')
report['sdk_function_comparisons']=comparisons;report['completed_build_map_observations']=maps
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(comparisons,indent=2));print(json.dumps(maps,indent=2))
