from datetime import datetime, timedelta
from pathlib import Path
import pandas

latest_data = Path(__file__) / "history" / "latest.json"


if __name__ == "__main__":
    dtnow = datetime.now()
    now = dtnow.strftime("%Y%m%dT%H")
    onehourago = (dtnow - timedelta(hours=1)).strftime("%Y%m%dT%H")

    df: pandas.DataFrame = pandas.read_json(latest_data)

    # filter out unimportant data
    df = df[(df["hloc"] == now) | (df["hloc"] == onehourago)]

    # filter out unused columns
    df = df[["ides", "idmun", "temp", "prec"]]

    # group by state, municipio and get average of the other fields
    df_prom = df.groupby(["ides", "idmun"]).mean()
