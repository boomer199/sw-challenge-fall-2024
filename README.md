# CTG Stock Data Processor

## Overview

This program processes CTG stock data from CSV files, cleans the data, and generates OHLCV (Open, High, Low, Close, Volume) data for specified time intervals. The program is designed to handle data from multiple CSV files, clean the data by removing invalid prices and duplicate timestamps, and filter the data based on a given timeframe.

## Functionality

### Data Loading

The program reads CSV files from a specified directory, combines the data into a single list, and returns it for further processing.

### Data Cleaning

The program cleans the data by:
1. Removing rows with invalid prices (negative or non-numeric values).
2. Removing rows with duplicate timestamps.

### Data Filtering

The program filters the data based on a specified start and end datetime.

### OHLCV Generation

The program generates OHLCV data for specified time intervals (e.g., 1 minute, 5 minutes).

### Saving to CSV

The program saves the generated OHLCV data to a CSV file.

## How to Use

1. **Prepare the Data Directory**: Ensure that your CSV files are placed in the `./data` directory. The files should follow the naming convention `ctg_tick_YEARMONTH_MINUTE_RandomString.csv`.

2. **Run the Program**: Execute the program with the following command:
   ```sh
   python main.py <start_date> <start_time> <end_date> <end_time> <interval>
   ```
   - `<start_date>`: The start date in `YYYY-MM-DD` format.
   - `<start_time>`: The start time in `HH:MM:SS` format.
   - `<end_date>`: The end date in `YYYY-MM-DD` format.
   - `<end_time>`: The end time in `HH:MM:SS` format.
   - `<interval>`: The time interval for OHLCV data (e.g., `1m` for 1 minute, `5m` for 5 minutes).

3. **Output**: The program will generate an `ohlcv_data.csv` file containing the OHLCV data for the specified timeframe and interval.

## Example

To process data from `2024-09-18 09:30:00` to `2024-09-18 16:00:00` with a 1-minute interval, run:

```
python main.py 2024-09-18 09:30:00 2024-09-18 16:00:00 1m
```

## Notes

- Ensure that the data directory exists and contains the relevant CSV files.
- The program assumes that the price is in the second column and the timestamp is in the first column of the CSV files.
- The program will print debugging information if there are issues with reading files or parsing data.
