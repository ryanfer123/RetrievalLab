import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest

from retrieval_lab.server import make_server
from retrieval_lab.engine import validate_dataset

DEMO = json.loads((Path(__file__).parents[1]/'retrieval_lab/web/demo.json').read_text())


class APITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name)/'test.sqlite3'
        self.server = make_server(0,self.db)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def request(self, path, data=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1',self.server.server_port)
        connection.request('POST' if data is not None else 'GET',path,
                           json.dumps(data) if data is not None else None,
                           headers or {'Content-Type':'application/json'})
        response=connection.getresponse()
        body=response.read()
        connection.close()
        return response.status, body

    def test_import_run_export_and_reload(self):
        status, body = self.request('/api/datasets',DEMO)
        self.assertEqual(status,201)
        dataset=json.loads(body)
        status, body=self.request('/api/runs',{'dataset_id':dataset['id'],'k':3})
        self.assertEqual(status,201)
        run=json.loads(body)
        self.assertEqual(run['dataset'],validate_dataset(DEMO))
        status, saved=self.request('/api/runs/'+run['id'])
        self.assertEqual(json.loads(saved),run)
        status,state=self.request('/api/state')
        self.assertEqual(len(json.loads(state)['runs']),1)
        # A second server instance reads the same persisted experiment.
        other=make_server(0,self.db)
        try:
            thread=threading.Thread(target=other.serve_forever,daemon=True);thread.start()
            connection=http.client.HTTPConnection('127.0.0.1',other.server_port)
            connection.request('GET','/api/state')
            self.assertEqual(len(json.loads(connection.getresponse().read())['runs']),1)
            connection.close()
        finally:
            other.shutdown();other.server_close();thread.join()

    def test_invalid_import_is_not_saved(self):
        self.assertEqual(self.request('/api/datasets',{'name':'bad'})[0],400)
        self.assertEqual(json.loads(self.request('/api/state')[1])['datasets'],[])

    def test_json_array_is_rejected(self):
        self.assertEqual(self.request('/api/datasets',[])[0],400)

    def test_missing_run_and_dataset(self):
        self.assertEqual(self.request('/api/runs/missing')[0],404)
        self.assertEqual(self.request('/api/runs',{'dataset_id':'missing'})[0],404)

    def test_foreign_origin_and_host_are_blocked(self):
        self.assertEqual(self.request('/api/datasets',DEMO,{'Content-Type':'application/json','Origin':'https://example.com'})[0],403)
        self.assertEqual(self.request('/api/state',headers={'Host':'example.com'})[0],403)

    def test_non_json_form_is_rejected(self):
        self.assertEqual(self.request('/api/datasets',DEMO,{'Content-Type':'text/plain'})[0],400)

    def test_source_and_database_are_not_served(self):
        for path in ('/server.py','/../server.py','/test.sqlite3'):
            self.assertEqual(self.request(path)[0],404)

    def test_direct_export_has_download_header(self):
        dataset=json.loads(self.request('/api/datasets',DEMO)[1])
        run=json.loads(self.request('/api/runs',{'dataset_id':dataset['id'],'k':3})[1])
        connection=http.client.HTTPConnection('127.0.0.1',self.server.server_port)
        connection.request('GET','/api/runs/'+run['id']+'?download=1')
        response=connection.getresponse()
        self.assertIn('attachment;',response.getheader('Content-Disposition'))
        self.assertEqual(json.loads(response.read()),run)
        connection.close()

    def test_frontend_assets_are_served(self):
        for path in ('/','/app.js','/motion.js','/style.css','/vendor/manrope-latin.woff2','/vendor/gsap.min.js'):
            self.assertEqual(self.request(path)[0],200)
