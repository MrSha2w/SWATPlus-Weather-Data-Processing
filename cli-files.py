# -*- coding: utf-8 -*-
"""
Created on Jan 2025
@author: SHA2W
"""
 
import os
import csv
from datetime import datetime


def list_files_to_csv(directory, parameter, output_directory):

    try:
        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)
        
        # Get all files in the directory
        files = sorted(os.listdir(directory))  # Sorting files alphabetically
        
        # Prepare the header
        header = f"{parameter}.cli: Relative Humidity file names - file written by {Author_name} - {datetime.now().strftime('%b %Y')}"
        
        # Define output file path
        output_file = os.path.join(output_directory, f"{parameter}.cli")
        
        # Write to CSV file
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([header])
            writer.writerow(["filename"])  # Column header
            for filename in files:
                writer.writerow([filename])
        
        print(f"File list has been saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")

# Example usage
directory_path = r"PATH-TO-REFOREMATED-DATA\wnd"
output_directory = r"PATH-TO-REFOREMATED-DATA"
parameter_name = "wnd"
Author_name = "YOUR NAME"
list_files_to_csv(directory_path, parameter_name, output_directory)
 
