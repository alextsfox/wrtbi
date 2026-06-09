"""
Compute a composite fingerprint for each file in a directory:
  - filename
  - file size
  - mtime
  - first and last 1 MB of content

Writes one line per file: <hex_hash>  <filepath>
"""
import argparse
import hashlib
import os
from pathlib import Path


SAMPLE_BYTES = 1 * 1024 * 1024  # 1 MB


def file_fingerprint(path: Path) -> str:
    stat = path.stat()
    h = hashlib.sha256()
    h.update(path.name.encode())
    h.update(str(stat.st_size).encode())
    h.update(str(stat.st_mtime).encode())
    with open(path, 'rb') as f:
        h.update(f.read(SAMPLE_BYTES))
        if stat.st_size > SAMPLE_BYTES:
            f.seek(-SAMPLE_BYTES, os.SEEK_END)
            h.update(f.read(SAMPLE_BYTES))
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description='Compute composite file fingerprints.')
    parser.add_argument('--input_files', nargs='+', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    files = sorted(Path(f) for f in args.input_files)

    with open(args.output, 'w') as out:
        for f in files:
            out.write(f"{file_fingerprint(f)}  {f}\n")


if __name__ == '__main__':
    main()
