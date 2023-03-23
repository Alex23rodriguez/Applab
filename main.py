from datetime import datetime
import json
import subprocess
import util
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
L = logging.getLogger(__name__)

url = "https://smn.conagua.gob.mx/webservices/index.php?method=3"
# use pathlib to ensure proper behavior in any OS
history_folder = Path(__file__).parent / "history"


if __name__ == "__main__":
    # download latest data
    tmp_file = history_folder / "tmp"
    L.info("downloading file")
    util.download_file(url, tmp_file)

    new_file = history_folder / datetime.now().strftime("%Y%m%dT%H.json")

    # API unreliable: sometimes returns JSON and sometimes a zipped file
    file_type = str(subprocess.check_output(["file", tmp_file]))
    if "gzip" in file_type:
        L.info("got gzip file")
        jsn = util.gzip_to_json(tmp_file)
        json.dump(jsn, open(new_file, "w"))
        tmp_file.unlink()  # remove tmp file
    elif "empty" in file_type:
        L.error("received empty file!")
        # TODO: handle empty file case
        tmp_file.unlink()
    else:
        L.info("got json file")
        tmp_file.rename(new_file)

    # add symlink 'latest'
    sym = history_folder / "latest.json"
    sym.unlink(missing_ok=True)  # remove previous to avoid FileExistsError
    sym.symlink_to(new_file)
