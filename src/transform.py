from pathlib import Path
import json
import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
COLUMNS = ["bs_published_date", "list_id", "list_name", "primary_isbn13", "author", "title", "rank", "rank_last_week", "weeks_on_list"]

def find_raw_files():
    """Look up and retrieve the paths to the raw data files
    Returns: list of paths sorted from oldest to recent
    """
    return sorted(RAW_DIR.glob("lists_*.json"))

def load_raw(path):
    """Loads the data of given path
    Args: path of the data
    Returns: dict of the data
    """
    with open(path, "r") as f:
        return json.load(f)

def flatten_week(payload):
    """Takes the loaded data and transforms it into a flattened dataframe.
    Args: Loaded data (python dict)
    Returns: Dataframe with desired columns
    """
    bs_lists = payload["results"]["lists"]
    published_date = payload["results"]["published_date"]
    df = pd.json_normalize(data=bs_lists, record_path="books", meta=["list_name", "list_id"])
    df["bs_published_date"] = published_date

    df_rows = len(df)
    expected_num_results = payload["num_results"]
    if df_rows != expected_num_results:
        raise ValueError(f"Row count mismatch on lists from {published_date}, expected number of rows is {expected_num_results}, actual row count is {df_rows}.")
    
    return df[COLUMNS]

def combine_weeks(dfs):
    """Stack the weekly DataFrames into one table, sort it and set the column types.
    Rows are sorted by published date, then list ID, then rank, so
    each week's lists appear in order with books from rank 1 down.
    Args: List of weekly DataFrames from flatten_week.
    Returns: One combined, sorted DataFrame.
    """
    combined = pd.concat(objs=dfs, ignore_index=True)
    combined = combined.sort_values(by=["bs_published_date", "list_id", "rank"], ignore_index=True)
    combined["bs_published_date"] = pd.to_datetime(combined["bs_published_date"])
    combined["list_id"] = combined["list_id"].astype(int)
    return combined

def validate(df):
    """Run data-quality checks on the combined DataFrame.
    Checks that every row has an ISBN-13, that no book appears twice
    for the same date and list, and that rank, weeks_on_list and
    rank_last_week are within valid ranges.
    Args: The combined DataFrame from combine_weeks.
    Raises: ValueError if any check fails.
    """
    isbn_13 = df["primary_isbn13"]
    isbn_13_isna_sum = isbn_13.isna().sum()
    isbn_13_emptystr_sum = (isbn_13 == "").sum()
    if isbn_13_isna_sum > 0 or isbn_13_emptystr_sum > 0:
        raise ValueError(f"{isbn_13_isna_sum} ISBN13 values are NA, {isbn_13_emptystr_sum} ISBN13 values are empty strings")

    duplicates_count = df.duplicated(subset=["bs_published_date", "list_id", "primary_isbn13"]).sum()
    if duplicates_count > 0:
        raise ValueError(f"There are {duplicates_count} duplicate rows for the same date, list and ISBN in the DataFrame")

    invalid_rank_count = (df["rank"] <= 0).sum()
    invalid_weeks_on_list_count = (df["weeks_on_list"] <= 0).sum()
    invalid_rank_last_week_count = (df["rank_last_week"] < 0).sum()
    if invalid_rank_count > 0 or invalid_weeks_on_list_count > 0 or invalid_rank_last_week_count > 0:
        raise ValueError(f"There are {invalid_rank_count} rows with ranks < 1, {invalid_weeks_on_list_count} rows with weeks_on_list < 1 and {invalid_rank_last_week_count} rows with rank_last_week < 0.")

def save_processed(df):
    """Save the processed DataFrame as a CSV file.
    Overwrites the file on each run, since the processed table is
    rebuilt from all raw files every time.
    Args: the validated DataFrame.
    Returns: the path of the saved CSV file.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    processed_path = PROCESSED_DIR / "bestsellers.csv"
    df.to_csv(path_or_buf=processed_path, index=False)
    return processed_path

def main():
    """Run the transform step: raw JSON files → validated CSV"""
    files = find_raw_files()
    file_count = len(files)

    if not files:
        raise RuntimeError("No raw data found, run extract.py first.")
    
    print(f"Found {file_count} raw data files.")

    dfs = []

    for file in files:
        data = load_raw(file)
        df = flatten_week(data)
        dfs.append(df)

    processed_df = combine_weeks(dfs)
    print(f"Combined {len(dfs)} DataFrames into one stacked DataFrame.")

    validate(processed_df)
    print("Validation passed")

    processed_path = save_processed(processed_df)
    print(f"Saved {len(processed_df)} rows from {file_count} weeks to {processed_path}.")

if __name__ == "__main__":
    main()