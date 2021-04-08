import io
import json
from pathlib import Path

import pandas as pd

with open(Path(__file__).parent / "data.json") as file:
    data_in = json.load(file)

data = {
    k: pd.read_json(io.StringIO(json.dumps(v)), typ="series", orient="split")
    for k, v in data_in.items()
}
