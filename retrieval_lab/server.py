"""Loopback HTTP API and SQLite storage for RetrievalLab."""
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
from urllib.parse import urlsplit
import uuid

from . import __version__
from .engine import canonical_json, compare, validate_dataset

WEB = Path(__file__).parent / 'web'
MAX_BODY = 2 * 1024 * 1024


def connect(path):
    connection = sqlite3.connect(path)
    connection.execute('CREATE TABLE IF NOT EXISTS datasets (id TEXT PRIMARY KEY, created TEXT, body TEXT)')
    connection.execute('CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, created TEXT, body TEXT)')
    return connection


def now():
    return datetime.now(timezone.utc).isoformat()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, database, **kwargs):
        self.database = database
        super().__init__(*args, directory=str(WEB), **kwargs)

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none'")
        super().end_headers()

    def send_json(self, value, status=200, filename=None):
        body = canonical_json(value).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        if filename:
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def valid_host(self):
        expected = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        if self.headers.get('Host') not in expected:
            self.send_json({'error': 'This app accepts localhost requests only.'}, 403)
            return False
        return True

    def do_GET(self):
        if not self.valid_host():
            return
        path = urlsplit(self.path).path
        if path == '/api/state':
            with connect(self.database) as db:
                datasets = [dict(json.loads(body), id=identifier, created=created) for identifier, created, body in db.execute('SELECT * FROM datasets ORDER BY created DESC')]
                runs = [dict(id=identifier, created=created, name=json.loads(body)['dataset']['name'], k=json.loads(body)['results']['k']) for identifier, created, body in db.execute('SELECT * FROM runs ORDER BY created DESC')]
            self.send_json({'datasets': datasets, 'runs': runs, 'version': __version__})
        elif path.startswith('/api/runs/'):
            identifier = path.removeprefix('/api/runs/')
            with connect(self.database) as db:
                row = db.execute('SELECT body FROM runs WHERE id=?', (identifier,)).fetchone()
            filename = f'retrieval-lab-{identifier}.json' if row and urlsplit(self.path).query == 'download=1' else None
            self.send_json(json.loads(row[0]) if row else {'error': 'Run not found.'}, 200 if row else 404, filename)
        elif path in ('/', '/app.js', '/motion.js', '/style.css', '/demo.json', '/favicon.svg') or (path.startswith('/vendor/') and Path(path).name in {p.name for p in (WEB/'vendor').iterdir()}):
            super().do_GET()
        else:
            self.send_json({'error': 'Not found.'}, 404)

    def do_POST(self):
        if not self.valid_host():
            return
        origin = self.headers.get('Origin')
        if origin and origin != f'http://{self.headers.get("Host")}':
            self.send_json({'error': 'Cross-origin writes are not allowed.'}, 403)
            return
        try:
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                raise ValueError('Send application/json.')
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= MAX_BODY:
                raise ValueError('Request must be between 1 byte and 2 MiB.')
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError('Request must be a JSON object.')
            path = urlsplit(self.path).path
            identifier, created = str(uuid.uuid4()), now()
            if path == '/api/datasets':
                dataset = validate_dataset(data)
                with connect(self.database) as db:
                    db.execute('INSERT INTO datasets VALUES (?,?,?)', (identifier, created, canonical_json(dataset)))
                self.send_json(dict(dataset, id=identifier, created=created), 201)
            elif path == '/api/runs':
                dataset_id = data.get('dataset_id')
                if not isinstance(dataset_id, str):
                    raise ValueError('dataset_id must be a string.')
                with connect(self.database) as db:
                    row = db.execute('SELECT body FROM datasets WHERE id=?', (dataset_id,)).fetchone()
                if not row:
                    self.send_json({'error': 'Dataset not found.'}, 404)
                    return
                dataset = json.loads(row[0])
                run = {'id': identifier, 'created': created, 'version': __version__,
                       'dataset': dataset, 'results': compare(dataset, data.get('k', 5))}
                with connect(self.database) as db:
                    db.execute('INSERT INTO runs VALUES (?,?,?)', (identifier, created, canonical_json(run)))
                self.send_json(run, 201)
            else:
                self.send_json({'error': 'Not found.'}, 404)
        except (ValueError, TypeError, RecursionError) as error:
            self.send_json({'error': str(error)}, 400)


def make_server(port=8765, database='retrieval-lab.sqlite3'):
    return ThreadingHTTPServer(('127.0.0.1', port), partial(Handler, database=str(database)))
