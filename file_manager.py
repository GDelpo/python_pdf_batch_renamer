import logging
import os
from pathlib import Path
from typing import List, Tuple

from natsort import natsorted

logger = logging.getLogger(__name__)


def get_file_paths_and_extension(
    directory_path: str, allowed_extensions: List[str] = [".pdf"]
) -> Tuple[List[str], str]:
    """
    Retrieves the absolute paths of all files in the given directory and returns them along with the common file extension.

    Validations:
      - The directory must exist and be a directory.
      - There must be at least one file in the directory.
      - All files must share the same extension.
      - The common extension must be one of the allowed extensions.

    Args:
        directory_path (str): The path to the directory containing the files.
        allowed_extensions (List[str], optional): List of allowed file extensions (default: ['.pdf']).

    Returns:
        Tuple[List[str], str]: A tuple with a list of file paths and the common file extension.

    Raises:
        FileNotFoundError: If the directory does not exist.
        NotADirectoryError: If the provided path is not a directory.
        ValueError: If no files are found, if there is a mix of extensions, or if the extension is not allowed.
    """
    directory = Path(directory_path)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    files = [file for file in directory.iterdir() if file.is_file()]
    if not files:
        raise ValueError("No files found in the directory.")

    extensions = {file.suffix.lower() for file in files}
    if len(extensions) != 1:
        raise ValueError("Error: Mixed file extensions in the directory.")

    ext = extensions.pop()
    allowed_extensions_lower = [ext.lower() for ext in allowed_extensions]
    if ext not in allowed_extensions_lower:
        raise ValueError(
            f"Extension not allowed: {ext}. Allowed: {allowed_extensions}")

    file_paths = [str(file.resolve()) for file in files]
    file_paths = natsorted(file_paths)

    return file_paths, ext


def rename_files(original_files: List[str], new_names: List[str]) -> None:
    """
    Renames the files specified in 'original_files' using the corresponding names from 'new_names'.

    The original file extension is preserved. Assumes that both lists are ordered in the same way.

    Args:
        original_files (List[str]): List of absolute file paths.
        new_names (List[str]): List of new file names (without extension).

    Raises:
        ValueError: If the number of original files does not match the number of new names.
    """
    # Discard first empty new name if present
    if new_names and new_names[0] == "":
        new_names = new_names[1:]

    if len(original_files) != len(new_names):
        raise ValueError(
            "The number of original files and new names does not match.")

    for original, new in zip(original_files, new_names):
        original_path = Path(original)
        new_file_name = new + original_path.suffix
        new_path = original_path.parent / new_file_name
        logger.info(f"Renaming: {original_path} -> {new_path}")
        original_path.rename(new_path)
