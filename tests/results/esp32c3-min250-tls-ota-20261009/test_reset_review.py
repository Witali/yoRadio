"""Synthetic reset boundaries cannot excuse panic resets or negative-upload resets."""
from summarize import ota_reset_review
timeline=[dict(action='ota:while-playing:upload',event='begin',at=10),
          dict(action='ota:while-playing:verify-boot',event='returned',at=20),
          dict(action='restore-saved-station:reboot-request',event='begin',at=30),
          dict(action='restore-saved-station:verify-boot',event='returned',at=40)]
normal=lambda at:dict(at=at,line='rst:0xc (RTC_SW_CPU_RST),boot:0xc (SPI_FAST_FLASH_BOOT)')
good=ota_reset_review(timeline,[normal(12),normal(32)])
assert good['result']=='PASS' and all(r['expected'] for r in good['rows'])
for row in (normal(2),normal(25),normal(41),dict(at=12,line='rst:0x8 (TG1WDT_SYS_RESET)'),
            dict(at=12,line='rst:0x8 (RTC_SW_CPU_RST),boot:0xc')):
    assert ota_reset_review(timeline,[row])['result']=='REVIEW_REQUIRED'
assert ota_reset_review(timeline[:1],[normal(12)])['result']=='REVIEW_REQUIRED'
print('PASS: explicit reset windows, unexpected resets and incomplete boot verification')
