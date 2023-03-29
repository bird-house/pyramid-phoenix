import pandas as pd

import pathlib
INDEX_PATH = pathlib.Path(__file__).parent.resolve() / "index"

def search(service, identifier, **kwargs):
    df = pd.read_csv(INDEX_PATH / f"{service}.csv")
    res = df.loc[df.identifier==identifier]
    return res

