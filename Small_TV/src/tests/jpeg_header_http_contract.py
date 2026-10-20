"""Keep JPEG header upload acceptance separate from the decoder-only oracle."""

NAMES = {'gray-dri-length-1', 'gray-sos-length-1', 'gray-sos-ahal-1',
         'gray-unknown-component-0', 'duplicate-frame-1-1-3', 'zero-quantizer-63'}


def validate_photo_headers(report):
    """Require actual finalize rejection, absent files and a valid custom-ID upload."""
    cases = report['invalid_headers']
    if (set(cases) != NAMES or report['checks'].get('header_fields_rejected') is not True or
            report['checks'].get('custom_component_ids_published') is not True or
            any(row['finish_status'] != 400 or row['metadata'] != {'exists': False, 'size': 0}
                for row in cases.values())):
        raise ValueError('JPEG header HTTP evidence is missing or accepted a malformed file')
