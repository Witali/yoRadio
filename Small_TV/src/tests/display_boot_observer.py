"""Observe exact completed LCD pixels without HTTP, SDK role flags or UART."""
import hashlib
from pathlib import Path
import time


def observe_frame(qmp,folder,virtual_us,read_pixels,expected,host_timeout=90,guest_timeout=10):
    """Bound complete-frame equality in host/guest time, permitting startup clears.

    The caller supplies only a panel decoder and a read-only elapsed counter.
    An old screenshot is removed before every request so a failed capture cannot
    masquerade as a fresh frame. Readiness exactly at either deadline fails.
    """
    if len(expected)!=240*240*3:raise ValueError('Expected the complete 240x240 RGB reference')
    started,initial=time.monotonic(),virtual_us()
    frame=Path(folder)/'display.ppm'
    samples=[]
    while True:
        frame.unlink(missing_ok=True)
        qmp.execute('screendump',filename=str(frame))
        pixels=read_pixels(frame)
        if len(pixels)!=len(expected):raise ValueError('Short LCD raster')
        # The counter may wrap once, but a bounded cold start cannot span 2^32 us.
        sample=dict(host_seconds=time.monotonic()-started,
            guest_seconds=((virtual_us()-initial)&0xffffffff)/1e6,
            differing_rgb_bytes=sum(a!=b for a,b in zip(pixels,expected)),
            rgb_sha256=hashlib.sha256(pixels).hexdigest(),file_sha256=hashlib.sha256(frame.read_bytes()).hexdigest())
        samples.append(sample)
        expired=sample['host_seconds']>=host_timeout or sample['guest_seconds']>=guest_timeout
        equal=sample['differing_rgb_bytes']==0
        if expired or equal:
            return dict(passed=equal and not expired,method='exact_factory_setup_frame',
                expected_rgb_sha256=hashlib.sha256(expected).hexdigest(),samples=samples,
                host_timeout=host_timeout,guest_timeout=guest_timeout,**sample)
        time.sleep(.1)
