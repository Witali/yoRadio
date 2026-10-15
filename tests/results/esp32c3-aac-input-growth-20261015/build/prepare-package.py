from pathlib import Path
import shutil
base=Path('.build/c3-aac-input-growth-20261015')
old=Path('.build/c3-confirm-tls-lab-20261015')
package=(old/'package.py').read_text().replace('build-confirm-tls-lab-20261015','build-aac-input4-lab-20261015')
package=package.replace('c3-confirm-tls-lab-20261015','c3-aac-input-growth-20261015')
package=package.replace('esp32c3-idf61-confirm-tls-lab','esp32c3-idf61-aac-input4-lab')
package=package.replace('idf61-ctls-20261015','idf61-aacin4-20261015')
package=package.replace("assert config['CONFIG_LOG_MAXIMUM_LEVEL']", "assert config['CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS'] == '4'\nassert config['CONFIG_LOG_MAXIMUM_LEVEL']",1)
package=package.replace('continuous_confirmation=True','continuous_confirmation=True, aac_input_extra_slots=4')
package=package.replace("+ PIPELINE_HEALTH_DIAGNOSTIC'", "+ PIPELINE_HEALTH_DIAGNOSTIC + AAC_INPUT_EXTRA_SLOTS=4'")
(base/'package.py').write_text(package)
(base/'trust').mkdir()
shutil.copyfile(old/'trust/ca.pem',base/'trust/ca.pem')
