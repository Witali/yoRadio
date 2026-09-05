const fs = require('node:fs'), path = require('node:path'), zlib = require('node:zlib');
const file = path.join(__dirname, '../yoRadio/data/www/script.js.gz');
let source = zlib.gunzipSync(fs.readFileSync(file)).toString('utf8');
source = source.replace('getId("ssid"+i).value=line[0].trim();',
  'if(!getId("ssid"+i)) continue;\n      getId("ssid"+i).value=line[0];');
source = source.replace("getId(\"pass\"+i).attr('data-pass', line[1].trim());",
  "getId(\"pass\"+i).attr('data-pass', line[1].replace(/\\r$/, ''));");
if(!source.includes('function reportUploadFailure')) {
  source = source.replace('function doPlUpload(finput) {',
    "function reportUploadFailure(xhr){ alert('Upload failed: '+(xhr.responseText || 'network error')); }\nfunction doPlUpload(finput) {");
  source = source.replace('  xhr.send(formData);\n  finput.value',
    "  xhr.onload = () => { if(xhr.status < 200 || xhr.status >= 300) reportUploadFailure(xhr); };\n  xhr.onerror = () => reportUploadFailure(xhr);\n  xhr.send(formData);\n  finput.value");
  const pattern = /    xhr.send\(formData\);\n    fileuploadinput.value = '';\n([\s\S]*?10000\);)/;
  if(!pattern.test(source)) throw Error('Missing Wi-Fi upload handler');
  source = source.replace(pattern, (_, feedback) =>
    "    xhr.onload = () => {\n      if(xhr.status < 200 || xhr.status >= 300){ reportUploadFailure(xhr); return; }\n" +
    feedback + "\n    };\n    xhr.onerror = () => reportUploadFailure(xhr);\n    xhr.send(formData);\n    fileuploadinput.value = '';");
}
source = source.replaceAll('getId("status").innerHTML =', 'getId("uploadstatus").innerHTML =');
if(!source.includes("nativeFirmwareOnly === true")) {
  source = source.replace("getId('content').innerHTML = updform;",
    "getId('content').innerHTML = updform;\n" +
    "        if(typeof nativeFirmwareOnly !== 'undefined' && nativeFirmwareOnly === true){\n" +
    "          getId('uploadtype2').closest('label').classList.add('hidden');\n" +
    "          getId('uploadstatus').innerText='Choose ESP8266 native app.bin. For WebUI files use Board.';\n" +
    "        }");
  source = source.replace('system.appendChild(row);',
    "system.appendChild(row);\n      document.querySelector('[data-command=\"format\"]')?.classList.add('hidden');");
}
fs.writeFileSync(file, zlib.gzipSync(source, {level:9}));
