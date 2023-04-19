import pandas as pd

import pathlib
INDEX_PATH = pathlib.Path(__file__).parent.resolve() / "index"

def search(service, identifier, dataset_name):
    df = pd.read_csv(INDEX_PATH / f"{service}.csv")
    res = df.loc[
        (df.identifier==identifier)
        & (df.dataset_name==dataset_name)]
    return res

