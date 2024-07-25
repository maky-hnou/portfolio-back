import os

import pandas as pd


def read_from_file(filename: str) -> str:
    with open(filename) as input_file:
        return input_file.read()


def does_file_exist(filename: str) -> bool:
    return os.path.exists(filename)


def read_from_csv(filename: str) -> pd.DataFrame:
    return pd.read_csv(filename, low_memory=False)


def create_text_df(parent_path: str) -> pd.DataFrame:
    text_dict = {}
    for item in os.listdir(parent_path):
        if os.path.isfile(os.path.join(parent_path, item)):
            text_dict["topic"] = item.split(".")[0]
            text_dict["text"] = read_from_file(os.path.join(parent_path, item))
    return pd.DataFrame(text_dict)
