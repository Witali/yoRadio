from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
import json
from urllib.parse import urlsplit
page=Path('idf/esp32-cyd2usb-native/main/web_pages.cpp').read_text(encoding='utf-8').split('R"HTML(',1)[1].split(')HTML"',1)[0].encode()
responses={"capabilities":{"audio_output":"PDM GPIO26 · preview","websocket":False,"smartstart":True,"wifi_reconnect":True},"status":{"station":"Радио · тестовый пример","title":"Название композиции — Исполнитель","format":"AAC PCM 44.1 kHz / 16 bit / stereo","audio":True,"bitrate":128},"radio":{"current":7,"count":15,"smartstart":False},"settings":{"volume":123,"balance":0,"normalization":False,"normgain":12,"normtarget":-6,"normtime":6000}}
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  key=urlsplit(self.path).path.rsplit('/',1)[-1]
  data=page if not key else json.dumps(responses.get(key,{}),ensure_ascii=False).encode()
  self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8' if not key else 'application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def log_message(self,*args):pass
HTTPServer(('127.0.0.1',8819),Handler).serve_forever()
