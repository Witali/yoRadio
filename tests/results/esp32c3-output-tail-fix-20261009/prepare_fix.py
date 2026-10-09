"""Prepare isolated output-boundary changes; do not mutate the live build inputs."""
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/codec_benchmark/run_output_dma_host.py').is_file())
DEST=ROOT/'candidate'
assert not DEST.exists()
files=['idf/esp32c3-oled-native/main/'+name for name in (
    'native_audio_output.c','native_audio_output.h','native_audio_output_dma.c',
    'native_audio_output_qemu.c','native_i2s_generator.c','native_i2s_generator.h',
    'pipeline_wait.h','pipeline_profile.h','audio_service.c')]
files += ['tests/native/output_dma/'+name for name in ('test.c','stubs.h','normalizer_chunks.cpp')]
files += ['yoRadio/src/audioI2S/'+name for name in ('AudioNormalizer.cpp','AudioNormalizer.h')]
files += ['tools/codec_benchmark/run_output_dma_host.py']
for relative in files:
    path=DEST/relative;path.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(REPO/relative,path)

def replace(relative,old,new,count=1):
    path=DEST/relative
    text=path.read_text()
    assert text.count(old)==count,(relative,old,text.count(old))
    path.write_text(text.replace(old,new))

main='idf/esp32c3-oled-native/main/'
replace(main+'native_audio_output.h',
    'esp_err_t native_audio_output_flush_pcm(void);\nvoid native_audio_output_discard_pcm(void);\n#endif',
    '#endif\n\n// Owned by the output task. Flush submits a zero-padded final DMA block; it\n'
    '// does not wait for the hardware to play it. Discard drops software PCM\n'
    '// and resampler history on Stop/new stream without draining old samples.\n'
    'esp_err_t native_audio_output_flush_pcm(void);\nvoid native_audio_output_discard_pcm(void);')
replace(main+'native_audio_output.c',
    '    if (input_sample_rate != s_input_sample_rate) {\n        s_input_sample_rate = input_sample_rate;\n        s_buffered_frames = 0;',
    '    if (input_sample_rate != s_input_sample_rate) {\n'
    '        ESP_RETURN_ON_ERROR(native_audio_output_flush_pcm(), TAG, "flush old PCM rate");\n'
    '        s_input_sample_rate = input_sample_rate;')
replace(main+'native_audio_output.c','void native_audio_output_idle(void) {',
    'void native_audio_output_discard_pcm(void) {\n'
    '    s_buffered_frames = 0;\n    reset_resampler();\n}\n\n'
    'esp_err_t native_audio_output_flush_pcm(void) {\n'
    '    if (!s_buffered_frames) return ESP_OK;\n'
    '    // The output task is the sole owner. Consume this tail once, even on\n'
    '    // a partial/failed driver write, so a later stream cannot replay it.\n'
    '    memset(s_frame_buffer + s_buffered_frames * 2U, 0,\n'
    '           (PDM_DMA_FRAMES - s_buffered_frames) * 2U * sizeof(*s_frame_buffer));\n'
    '    s_buffered_frames = 0;\n'
    '    esp_err_t result = pdm_write_block(s_frame_buffer, PDM_DMA_FRAMES);\n'
    '    if (result != ESP_OK) reset_resampler();\n'
    '    return result;\n}\n\nvoid native_audio_output_idle(void) {')
replace(main+'native_audio_output_qemu.c','void native_audio_output_idle(void) {',
    'esp_err_t native_audio_output_flush_pcm(void) {\n'
    '    // The virtual sink receives each generated frame synchronously.\n'
    '    return ESP_OK;\n}\n\n'
    'void native_audio_output_discard_pcm(void) {\n'
    '    reset_resampler();\n}\n\nvoid native_audio_output_idle(void) {')
replace(main+'audio_service.c',
    '#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM\n    uint32_t generation = atomic_load(&s_generation);\n#endif\n    while (true) {\n#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM',
    '    uint32_t generation = atomic_load(&s_generation);\n    while (true) {')
replace(main+'audio_service.c',
    '        }\n#endif\n#ifdef CONFIG_YORADIO_DEEP_SLEEP_CLOCK\n        if (atomic_exchange(&s_suspend_output, false))',
    '        }\n#ifdef CONFIG_YORADIO_DEEP_SLEEP_CLOCK\n        if (atomic_exchange(&s_suspend_output, false))')
replace(main+'audio_service.c',
    '#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM\n        current_generation = atomic_load(&s_generation);',
    '        current_generation = atomic_load(&s_generation);')
replace(main+'audio_service.c',
    '        }\n#endif\n        if (packet->generation != atomic_load(&s_generation))',
    '        }\n        if (packet->generation != atomic_load(&s_generation))')
replace(main+'audio_service.c',
    '        if (packet->end_of_stream) {\n#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM\n'
    '            esp_err_t flush_result = native_audio_output_flush_pcm();\n'
    '            if (flush_result != ESP_OK) ESP_LOGW(TAG, "PCM tail flush failed: %s", esp_err_to_name(flush_result));\n#endif',
    '        if (packet->end_of_stream) {\n'
    '            esp_err_t flush_result = native_audio_output_flush_pcm();\n'
    '            if (flush_result != ESP_OK) ESP_LOGW(TAG, "PCM tail flush failed: %s", esp_err_to_name(flush_result));')
replace('tests/native/output_dma/test.c',
    '        if(s_buffered_frames){\n'
    '            memset(s_frame_buffer+s_buffered_frames*2,0,(512-s_buffered_frames)*4);\n'
    '            assert(pdm_write_block(s_frame_buffer,512)==0);\n'
    '        }\n        s_buffered_frames=0;',
    '        assert(native_audio_output_flush_pcm()==0);')
replace('tests/native/output_dma/test.c','        s_input_sample_rate=0;assert(native_audio_output_configure(rates[r])==0);',
    '        native_audio_output_discard_pcm();assert(native_audio_output_configure(rates[r])==0);')
print('Prepared isolated candidate at',DEST)
