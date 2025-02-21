import logging
import os
from pathlib import Path
from typing import List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


def load_excel_dataframe(excel_path: Path) -> Tuple[pd.DataFrame, List[str]]:
    """
    Loads an Excel file into a DataFrame and returns the DataFrame along with its column names.

    Args:
        excel_path (Path): The path to the Excel file.

    Returns:
        Tuple[pd.DataFrame, List[str]]: The DataFrame and a list of its column names.

    Raises:
        FileNotFoundError: If the Excel file does not exist.
    """
    excel_file = Path(excel_path)
    if not excel_file.exists():
        raise FileNotFoundError(f"File not found: {excel_file}")
    df = pd.read_excel(excel_file)
    return df, list(df.columns)


def generate_formatted_names(
    df: pd.DataFrame, columns: List[str], format_string: str
) -> List[str]:
    """
    Generates a list of formatted file names based on the DataFrame values and a format string.

    The function replaces each occurrence of a column name in the format string with its corresponding
    value from each row of the DataFrame. The file extension from the format string is discarded.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        columns (List[str]): List of column names to use as placeholders.
        format_string (str): The format string containing placeholders for columns.

    Returns:
        List[str]: A list of formatted file names.
    """
    # Remove the extension from the format string (not used in the final name)
    base_string, _ = os.path.splitext(format_string)
    formatted_names = []
    for _, row in df.iterrows():
        temp_name = base_string
        for col in columns:
            value = row[col]
            # Convert float to int if it is an integer value
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            value_str = str(value).strip()
            temp_name = temp_name.replace(col, value_str)
        formatted_names.append(temp_name)
    return formatted_names
