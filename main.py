from datetime import datetime
import json
import subprocess
import util
from pathlib import Path
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
L = logging.getLogger(__name__)

url = "https://smn.conagua.gob.mx/webservices/index.php?method=3"
# use pathlib to ensure proper behavior in any OS
history_folder = Path(__file__).parent / "history"


if __name__ == "__main__":
    # download current data
    tmp_file = history_folder / "tmp"
    L.info("downloading file")
    util.download_file(url, tmp_file)

    new_file = history_folder / datetime.now().strftime("%Y%m%dT%H.csv")

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
        exit()
    else:
        L.info("got json file")
        jsn = json.load(open(tmp_file))
        tmp_file.unlink()

    # save as csv data
    L.info("transforming json to csv file")
    pd.DataFrame(jsn).to_csv(new_file, index=False)

    # add symlink 'current'
    sym = history_folder / "current"
    sym.unlink(missing_ok=True)  # remove previous to avoid FileExistsError
    sym.symlink_to(new_file)
