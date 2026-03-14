import threading
import json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from io import BytesIO
import os
from log_utils import read_logs, append_entry
from state_utils import read_state, write_state


class APIHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/log':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            msgs = read_logs()
            self.wfile.write(json.dumps({'messages': msgs}, ensure_ascii=False).encode('utf-8'))
            return
        if parsed.path == '/api/state':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            state = read_state()
            self.wfile.write(json.dumps(state, ensure_ascii=False).encode('utf-8'))
            return
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/log':
            length = int(self.headers.get('Content-Length', '0'))
            body = self.rfile.read(length) if length else b''
            try:
                data = json.loads(body.decode('utf-8')) if body else {}
                # If a full entry provided, append; otherwise expect {message,type}
                if isinstance(data, dict) and 'message' in data:
                    entry = {
                        'id': int(__import__('time').time()),
                        'type': data.get('type', 'info'),
                        'message': data.get('message'),
                        'ts': data.get('ts') or __import__('datetime').datetime.utcnow().isoformat() + 'Z'
                    }
                    append_entry(entry)
                    self.send_response(201)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps(entry, ensure_ascii=False).encode('utf-8'))
                    return
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
                return
        if parsed.path == '/api/state':
            length = int(self.headers.get('Content-Length', '0'))
            body = self.rfile.read(length) if length else b''
            try:
                data = json.loads(body.decode('utf-8')) if body else {}
                if isinstance(data, dict):
                    write_state(data)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status':'ok','state': data}, ensure_ascii=False).encode('utf-8'))
                    return
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
                return
        return super().do_POST()


def start_server(port=8000, host='127.0.0.1'):
    cwd = os.path.dirname(__file__)
    os.chdir(cwd)
    server = ThreadingHTTPServer((host, port), APIHandler)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
