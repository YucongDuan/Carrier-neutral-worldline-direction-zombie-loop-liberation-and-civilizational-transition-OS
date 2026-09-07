from pathlib import Path
import argparse
from vitavector85.server import serve

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8781)
    parser.add_argument("--db", default=str(ROOT / "var" / "vitavector85.db"))
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    serve(ROOT, args.db, args.host, args.port, args.quiet)
