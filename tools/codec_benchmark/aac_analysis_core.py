"""Verified native argument roles for the extended AAC analysis, not an ABI patch."""

def extend(parameters):
    def roles(names, *entries):
        for name in names.split():
            parameters.setdefault(name, {}).update({str(i): dict(type=t, name=n) for i,t,n in entries})
    # Propagate the full core view into the previously typed SBR callers, too.
    for fields in parameters.values():
        for field in fields.values():
            if field['type'] == 'aac_core_abi_t *': field['type'] = 'aac_analysis_core_t *'
    roles('PVMP4AudioDecodeFrame PVMP4AudioDecoderInitLibrary PVMP4AudioDecoderDeInit',
          (0,'aac_analysis_external_t *','external'), (1,'aac_analysis_core_t *','core'))
    roles('raw_stream_parameter_setup', (2,'aac_analysis_core_t *','core'))
    roles('get_adif_header get_adts_header get_prog_config reset_adts_sync_para', (0,'aac_analysis_core_t *','core'))
    roles('get_prog_config', (1,'aac_analysis_program_t *','program'))
    roles('get_adif_header', (1,'aac_analysis_adif_t *','adif'))
    roles('set_mc_info', (0,'aac_analysis_mc_t *','mc'), (4,'aac_analysis_window_t **','window_map'))
    roles('infoinit', (1,'aac_analysis_window_t **','window_map'))
    roles('calc_gsfb_table', (0,'aac_analysis_window_t *','window'))
    roles('byte_align getfill decode_huff_scl', (0,'aac_analysis_bits_t *','bits'))
    roles(' '.join('decode_huff_cw_tab'+str(i) for i in range(1,12)),
          (0,'aac_analysis_bits_t *','bits'))
    roles('get_dse get_ele_list getgroup get_pulse_data getmask huffcb hufffac get_tns lt_decode get_sbr_bitstream',
          (1,'aac_analysis_bits_t *','bits'))
    roles('find_adts_syncword', (1,'aac_analysis_bits_t *','bits'))
    roles('get_ele_list', (0,'aac_analysis_elements_t *','elements'))
    roles('get_pulse_data', (0,'aac_analysis_pulse_t *','pulse'))
    roles('getmask hufffac', (0,'aac_analysis_window_t *','window'))
    roles('huffcb', (0,'aac_analysis_section_t *','sections'))
    roles('hufffac', (4,'aac_analysis_section_t *','sections'))
    roles('huffspec_fxp', (0,'aac_analysis_window_t *','window'), (1,'aac_analysis_bits_t *','bits'),
          (3,'aac_analysis_section_t *','sections'), (8,'aac_analysis_window_t *','pulse_window'),
          (9,'aac_analysis_pulse_t *','pulse'))
    roles('unpack_idx unpack_idx_sgn unpack_idx_esc', (2,'aac_analysis_codebook_t *','book'))
    roles('unpack_idx_sgn unpack_idx_esc', (3,'aac_analysis_bits_t *','bits'))
    roles('pulse_nc', (1,'aac_analysis_pulse_t *','pulse'), (2,'aac_analysis_window_t *','window'))
    roles('pns_left apply_ms_synt', (0,'aac_analysis_window_t *','window'))
    roles('pns_intensity_right', (1,'aac_analysis_window_t *','window'))
    roles('deinterleave', (2,'aac_analysis_window_t *','window'))
    roles('pv_div pv_sqrt', (2,'aac_analysis_fraction_t *','result'))
    roles('pv_sqrt', (3,'aac_analysis_sqrt_cache_t *','cache'))
    roles('calc_auto_corr calc_auto_corr_LC', (0,'aac_analysis_autocorrelation_t *','correlation'))
    roles('calc_sbr_envelope', (19,'aac_analysis_envelope_workspace_t *','scratch'),
          (20,'aac_analysis_patch_t *','patch'), (21,'aac_analysis_sqrt_cache_t *','sqrt_cache'))
    roles('sbr_create_limiter_bands', (3,'aac_analysis_patch_t *','patch'))
    roles('huffdecode', (1,'aac_analysis_bits_t *','bits'), (2,'aac_analysis_core_t *','core'),
          (3,'aac_analysis_core_channel_t **','channels'))
    roles('getics', (0,'aac_analysis_bits_t *','bits'), (2,'aac_analysis_core_t *','core'),
          (3,'aac_analysis_core_channel_t *','channel'), (7,'aac_analysis_tns_t *','tns'),
          (8,'aac_analysis_window_t **','window_map'), (9,'aac_analysis_pulse_t *','pulse'),
          (10,'aac_analysis_section_t *','sections'))
    roles('get_ics_info', (0,'aac_analysis_bits_t *','bits'), (6,'aac_analysis_window_t **','window_map'),
          (7,'aac_analysis_ltp_t *','left_ltp'), (8,'aac_analysis_ltp_t *','right_ltp'))
    roles('lt_decode', (3,'aac_analysis_ltp_t *','ltp'))
    roles('get_tns', (5,'aac_analysis_tns_t *','tns'), (3,'aac_analysis_window_t *','window'),
          (4,'aac_analysis_mc_t *','mc'))
    roles('apply_tns', (3,'aac_analysis_tns_t *','tns'), (2,'aac_analysis_window_t *','window'))
    roles('get_sbr_bitstream', (0,'aac_analysis_sbr_stream_t *','stream'))
    roles('sbr_read_data', (2,'aac_analysis_sbr_stream_t *','stream'))
    roles('sbr_applied', (1,'aac_analysis_sbr_stream_t *','stream'))
    roles('buf_getbits buf_get_1bit GetNrBitsAvailable sbr_crc_check', (0,'aac_analysis_sbr_bits_t *','bits'))
    roles('check_crc', (0,'aac_analysis_crc_t *','crc'))
    roles('sbr_get_sce sbr_get_header_data sbr_get_envelope sbr_get_noise_floor_data '
          'sbr_get_dir_control_data sbr_get_additional_data ps_read_data',
          (1,'aac_analysis_sbr_bits_t *','bits'))
    roles('sbr_get_cpe', (2,'aac_analysis_sbr_bits_t *','bits'))
    roles('sbr_extract_extended_data', (0,'aac_analysis_sbr_bits_t *','bits'))
    roles('esp_aac_dec_open', (0,'aac_analysis_config_t *','config'),
          (2,'aac_analysis_decoder_t **','decoder'))
    roles('esp_aac_dec_close esp_aac_dec_reset esp_aac_dec_decode',
          (0,'aac_analysis_decoder_t *','decoder'))
    roles('esp_aac_dec_decode', (1,'aac_analysis_raw_t *','input'),
          (2,'aac_analysis_output_t *','output'), (3,'aac_analysis_info_t *','info'))
