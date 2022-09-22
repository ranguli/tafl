import csv
import json
import sqlite3

from tqdm import tqdm
from sqlite_utils import Database

csv_headers_file = "headers.txt"
csv_file = "TAFL_LTAF.csv"

data_file = "data.json"
data_json = {}

with open(data_file) as f:
    data_json = json.load(f)


def set_attribute(row, attribute):
    code = row.get(attribute)

    if not code:
        return row

    row[attribute] = data_json.get(attribute).get(row.get(attribute))
    return row

def set_polarization(row):
    polarization_code = row.get("Polarization")

    if not polarization_code:
        return row

    row["Polarization"] = data_json.get("polarization").get(row.get("Polarization"))
    return row


def set_filtered_columns(row):
    return {key: row[key] for key in row if key not in data_json.get('filter_columns')}

def process_row(row):
    attributes = data_json.get("Attributes")
    processed_row = set_filtered_columns(row)

    for attribute in attributes:
        processed_row = set_attribute(processed_row, attribute)
    return processed_row


csv_fieldnames = []

db = Database("tafl.db")
tafl = db["tafl"]

with open(csv_headers_file) as headers:
    for line in headers:
        csv_fieldnames.append(line.strip())

db = Database("my_database.db")
table = db['TAFL_LTAF']

rows = []

print("Iterating and processing rows")

with open(csv_file, newline='') as f:
    reader = csv.DictReader(f, fieldnames=csv_fieldnames)
    for row in tqdm(reader):
        processed_row = process_row(row)

        if processed_row is None:
            print("error!")
            exit()

        rows.append(processed_row)


column_order = [
        "Frequency",
        "Radio Type",
        "Call sign",
        "In service date",
        "Station location",
        "Province",
        "Latitude",
        "Longitude",
        "Licensee name",
        "ITU class",
        "Service",
        "Subservice"
        "Occupied bandwidth",
        "Modulation type"
]


print(f"Bulk inserting {len(rows)} rows, this will take several minutes.")
tafl.insert_all(rows, batch_size=50000, column_order=column_order)

print("Done inserting, enabling full-text search")
tafl.enable_fts(["Manufacturer", "Model number", "Station location", "Call sign", "Licensee name", "In service date"])

print("Full-text search enabled, optimizing")
tafl.optimize()
db.vacuum()
