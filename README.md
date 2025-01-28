# SWAT Weather Data Processing Scripts

## Overview
This repository contains three Python scripts designed to process meteorological data from **MeteoSwiss** and format it for use in the **SWAT (Soil and Water Assessment Tool) model**. These scripts handle **precipitation, temperature (max/min), and relative humidity** data, ensuring they are structured correctly for SWAT simulations.

## Features
- **Script 1: Precipitation Data Processing**
  - Reads and reformats raw precipitation data.
  - Extracts relevant station information from a legend file.
  - Handles missing values and creates SWAT-compatible `.pcp` files.

- **Script 2: Temperature Data Processing**
  - Processes daily maximum and minimum temperature data.
  - Merges separate files for Tmax and Tmin.
  - Generates `.tmp` files formatted for SWAT.

- **Script 3: CLI File Generator**
  - Lists processed climate files.
  - Generates a `.cli` file containing the names of available weather data files.

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/your-repo/swat-weather-data.git
   cd swat-weather-data
   ```
2. Install required dependencies:
   ```sh
   pip install pandas chardet
   ```

## Usage Instructions
### 1. Precipitation Data Processing
Run the following command, replacing `INPUT_DIR` and `OUTPUT_DIR` with actual paths:
```sh
python precipitation_processing.py
```

### 2. Temperature Data Processing
```sh
python temperature_processing.py
```

### 3. Generating CLI File
```sh
python generate_cli_list.py
```

## Data Source
- The scripts are designed for **MeteoSwiss** datasets but can be adapted to other sources with similar formats.
- Ensure the input files contain correctly formatted station data and measurements.

## Output Formats
- `.pcp` for precipitation
- `.tmp` for temperature
- `.cli` for climate file listing

## License
This project is open-source and free to use. Contributions and improvements are welcome!

## Contact
For any issues or suggestions, please create an issue in the repository or contact **Mostafa Jafari**.

