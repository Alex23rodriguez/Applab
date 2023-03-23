from subprocess import call
from pathlib import Path
import gzip
import json

import logging


def download_file(url: str, dest: str | Path, tries=10):
    # try multiple times because API is unreliable
    for _ in range(tries):
        return_code = call(["curl", url, "--silent", "--output", dest])
        if return_code == 0:
            return

    logging.error(f"Failed to download file! Tried {tries} times")
    # TODO: handle download failure


def gzip_to_json(filepath: str | Path):
    unzipped = gzip.open(filepath)
    return json.loads(unzipped.read())
