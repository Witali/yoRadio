from pathlib import Path
root=Path(__file__).resolve().parent
source=Path('.build/c3-quiet-tls-records-20261010/review.py').read_text()
source=source.replace('from quiet_tls_records import check_record_window,check_format,check_response',
    'from quiet_tls_records import check_record_window,check_format,check_response,check_renegotiation')
source=source.replace("    replay(key+':output',lambda:check_output(measured))", "    renegotiation=replay(key+':renegotiation',lambda:check_renegotiation(observation,first,observation['captured_at'],r['renegotiate_seconds']))\n    replay(key+':output',lambda:check_output(measured))")
source=source.replace('format=fmt,records=records,','format=fmt,records=records,renegotiation=renegotiation,')
source=source.replace('Replay quiet TLS-record gates','Replay quiet TLS renegotiation gates')
source=source.replace("P=ROOT/'physical'", "phase=sys.argv[1] if len(sys.argv)>1 else 'physical'\nassert phase in ('physical','physical-comparison')\nP=ROOT/phase\nreview_name='review.json' if phase=='physical' else 'comparison-review.json'")
source=source.replace("ROOT/'review.json'",'ROOT/review_name')
(root/'review.py').write_text(source)
print('Prepared independent saved-evidence replay')
