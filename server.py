"""Local dashboard server. Run: python3 server.py"""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json, csv, io, argparse, webbrowser
from urllib.parse import urlparse, parse_qs
from model import Config, simulate
import storage

class Handler(BaseHTTPRequestHandler):
    def send(self,payload,status=200,kind='application/json'):
        body=payload.encode() if isinstance(payload,str) else json.dumps(payload,allow_nan=False).encode()
        self.send_response(status); self.send_header('Content-Type',kind+'; charset=utf-8')
        self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        route=urlparse(self.path)
        try:
            if route.path=='/': self.send(Path(__file__).with_name('dashboard.html').read_text(),kind='text/html')
            elif route.path=='/api/history': self.send(storage.history())
            elif route.path=='/api/result': self.send(storage.load(int(parse_qs(route.query)['id'][0])))
            elif route.path=='/api/export':
                query=parse_qs(route.query); result=storage.load(int(query['id'][0]))
                table=query.get('table',['trials'])[0]
                if table not in ('trials','daily','sample_daily'): raise ValueError('Invalid export table')
                rows=result[table]; out=io.StringIO(); writer=csv.DictWriter(out,fieldnames=list(rows[0]))
                writer.writeheader(); writer.writerows(rows)
                self.send(out.getvalue(),kind='text/csv')
            else: self.send({'error':'Not found'},404)
        except (ValueError,KeyError) as exc: self.send({'error':str(exc)},400)
    def do_POST(self):
        if self.path!='/api/simulate': return self.send({'error':'Not found'},404)
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<20000: raise ValueError('Invalid request size')
            data=json.loads(self.rfile.read(length)); c=Config(**data['config'])
            result=simulate(c); sid=storage.save(str(data.get('name','Scenario'))[:80],result)
            result['id']=sid; self.send(result)
        except (ValueError,TypeError,KeyError) as exc: self.send({'error':str(exc)},400)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--port',type=int,default=8765); parser.add_argument('--no-browser',action='store_true'); args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'Readiness Lab: http://127.0.0.1:{args.port} — Ctrl+C to stop',flush=True)
    if not args.no_browser: webbrowser.open(f'http://127.0.0.1:{args.port}')
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
if __name__=='__main__': main()
