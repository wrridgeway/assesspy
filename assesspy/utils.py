import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype


def check_inputs(*args) -> None:
    out_msg = [""]

    for x in args:
        # *args passed into *args can created nested tuples - unnest
        if isinstance(x, tuple):
            args = x

    for x in args:
        check = pd.Series(x)

        if not is_numeric_dtype(check):
            out_msg.append("\nAll input values must be numeric.")
        if check.isnull().any():
            out_msg.append("\nAll input values cannot be null.")
        if len(check) <= 1:
            out_msg.append("\nAll input values must have length greater than 1.")
        if not all(np.isfinite(check) | check.isnull()):
            out_msg.append("\nAll input values cannot be infinite.")
        if any(check <= 0):
            out_msg.append("\nAll input values must be greater than 0.")

    lengths = [len(pd.Series(x)) for x in args]
    if len(set(lengths)) > 1:
        out_msg.append("\nAll input values must have the same length.")

    out_msg_set = set(out_msg)
    if len(out_msg_set) > 1:
        raise Exception("".join(map(str, out_msg_set)))
