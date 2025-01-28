# -*- coding: utf-8 -*-
"""
Created on Jan 2025
@author: SHA2W
"""

import os
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
import chardet
import re

# Input directory containing the files
input_dir = r"PATH-TO-METESWISS-DATA\Air temperature - max min"
output_dir = r"PATH-TO-REFOREMATED-DATA\Temperature"
missed_values_dir = os.path.join(output_dir, "missed_values")
os.makedirs(missed_values_dir, exist_ok=True)

# Define dynamic parameters
DATA_COLUMN_MIN = "tre200dn"  # Temperature Min Column
DATA_COLUMN_MAX = "tre200dx"  # Temperature Max Column
EXTENSION = "tmp"  # Output file extension

# Helper function to detect file encoding
def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
    return result.get("encoding", "utf-8")

# Function to sanitize filenames
def sanitize_filename(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)

# Process legend file
def parse_legend_file(legend_file):
    encoding = detect_encoding(legend_file)
    station_info = {}
    with open(legend_file, "r", encoding=encoding, errors="replace") as file:
        lines = file.readlines()

    start_index = None
    for i, line in enumerate(lines):
        if line.strip() == "Stations":
            start_index = i + 3
            break

    if start_index is None:
        raise ValueError(f"Legend file {legend_file} does not contain a 'Stations' section.")

    for line in lines[start_index:]:
        if line.strip() == "":
            break
        parts = line.split()
        stn = parts[0]
        name = " ".join(parts[1:-3]).strip()
        longitude_latitude = parts[-3]
        elevation = parts[-1]
        station_info[stn] = {
            "name": name,
            "longitude_latitude": longitude_latitude,
            "elevation": elevation,
        }
    return station_info

# Process data files
def process_temperature_data(min_data_file, max_data_file, station_info, output_dir):
    encoding = detect_encoding(min_data_file)
    
    min_df = pd.read_csv(min_data_file, sep=";", encoding=encoding, dtype=str)
    max_df = pd.read_csv(max_data_file, sep=";", encoding=encoding, dtype=str)
    
    for df in [min_df, max_df]:
        df["time"] = pd.to_datetime(df["time"], format="%Y%m%d", errors="coerce")
        df["day_of_year"] = df["time"].dt.day_of_year
        df["year"] = df["time"].dt.year
    
    merged_df = pd.merge(min_df, max_df, on=["time", "year", "day_of_year"], how="outer", suffixes=("_min", "_max"))
    merged_df[DATA_COLUMN_MIN] = pd.to_numeric(merged_df[DATA_COLUMN_MIN], errors="coerce").fillna(-99.0)
    merged_df[DATA_COLUMN_MAX] = pd.to_numeric(merged_df[DATA_COLUMN_MAX], errors="coerce").fillna(-99.0)
    
    station = merged_df["stn_min"].iloc[0] if "stn_min" in merged_df.columns else "Unknown"
    if station not in station_info:
        print(f"Warning: Station {station} not found in legend file.")
        return

    metadata = station_info[station]
    observed_name = f"O{station}{merged_df['year'].min()}{merged_df['year'].max()}"
    
    start_date = merged_df["time"].min()
    end_date = merged_df["time"].max()
    years_difference = end_date.year - start_date.year + 1
    
    # Generate output content
    file_content = (
        f"{observed_name}.{EXTENSION}:: {EXTENSION} file for station {observed_name}\n"
        f"nbyr     tstep       lat       lon      elev\n"
        f"{years_difference}    0 {metadata['longitude_latitude']} {metadata['elevation']}\n"
    )
    
    for _, row in merged_df.iterrows():
        file_content += f"{row['year']}    {row['day_of_year']:03d}   {float(row[DATA_COLUMN_MIN]):.6f}   {float(row[DATA_COLUMN_MAX]):.6f}\n"
    
    text_output_file = os.path.join(output_dir, f"{observed_name}.{EXTENSION}")
    with open(text_output_file, "w", encoding="utf-8") as f:
        f.write(file_content)
    print(f"File created: {text_output_file}")
    
    # Find and save missing values
    missing_dates = merged_df[(merged_df[DATA_COLUMN_MIN] == -99.0) | (merged_df[DATA_COLUMN_MAX] == -99.0)]["time"]
    if not missing_dates.empty:
        missed_values_file = os.path.join(missed_values_dir, f"missed_values_{station}.csv")
        with open(missed_values_file, "w", encoding="utf-8") as f:
            for i, date in enumerate(missing_dates, 1):
                missing_info = "(tmax)" if merged_df.loc[merged_df["time"] == date, DATA_COLUMN_MAX].iloc[0] == -99.0 else "(tmin)"
                f.write(f"{i}- {date.strftime('%Y-%m-%d')} {missing_info}\n")
        print(f"Missed values file created: {missed_values_file}")

# Main processing function
def main(input_dir, output_dir):
    station_info = {}

    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)
        if file.endswith("_legend.txt"):
            station_info.update(parse_legend_file(file_path))

    if not station_info:
        raise ValueError("No legend file found in the input directory.")

    data_files = {}  # Group min and max data files by station
    for file in os.listdir(input_dir):
        if file.endswith("_data.txt"):
            parts = file.split("_")
            station = parts[2]
            param = parts[3]
            data_files.setdefault(station, {})[param] = os.path.join(input_dir, file)
    
    for station, files in data_files.items():
        if DATA_COLUMN_MIN in files and DATA_COLUMN_MAX in files:
            process_temperature_data(files[DATA_COLUMN_MIN], files[DATA_COLUMN_MAX], station_info, output_dir)

if __name__ == "__main__":
    main(input_dir, output_dir)
