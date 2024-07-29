import os

import pandas as pd


def read_from_file(filename: str) -> str:
    with open(filename) as input_file:
        return input_file.read()


def file_exists(filename: str) -> bool:
    return os.path.exists(filename)


def read_from_csv(filename: str) -> pd.DataFrame:
    return pd.read_csv(filename, low_memory=False)


def create_text_df(parent_path: str) -> pd.DataFrame:
    data = []
    i = 0
    for item in os.listdir(parent_path):
        text_dict = {}
        if os.path.isfile(os.path.join(parent_path, item)):
            text_dict["id"] = i
            text_dict["topic"] = item.split(".")[0]  # type: ignore
            text_dict["text"] = read_from_file(os.path.join(parent_path, item))  # type: ignore
            i += 1
            data.append(text_dict)
    return pd.DataFrame(data)
