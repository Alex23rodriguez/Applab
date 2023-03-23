from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

current_data = Path(__file__) / "history" / "current"
tables_folder = Path(__file__) / "data_municipios"

if __name__ == "__main__":
    dtnow = datetime.now()
    now = dtnow.strftime("%Y%m%dT%H")
    onehourago = (dtnow - timedelta(hours=1)).strftime("%Y%m%dT%H")

    df: pd.DataFrame = pd.read_json(current_data)

    # filter out unimportant data
    # hloc: hora local
    df = df[(df["hloc"] == now) | (df["hloc"] == onehourago)]

    # filter out unused columns
    df = df[["ides", "idmun", "temp", "prec"]]

    # group by state, municipio and get average of the other fields
    df_prom = df.groupby(["ides", "idmun"]).mean()

    # reset index to go back to normal dataframe
    df_prom = df_prom.reset_index()

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
    ans.to_csv(new_file)

    # add symlink 'current'
    sym = tables_folder / "current"
    sym.unlink(missing_ok=True)  # remove previous to avoid FileExistsError
    sym.symlink_to(new_file)
