import subprocess
from pathlib import Path
import gzip
import json

import logging


def download_file(url: str, dest: Path, tries=10):
    # try multiple times because API is unreliable
    for i in range(tries):
        logging.debug(f"downloading file using curl, attempt {i}")
        returncode = subprocess.run(
            ["curl", url, "--silent", "--output", dest]
        ).returncode

        # check that curl ran successfully AND actually received data
        if returncode == 0 and dest.stat().st_size > 0:
            return

    logging.error(f"Failed to download file! Tried {tries} times")
    # TODO: handle download failure


def gzip_to_json(filepath: str | Path):
    unzipped = gzip.open(filepath)
    return json.loads(unzipped.read())


def symlink_to(symlink: Path, target_file: Path | str):
    # remove previous to avoid FileExistsError
    symlink.unlink(missing_ok=True)
    symlink.symlink_to(target_file)
