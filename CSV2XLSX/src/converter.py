"""CSV and Excel file conversion utilities.

This module provides functions for converting between CSV and Excel (XLSX) formats
with support for multiple encodings and progress tracking.
"""

import os
from pathlib import Path
from typing import List, Optional, Callable, Union

import pandas as pd
from openpyxl import Workbook


class ConversionError(Exception):
    """Custom exception for conversion-related errors."""
    pass


class EncodingDetectionError(ConversionError):
    """Exception raised when encoding detection fails."""
    pass


class FileProcessingError(ConversionError):
    """Exception raised during file processing."""
    pass


# Constants
MAX_SHEET_NAME_LENGTH = 31
DEFAULT_ENCODINGS = ["utf-8", "shift_jis"]


def _detect_encoding_and_read_csv(csv_file: Union[str, Path]) -> pd.DataFrame:
    """Detect encoding and read CSV file with automatic fallback.

    Args:
        csv_file: Path to the CSV file

    Returns:
        DataFrame with the CSV data

    Raises:
        EncodingDetectionError: If no supported encoding works
        FileProcessingError: If file cannot be processed
    """
    csv_path = Path(csv_file)

    if not csv_path.exists():
        raise FileNotFoundError(f"Input file not found: {csv_file}")

    for encoding in DEFAULT_ENCODINGS:
        try:
            return pd.read_csv(csv_path, encoding=encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
        except Exception as e:
            raise FileProcessingError(f"Error processing file {csv_file}: {e}")

    raise EncodingDetectionError(
        f"Unable to detect encoding for file: {csv_file}. "
        f"Tried encodings: {DEFAULT_ENCODINGS}"
    )


def _generate_unique_sheet_name(base_name: str, used_names: set) -> str:
    """Generate a unique sheet name that doesn't exceed Excel's limits.

    Args:
        base_name: The base name for the sheet
        used_names: Set of already used sheet names

    Returns:
        A unique sheet name
    """
    # Clean and truncate base name
    clean_name = base_name[:MAX_SHEET_NAME_LENGTH]

    if clean_name not in used_names:
        return clean_name

    # Generate unique name with suffix
    counter = 1
    while True:
        suffix = f"_{counter}"
        max_base_length = MAX_SHEET_NAME_LENGTH - len(suffix)
        unique_name = f"{clean_name[:max_base_length]}{suffix}"

        if unique_name not in used_names:
            return unique_name
        counter += 1


def csv_to_xlsx(
    csv_files: List[Union[str, Path]],
    output_xlsx: Union[str, Path],
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> None:
    """Convert multiple CSV files to a single XLSX file with multiple sheets.

    Each CSV file becomes a separate sheet in the output Excel file.
    Sheet names are automatically generated from file names and made unique.

    Args:
        csv_files: List of paths to input CSV files
        output_xlsx: Path to the output XLSX file
        progress_callback: Optional callback function for progress updates.
                          Called with (current_step, total_steps)

    Raises:
        ConversionError: If conversion fails
        FileNotFoundError: If any input file is not found
    """
    if not csv_files:
        raise ValueError("No CSV files provided")

    # Validate all input files exist
    for csv_file in csv_files:
        csv_path = Path(csv_file)
        if not csv_path.exists():
            raise FileNotFoundError(f"Input file not found: {csv_file}")
        if not csv_path.suffix.lower() == '.csv':
            raise ValueError(f"File is not a CSV file: {csv_file}")

    # Ensure output directory exists
    output_path = Path(output_xlsx)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total_files = len(csv_files)
    used_sheet_names = set()

    try:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for i, csv_file in enumerate(csv_files):
                try:
                    # Read CSV with encoding detection
                    df = _detect_encoding_and_read_csv(csv_file)

                    # Generate unique sheet name
                    base_name = Path(csv_file).stem
                    sheet_name = _generate_unique_sheet_name(base_name, used_sheet_names)
                    used_sheet_names.add(sheet_name)

                    # Write to Excel
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

                    # Update progress
                    if progress_callback:
                        progress_callback(i + 1, total_files)

                except Exception as e:
                    raise FileProcessingError(f"Error processing {csv_file}: {e}")

    except Exception as e:
        if isinstance(e, (ConversionError, FileNotFoundError, ValueError)):
            raise
        raise ConversionError(f"Failed to convert CSV files to XLSX: {e}")


def xlsx_to_csv(
    input_xlsx: str,
    output_dir: str,
    encoding: str = "utf-8",
    progress_callback: Optional[Callable[[int, int], None]] = None,
):
    """
    Converts all sheets in an XLSX file to separate CSV files.

    Args:
        input_xlsx: The path to the input XLSX file.
        output_dir: The directory where the output CSV files will be saved.
        encoding: The encoding to use for the output CSV files.
        progress_callback: An optional function to call with progress updates.
                           It receives (current_step, total_steps).
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with pd.ExcelFile(input_xlsx) as xls:
        sheet_names = xls.sheet_names
        total_sheets = len(sheet_names)
        for i, sheet_name in enumerate(sheet_names):
            df = xls.parse(sheet_name)

            base_filename = os.path.splitext(os.path.basename(input_xlsx))[0]
            output_csv_path = os.path.join(
                output_dir, f"{base_filename}_{sheet_name}.csv"
            )

            # BOM付きUTF-8で出力（Excel互換性のため）
            if encoding.lower() in ['utf-8', 'utf8']:
                df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
            else:
                df.to_csv(output_csv_path, index=False, encoding=encoding)

            if progress_callback:
                progress_callback(i + 1, total_sheets)
