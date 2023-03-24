from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import logging
from util import symlink_to

logging.basicConfig(
    format="%(asctime)s:%(levelname)8s:%(module)6s: %(message)s",
    datefmt="%y%m%dT%H%M",
    level=logging.INFO,
    filename=Path(__file__).parent / "logs" / "main.log",
)

current_data = Path(__file__).parent / "history" / "current"
tables_folder = Path(__file__).parent / "data_municipios"

if __name__ == "__main__":
    if not tables_folder.exists():
        tables_folder.mkdir()

    dtnow = datetime.now()
    now = dtnow.strftime("%Y%m%dT%H")
    onehourago = (dtnow - timedelta(hours=1)).strftime("%Y%m%dT%H")

    logging.info("reading latest data from API")
    df = pd.read_csv(current_data)

    logging.info("extracting values")
    # filter out unimportant data
    # hloc: hora local
    df = df[(df["hloc"] == now) | (df["hloc"] == onehourago)]

    # filter out unused columns
    df = df[["ides", "idmun", "temp", "prec"]]

    # group by state, municipio and get average of the other fields
    df_prom = df.groupby(["ides", "idmun"]).mean()

    logging.info("merging with previous data")
    # merge with other data
    data = pd.read_csv(tables_folder / "data1.csv")

    ans = pd.merge(
        data,
        df_prom,
        how="inner",
        left_on=["Cve_Ent", "Cve_Mun"],
        right_on=["ides", "idmun"],
    )

    # save this data
    new_file = f"{tables_folder / now}.csv"
    logging.info(f"saving merged data as {new_file}")
    ans.to_csv(new_file, index=False)

    # add symlink 'current'
    symlink_to(tables_folder / "current", new_file)
    logging.info("done!")
