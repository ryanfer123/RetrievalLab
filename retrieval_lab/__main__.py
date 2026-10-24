import argparse
import json
from pathlib import Path
import uuid
from . import __version__
from .engine import compare, validate_dataset
from .server import make_server, now

parser = argparse.ArgumentParser(description='Local retrieval evaluation workbench')
parser.add_argument('--port', type=int, default=8765)
parser.add_argument('--database', type=Path, default=Path('retrieval-lab.sqlite3'))
parser.add_argument('--evaluate', type=Path, help='Evaluate a dataset JSON without starting the server')
parser.add_argument('--output', type=Path, help='Write an evaluated experiment JSON to this path')
parser.add_argument('--k', type=int, default=5)
args = parser.parse_args()
if args.evaluate:
    try:
        dataset = validate_dataset(json.loads(args.evaluate.read_text(encoding='utf-8')))
        run = {'id': str(uuid.uuid4()), 'created': now(), 'version': __version__,
               'dataset': dataset, 'results': compare(dataset, args.k)}
        encoded = json.dumps(run, ensure_ascii=False, indent=2, allow_nan=False)
        if args.output:
            args.output.write_text(encoded + '\n', encoding='utf-8')
            print(f'Wrote {args.output}')
        else:
            print(encoded)
    except (OSError, ValueError) as error:
        parser.exit(2, f'{error}\n')
else:
    server = make_server(args.port, args.database)
    print(f'RetrievalLab: http://127.0.0.1:{server.server_port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
