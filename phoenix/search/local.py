import pandas as pd

import pathlib
INDEX_PATH = pathlib.Path(__file__).parent.resolve() / "index"

def search(service, identifier, **kwargs):
    df = pd.from_csv(INDEX_PATH / f"{service}.csv")
    df.loc[identifier==identifier]
    return df

