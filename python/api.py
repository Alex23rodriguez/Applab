from datetime import datetime
import json
import subprocess
import util
from pathlib import Path
import logging
import pandas as pd

logging.basicConfig(
    format="%(asctime)s:%(levelname)8s:%(module)6s: %(message)s",
    datefmt="%y%m%dT%H%M",
    level=logging.INFO,
    filename=Path(__file__).parent.parent / "logs" / "main.log",
)

url = "https://smn.conagua.gob.mx/webservices/index.php?method=3"
# use pathlib to ensure proper behavior in any OS
history_folder = Path(__file__).parent.parent / "history"


if __name__ == "__main__":
    logging.info("--- running api.py ---")
    if not history_folder.exists():
        history_folder.mkdir()
    # download current data
    tmp_file = history_folder / "tmp"
    logging.info("downloading file")
    util.download_file(url, tmp_file)

    new_file = history_folder / datetime.now().strftime("%Y%m%dT%H.csv")

    # API unreliable: sometimes returns JSON and sometimes a zipped file
    file_type = str(subprocess.check_output(["file", tmp_file]))
    if "gzip" in file_type:
        logging.info("got gzip file")
        logging.info("extracting to json...")
        jsn = util.gzip_to_json(tmp_file)
        json.dump(jsn, open(new_file, "w"))
        tmp_file.unlink()  # remove tmp file
    elif "empty" in file_type:
        logging.error("received empty file!")
        # TODO: handle empty file case
        tmp_file.unlink()
        exit(1)  # return 1 so next script won't be run
    else:
        logging.info("got json file")
        jsn = json.load(open(tmp_file))
        tmp_file.unlink()

    # save as csv data
    logging.info("transforming json to csv file")
    pd.DataFrame(jsn).to_csv(new_file, index=False)

    # add symlink 'current'
    util.symlink_to(history_folder / "current", new_file)
    logging.info("done!")
