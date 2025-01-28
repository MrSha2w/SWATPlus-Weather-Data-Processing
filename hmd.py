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
input_dir = r"PATH-TO-METESWISS-DATA\Wind Speed"
output_dir = r"PATH-TO-REFOREMATED-DATA\wnd"
missed_values_dir = os.path.join(output_dir, "missed_values")
os.makedirs(missed_values_dir, exist_ok=True)
EXTENTION = "wnd"
DATA_COLUMN = "fkl010d0"   #Realated parameter to MeteoSwiss files

# Helper function to detect file encoding
def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
    return result.get("encoding", "utf-8")

# Function to sanitize filenames
def sanitize_filename(name):
    import re
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
        name_parts = []
        for part in parts[1:-3]:
            if not any(keyword in part.lower() for keyword in [DATA_COLUMN, "meteoschweiz", "schweiz", "meteo"]):
                name_parts.append(part)
        name = " ".join(name_parts).strip()
        longitude_latitude = parts[-3]
        elevation = parts[-1]
        station_info[stn] = {
            "name": name,
            "longitude_latitude": longitude_latitude,
            "elevation": elevation,
        }
        print("Station name: ", name)
    return station_info

# Process data files
def process_data_file(data_file, station_info, output_dir):
    encoding = detect_encoding(data_file)
    
    # Skip initial blank lines and read the header correctly
    with open(data_file, "r", encoding=encoding) as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines if line.strip()]
    df = pd.read_csv(StringIO("\n".join(lines)), sep=";", encoding=encoding, dtype=str)
    
    if DATA_COLUMN not in df.columns:
        raise KeyError("Column '{DATA_COLUMN}' not found in data file. Available columns: " + ", ".join(df.columns))
    
    df["time"] = pd.to_datetime(df["time"], format="%Y%m%d", errors="coerce")
    df["day_of_year"] = df["time"].dt.day_of_year
    df["year"] = df["time"].dt.year
    
    # Replace non-numeric values with NaN, then replace NaN with -99.0
    df[DATA_COLUMN] = pd.to_numeric(df[DATA_COLUMN], errors="coerce").fillna(-99.0)
    
    print("group by Station: ", df.groupby("stn"))
    
    for station, station_data in df.groupby("stn"):
        print(f"station: {station}")
        print(f"station_data: {station_data}")
        
        if station not in station_info:
            print(f"Warning: Station {station} not found in legend file.")
            continue

        metadata = station_info[station]
        station_name = sanitize_filename(metadata["name"])
        observed_name = f"O{station}{station_data['year'].min()}{station_data['year'].max()}"

        start_date = station_data["time"].min()
        end_date = station_data["time"].max()
        years_difference = end_date.year - start_date.year + 1
        
        # Generate output content
        file_content = (
            f"{observed_name}.{EXTENTION}:: {EXTENTION} file for station {observed_name}\n"
            f"nbyr     tstep       lat       lon      elev\n"
            f"{years_difference}    0 {metadata['longitude_latitude']} {metadata['elevation']}\n"
        )
        
        for _, row in station_data.iterrows():
            file_content += f"{row['year']}    {row['day_of_year']:03d}   {row[DATA_COLUMN]:.6f}\n"
        
        text_output_file = os.path.join(output_dir, f"{observed_name}.{EXTENTION}")
        with open(text_output_file, "w", encoding="utf-8") as f:
            f.write(file_content)
        print(f"File created: {text_output_file}")
        
        # Find and save missing values
        missing_dates = station_data[station_data[DATA_COLUMN] == -99.0]["time"]
        if not missing_dates.empty:
            missed_values_file = os.path.join(missed_values_dir, f"missed_values_{station}.csv")
            with open(missed_values_file, "w", encoding="utf-8") as f:
                for i, date in enumerate(missing_dates, 1):
                    f.write(f"{i}- {date.strftime('%Y-%m-%d')}\n")
            print(f"Missed values file created: {missed_values_file}")

# Main processing function
def main(input_dir, output_dir):
    station_info = {}

    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)

        if file.endswith("_legend.txt"):
            station_info.update(parse_legend_file(file_path))
            print(f"Parsed legend file: {file_path}")

    if not station_info:
        raise ValueError("No legend file found in the input directory.")

    for file in os.listdir(input_dir):
        if file.endswith("_data.txt"):
            print("station info: ", station_info)
            data_file = os.path.join(input_dir, file)
            print(f"Starting Data file: {data_file}")
            process_data_file(data_file, station_info, output_dir)

if __name__ == "__main__":
    main(input_dir, output_dir)