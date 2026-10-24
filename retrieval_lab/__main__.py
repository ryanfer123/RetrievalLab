import argparse
from pathlib import Path
from .server import make_server

parser = argparse.ArgumentParser(description='Local retrieval evaluation workbench')
parser.add_argument('--port', type=int, default=8765)
parser.add_argument('--database', type=Path, default=Path('retrieval-lab.sqlite3'))
args = parser.parse_args()
server = make_server(args.port, args.database)
print(f'RetrievalLab: http://127.0.0.1:{server.server_port}', flush=True)
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
