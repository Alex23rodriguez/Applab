from subprocess import call
from pathlib import Path
import gzip
import json


def download_file(url: str, dest: str | Path, tries=10):
    for _ in range(tries):
        return_code = call(["curl", url, "--output", dest])
        if return_code == 0:
            break
    else:
        # TODO log error downloading file
        pass


def gunzip_json(filepath: str | Path, output: str | Path):
    unzipped = gzip.open(filepath)
    return json.loads(unzipped.read())
