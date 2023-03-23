from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
L = logging.getLogger(__name__)

current_data = Path(__file__).parent / "history" / "current"
tables_folder = Path(__file__).parent / "data_municipios"

if __name__ == "__main__":
    if not tables_folder.exists():
        tables_folder.mkdir()
    dtnow = datetime.now()
    now = dtnow.strftime("%Y%m%dT%H")
    onehourago = (dtnow - timedelta(hours=1)).strftime("%Y%m%dT%H")

    L.info("reading latest data from API")
    df = pd.read_csv(current_data)

    L.info("extracting values")
    # filter out unimportant data
    # hloc: hora local
    df = df[(df["hloc"] == now) | (df["hloc"] == onehourago)]

    # filter out unused columns
    df = df[["ides", "idmun", "temp", "prec"]]

    # group by state, municipio and get average of the other fields
    df_prom = df.groupby(["ides", "idmun"]).mean()

    L.info("merging with previous data")
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
    L.info(f"saving merged data as {new_file}")
    ans.to_csv(new_file, index=False)

    # add symlink 'current'
    sym = tables_folder / "current"
    sym.unlink(missing_ok=True)  # remove previous to avoid FileExistsError
    sym.symlink_to(new_file)
