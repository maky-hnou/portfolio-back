"""Module containing utility functions for file handling and data manipulation.

This module provides functions to read text files, check for file existence,
read CSV files into pandas DataFrames, and create a DataFrame from text files
in a specified directory.

Functions:
    read_from_file: Read the contents of a text file.
    file_exists: Check if a file exists.
    read_from_csv: Read a CSV file into a pandas DataFrame.
    create_text_df: Create a DataFrame from text files in a specified directory.

Dependencies:
    - os: Standard library module for operating system dependent functionality.
    - pandas: Library for data manipulation and analysis.
"""

import os

import pandas as pd


def read_from_file(filename: str) -> str:
    """Read the contents of a text file.

    Args:
        filename (str): The path to the text file.

    Returns:
        str: The contents of the file as a string.
    """
    with open(filename) as input_file:
        return input_file.read()


def file_exists(filename: str) -> bool:
    """Check if a file exists.

    Args:
        filename (str): The path to the file.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.exists(filename)


def read_from_csv(filename: str) -> pd.DataFrame:
    """Read a CSV file into a pandas DataFrame.

    Args:
        filename (str): The path to the CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the CSV data.
    """
    return pd.read_csv(filename, low_memory=False)


def create_text_df(parent_path: str) -> pd.DataFrame:
    """Create a DataFrame from text files in a specified directory.

    Args:
        parent_path (str): The directory containing text files.

    Returns:
        pd.DataFrame: A DataFrame with columns ['id', 'topic', 'text']
        representing the text files in the directory.
    """
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
