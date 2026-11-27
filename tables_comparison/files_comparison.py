"""
Universal output comparison tool.

For every reference file listed in REFERENCE_FILES (located in REFERENCE_DIR), the script
searches OTHER_DIR for files with the same name plus a numeric suffix
(<name>_1.<ext>, <name>_2.<ext>, ...) and compares the FIRST sheet of each file with the
FIRST sheet of the reference file.

Comparison rules
----------------
- Row order is irrelevant (full-row outer merge on all columns).
- Duplicate rows are compared as a multiset (an occurrence counter is part of the key),
  e.g. 2 identical rows in mine vs 1 in theirs -> 1 row reported as "only mine".
- Numeric columns are rounded to ROUND_DECIMALS before comparison (floating-point noise).
- Columns listed in TEXT_COLUMNS are always compared as text (leading zeros, 'YYYY-MM').
- Empty cells are compared as empty strings (blank XYZ class == blank XYZ class).
- A row that differs in a single value appears once in OnlyMine and once in OnlyTheirs.

Output
------
One Excel workbook (REPORT_PATH) with 3 sheets per compared file:
<name>_<n>_Summary, <name>_<n>_OnlyMine, <name>_<n>_OnlyTheirs
"""

import os
import re
from typing import Dict, List, Set, Tuple

import numpy as np
import pandas as pd

# =====================================================================
# Configuration
# =====================================================================
REFERENCE_DIR = os.getcwd()                          # where MY outputs are
OTHER_DIR = os.path.join(REFERENCE_DIR, "other")     # where THEIR outputs are

# Reference files to compare (the list can be longer or shorter, any file names)
REFERENCE_FILES: List[str] = [
    "abc_Stock.xlsx",
    "abc_Sales.xlsx",
    "abc_total_Stock.xlsx",
    "abc_total_Sales.xlsx",
    "xyz_Stock.xlsx",
    "xyz_Sales.xlsx",
    "xyz_wide_Stock.xlsx",
    "xyz_wide_Sales.xlsx",
]

TEXT_COLUMNS: Set[str] = {"SKU", "Period"}   # always compared as text
ROUND_DECIMALS = 6                           # precision for numeric comparison
CSV_SEP = ";"                                # used only if a reference file is .csv
REPORT_PATH = os.path.join(REFERENCE_DIR, "comparison_report.xlsx")

# Excel limits
EXCEL_MAX_DATA_ROWS = 1_048_575              # 1,048,576 rows minus the header row
SHEET_NAME_MAX = 31
INVALID_SHEET_CHARS = r"[$$$$\:\*\?\/\$$"
SHEET_SUFFIXES = ("_Summary", "_OnlyMine", "_OnlyTheirs")


# =====================================================================
# File discovery and loading
# =====================================================================
def find_other_files(reference_name: str, other_dir: str) -> List[Tuple[int, str]]:
    """Return [(suffix_number, path), ...] for files named <stem>_<n><ext>, sorted by n."""
    if not os.path.isdir(other_dir):
        return []
    stem, ext = os.path.splitext(reference_name)
    pattern = re.compile(rf"^{re.escape(stem)}_(\d+){re.escape(ext)}$", re.IGNORECASE)

    found = []
    for name in os.listdir(other_dir):
        match = pattern.match(name)          # anchored: skips Excel lock files (~$...)
        if match:
            found.append((int(match.group(1)), os.path.join(other_dir, name)))
    return sorted(found)


def load_first_sheet(path: str) -> Tuple[pd.DataFrame, str]:
    """Load the first sheet of an Excel file (or a CSV file) with all values as text."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(path, sep=CSV_SEP, dtype=str, keep_default_na=False)
        sheet = "(csv)"
    else:
        with pd.ExcelFile(path) as xls:
            sheet = xls.sheet_names[0]
            df = pd.read_excel(xls, sheet_name=sheet, dtype=str, keep_default_na=False)
    df.columns = [str(c).strip() for c in df.columns]
    return df, sheet


# =====================================================================
# Normalization
# =====================================================================
def normalize_column(name: str, s: pd.Series, decimals: int) -> Tuple[pd.Series, pd.Series]:
    """
    Return (comparison_key, display_values) for one column.
    - TEXT_COLUMNS and non-numeric columns: stripped text, blanks as "".
    - Numeric columns: rounded and formatted with a fixed number of decimals
      (-0.0 normalized to 0.0); display values are the original numbers.
    """
    text = s.fillna("").astype(str).str.strip()
    if name in TEXT_COLUMNS:
        return text, text

    blank = text.eq("")
    num = pd.to_numeric(text.mask(blank), errors="coerce")
    is_numeric = (~blank).any() and num[~blank].notna().all()
    if not is_numeric:
        return text, text

    rounded = num.round(decimals) + 0.0      # + 0.0 turns -0.0 into 0.0
    key = rounded.map(lambda v: "" if pd.isna(v) else f"{v:.{decimals}f}")

    finite = num.dropna()
    finite = finite[np.isfinite(finite)]
    if len(finite) == len(num.dropna()) and (finite % 1 == 0).all():
        display = num.astype("Int64")        # whole numbers shown without .0
    else:
        display = num
    return key, display


def normalize_frame(df: pd.DataFrame, decimals: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    keys, display = {}, {}
    for col in df.columns:
        keys[col], display[col] = normalize_column(col, df[col], decimals)
    return pd.DataFrame(keys, index=df.index), pd.DataFrame(display, index=df.index)


# =====================================================================
# Comparison
# =====================================================================
def compare_frames(mine: pd.DataFrame, theirs: pd.DataFrame, decimals: int) -> Dict:
    """Full-row multiset comparison; row order is ignored."""
    mine = mine.reset_index(drop=True)
    theirs = theirs.reset_index(drop=True)

    mine_keys, mine_disp = normalize_frame(mine, decimals)
    theirs_keys, theirs_disp = normalize_frame(theirs, decimals)
    cols = list(mine_keys.columns)

    # Occurrence counter -> duplicates are matched one-to-one
    mine_keys["__occurrence"] = mine_keys.groupby(cols, sort=False).cumcount()
    theirs_keys["__occurrence"] = theirs_keys.groupby(cols, sort=False).cumcount()
    mine_keys["__row_mine"] = np.arange(len(mine_keys))
    theirs_keys["__row_theirs"] = np.arange(len(theirs_keys))

    merged = mine_keys.merge(
        theirs_keys,
        on=cols + ["__occurrence"],
        how="outer",
        indicator="__merge",
    )

    only_mine_rows = np.sort(merged.loc[merged["__merge"] == "left_only", "__row_mine"].astype(int).to_numpy())
    only_theirs_rows = np.sort(merged.loc[merged["__merge"] == "right_only", "__row_theirs"].astype(int).to_numpy())

    only_mine = mine_disp.iloc[only_mine_rows].copy()
    only_mine.insert(0, "Source_Row", only_mine_rows + 2)       # +2 = header row + 1-based
    only_theirs = theirs_disp.iloc[only_theirs_rows].copy()
    only_theirs.insert(0, "Source_Row", only_theirs_rows + 2)

    return {
        "rows_mine": len(mine),
        "rows_theirs": len(theirs),
        "identical": int((merged["__merge"] == "both").sum()),
        "only_mine": only_mine,
        "only_theirs": only_theirs,
        "n_columns": len(cols),
    }


def build_summary(ref_path: str, ref_sheet: str, other_path: str, other_sheet: str,
                  result: Dict, notes: List[str]) -> pd.DataFrame:
    n_mine, n_theirs = len(result["only_mine"]), len(result["only_theirs"])
    denominator = max(result["rows_mine"], result["rows_theirs"])
    match_pct = 100.0 if denominator == 0 else round(100 * result["identical"] / denominator, 4)
    status = "PASS" if n_mine == 0 and n_theirs == 0 else "FAIL"

    rows = [
        ("Status", status),
        ("My file", ref_path),
        ("My sheet (first)", ref_sheet),
        ("Their file", other_path),
        ("Their sheet (first)", other_sheet),
        ("Columns compared", result["n_columns"]),
        ("Numeric rounding (decimals)", ROUND_DECIMALS),
        ("Rows in my output", result["rows_mine"]),
        ("Rows in their output", result["rows_theirs"]),
        ("Identical rows", result["identical"]),
        ("Rows only in my output", n_mine),
        ("Rows only in their output", n_theirs),
        ("Total different rows", n_mine + n_theirs),
        ("Match % (identical / larger row count)", match_pct),
        ("Interpretation", "A row differing in one value appears once in OnlyMine and once in OnlyTheirs. "
                           "Source_Row = row number in the original file."),
    ]
    rows += [("Note", n) for n in notes]
    return pd.DataFrame(rows, columns=["Metric", "Value"])


# =====================================================================
# Report helpers
# =====================================================================
def make_sheet_prefix(stem: str, number: int, used: Set[str]) -> str:
    """Sheet-name prefix '<stem>_<n>' that fits the 31-char limit and is unique (case-insensitive)."""
    tail = f"_{number}"
    max_prefix = SHEET_NAME_MAX - max(len(s) for s in SHEET_SUFFIXES)
    clean_stem = re.sub(INVALID_SHEET_CHARS, "_", stem)

    prefix = clean_stem[: max_prefix - len(tail)] + tail
    k = 1
    while any((prefix + s).lower() in used for s in SHEET_SUFFIXES):
        marker = f"~{k}"
        prefix = clean_stem[: max_prefix - len(tail) - len(marker)] + marker + tail
        k += 1
    used.update((prefix + s).lower() for s in SHEET_SUFFIXES)
    return prefix


def truncate_for_excel(df: pd.DataFrame, label: str, notes: List[str]) -> pd.DataFrame:
    if len(df) > EXCEL_MAX_DATA_ROWS:
        notes.append(f"{label}: {len(df):,} rows truncated to {EXCEL_MAX_DATA_ROWS:,} (Excel limit).")
        return df.head(EXCEL_MAX_DATA_ROWS)
    return df


def write_report(sheets: List[Tuple[str, pd.DataFrame]], path: str) -> None:
    try:
        import xlsxwriter  # noqa: F401
        engine = "xlsxwriter"
    except ModuleNotFoundError:
        print("⚠️  xlsxwriter not found. Falling back to openpyxl.")
        engine = "openpyxl"

    try:
        with pd.ExcelWriter(path, engine=engine) as writer:
            for sheet_name, data in sheets:
                data.to_excel(writer, sheet_name=sheet_name, index=False)
    except PermissionError:
        print(f"❌ Cannot write {path} – close the file in Excel and run again.")
        return
    print(f"✅ Comparison report saved as: {path}")


# =====================================================================
# Main
# =====================================================================
def main() -> None:
    if not os.path.isdir(OTHER_DIR):
        print(f"❌ Folder not found: {OTHER_DIR}")
        return

    report_sheets: List[Tuple[str, pd.DataFrame]] = []
    used_names: Set[str] = set()
    n_pass = n_fail = 0

    for ref_name in REFERENCE_FILES:
        others = find_other_files(ref_name, OTHER_DIR)
        if not others:
            print(f"ℹ️  {ref_name}: no files with suffix _<n> in {OTHER_DIR}")
            continue

        ref_path = os.path.join(REFERENCE_DIR, ref_name)
        if not os.path.isfile(ref_path):
            print(f"⚠️  {ref_name}: reference file not found in {REFERENCE_DIR} – {len(others)} file(s) skipped.")
            continue

        mine, mine_sheet = load_first_sheet(ref_path)
        stem = os.path.splitext(ref_name)[0]

        for number, other_path in others:
            other_name = os.path.basename(other_path)
            theirs, their_sheet = load_first_sheet(other_path)

            # The output format is assumed to be identical; guard only against a crash
            if set(mine.columns) != set(theirs.columns):
                print(f"⚠️  {other_name}: column names differ from {ref_name} – comparison skipped.")
                continue
            theirs = theirs[list(mine.columns)]          # same column order as mine

            result = compare_frames(mine, theirs, ROUND_DECIMALS)

            notes: List[str] = []
            only_mine = truncate_for_excel(result["only_mine"], "OnlyMine", notes)
            only_theirs = truncate_for_excel(result["only_theirs"], "OnlyTheirs", notes)
            summary = build_summary(ref_path, mine_sheet, other_path, their_sheet, result, notes)

            prefix = make_sheet_prefix(stem, number, used_names)
            report_sheets += [
                (prefix + "_Summary", summary),
                (prefix + "_OnlyMine", only_mine),
                (prefix + "_OnlyTheirs", only_theirs),
            ]

            n_diff = len(result["only_mine"]) + len(result["only_theirs"])
            if n_diff == 0:
                n_pass += 1
                print(f"✅ {other_name}: PASS ({result['identical']:,} identical rows)")
            else:
                n_fail += 1
                print(f"❌ {other_name}: FAIL (only mine: {len(result['only_mine']):,}, "
                      f"only theirs: {len(result['only_theirs']):,}, identical: {result['identical']:,})")

    if not report_sheets:
        print("ℹ️  Nothing to compare – no report created.")
        return

    print(f"--- {n_pass + n_fail} comparison(s): {n_pass} PASS, {n_fail} FAIL ---")
    write_report(report_sheets, REPORT_PATH)


if __name__ == "__main__":
    main()
