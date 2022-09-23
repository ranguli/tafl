import csv
import json
import sqlite3

from tqdm import tqdm
from sqlite_utils import Database
from quantiphy import Quantity

csv_headers_file = "headers.txt"
csv_file = "TAFL_LTAF.csv"

data_file = "data.json"
data_json = {}

with open(data_file) as f:
    data_json = json.load(f)

def get_band(freq_hz):
    # oof
    if 3 < freq_hz < 30:
        return "ELF"
    elif 30 < freq_hz < 300:
        return "SLF"
    elif 300 < freq_hz < 3000:
        return "ULF"
    elif 3000 < freq_hz < 30e3:
        return "VLF"
    elif 30e3 < freq_hz < 30e4:
        return "LF"
    elif 30e4 < freq_hz < 30e5:
        return "MF"
    elif 30e5 < freq_hz < 30e6:
        return "HF"
    elif 30e6 < freq_hz < 30e7:
        return "VHF"
    elif 30e7 < freq_hz < 30e8:
        return "UHF"
    elif 30e8 < freq_hz < 30e9:
        return "SHF"
    elif 30e9 < freq_hz < 30e10:
        return "EHF"
    elif 30e10 < freq_hz < 30e11:
        return "THF"

def set_freq_band(row):
    freq_hz = row.get("Frequency (Hz, Sortable)")
    row["Frequency Band"] = get_band(freq_hz)

    return row

def set_friendly_freq(row):
    freq = row.get("Frequency (Hz, Sortable)")
    if freq is None:
        return row

    freq = Quantity(f"{freq} Hz")


    row['Frequency (Friendly)'] = str(freq)
    return row

def set_freq_hz(row):
    freq = row.get("Frequency (Hz, Sortable)")

    if freq is None:
        return row

    freq = Quantity(f"{freq} MHz")

    row["Frequency (Hz, Sortable)"] = float(freq)

    return row

def set_attribute(row, attribute):
    code = row.get(attribute)

    if not code:
        return row

    row[attribute] = data_json.get("csv_parsing_data").get(attribute).get(row.get(attribute))
    return row

def set_filtered_columns(row):
    return {key: row[key] for key in row if key not in data_json.get("filter_columns")}


def process_row(row):
    attributes = data_json.get("csv_parsing_data").get("Attributes")
    processed_row = set_filtered_columns(row)

    for attribute in attributes:
        processed_row = set_attribute(processed_row, attribute)

    processed_row = set_freq_hz(processed_row)
    processed_row = set_friendly_freq(processed_row)
    processed_row = set_freq_band(processed_row)

    return processed_row

def ignore_row(row):
    # A duplicate record that breaks primary key constraints
    if row.get("Frequency record identifier") in data_json.get("ignore_duplicates"):
        return True

    return False

def main():
    csv_fieldnames = []

    db = Database("tafl.db")
    tafl = db["tafl"]

    with open(csv_headers_file) as headers:
        for line in headers:
            csv_fieldnames.append(line.strip())

    rows = []

    print("Iterating and processing rows")

    with open(csv_file, newline="\n") as f:
        reader = csv.DictReader(f, fieldnames=csv_fieldnames)
        for row in tqdm(reader):
            if ignore_row(row):
                continue

            processed_row = process_row(row)

            if processed_row is None:
                # TODO: error handling
                print("error!")
            rows.append(processed_row)

    column_order = data_json.get("column_order")

    print(f"Bulk inserting {len(rows)} rows, this will take several minutes.")

    #for row in rows:
        #tafl.insert(row, column_order=column_order, pk="Frequency record identifier")
    tafl.insert_all(rows, batch_size=50000, column_order=column_order, pk="Frequency record identifier")

    fts_enabled_columns = data_json.get("enable_fts")

    print("Done inserting, enabling full-text search")
    tafl.enable_fts(fts_enabled_columns)

    print("Full-text search enabled, optimizing")
    tafl.optimize()

if __name__ == "__main__":
    main()
