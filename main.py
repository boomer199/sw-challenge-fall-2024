import os
from datetime import datetime, timedelta
import sys

"""
Reads the CSV file and returns the data.

This function opens the specified CSV file, reads its contents, and returns a list of lists, where each inner list represents a row from the CSV file.

Parameters:
    file_path (str): The path to the CSV file to be read.

Returns:
    list: A list of lists containing the data from the CSV file.
"""
def read_csv(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        # Split lines into columns
        data = [line.strip().split(',') for line in lines]
        return data
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

"""
Processes the data from the CSV files.

This function reads all CSV files in the specified directory, combines their data, and returns a single list of data.

Returns:
    list: A combined list of data from all CSV files.
"""
def process_data():
    # Define the directory containing the CSV file
    data_dir = './data'
    
    # Convert to absolute path
    data_dir = os.path.abspath(data_dir)
    
    # Check if the directory exists
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} does not exist.")
        return []
    
    # Get a list of all files in the data directory
    all_files = os.listdir(data_dir)
    
    # Filter files matching the pattern
    csv_files = [file for file in all_files if file.startswith('ctg_tick_') and file.endswith('.csv')]
    
    # Initialize an empty list to store all data
    combined_data = []
    
    # Loop through each file and read the data
    for file in csv_files:
        file_path = os.path.join(data_dir, file)
        data = read_csv(file_path)
        combined_data.extend(data)
    
    return combined_data

# Call the function and store the result
combined_data = process_data()


"""
Removes invalid prices from the data.

This function calculates the average price and defines a threshold for outliers. It then iterates through the data, checks for valid prices, and removes rows with invalid or outlier prices.

Parameters:
    data (list): The list of data containing prices.

Returns:
    list: The list of data with invalid prices removed.
"""
def remove_invalid_prices(data):
    price_index = 1  
    
    # Calculate the average price
    prices = []
    for row in data:
        try:
            price = float(row[price_index])
            if price > 0:  # Only consider positive prices
                prices.append(price)
        except ValueError:
            continue  # Skip rows with non-numeric prices
    
    if not prices:
        return []  # Return empty list if no valid prices found
    
    average_price = sum(prices) / len(prices)
    threshold = average_price * 0.5  # Define a threshold for outliers (50% of the average price)
   # Iterate through the data and remove rows with invalid or outlier prices
    valid_data = []
    for row in data:
        try:
            price = float(row[price_index])
            if price > 0 and price >= threshold:  # Check for positive prices and outliers
                valid_data.append(row)
        except ValueError:
            continue  # Skip rows with non-numeric prices
    return valid_data

"""
Removes duplicate timestamps from the data.

This function iterates through the data, checks for duplicate timestamps, and removes them.

Parameters:
    data (list): The list of data containing timestamps.

Returns:
    list: The list of data with duplicate timestamps removed.
"""
def remove_duplicate_timestamps(data):
    timestamp_index = 0  
    
    # Create a dictionary to store unique timestamps
    unique_timestamps = {}
    
    # Iterate through the data and remove duplicate timestamps
    for row in data:
        timestamp = row[timestamp_index]
        if timestamp not in unique_timestamps:
            unique_timestamps[timestamp] = row

    return list(unique_timestamps.values())

"""
Cleans the data by removing invalid prices and duplicate timestamps.

This function first removes invalid prices and then removes duplicate timestamps from the data.

Parameters:
    data (list): The list of data to be cleaned.

Returns:
    list: The cleaned list of data.
"""
def clean_data(data):
    data = remove_invalid_prices(data)
    data = remove_duplicate_timestamps(data)
    
    return data

cleaned_data = clean_data(combined_data)


"""
Parses the interval string and returns a timedelta object.

This function takes an interval string (e.g., '1h', '5m', '30s') and converts it into a timedelta object. It supports days, hours, minutes, and seconds.

Parameters:
    interval_str (str): The interval string to be parsed.

Returns:
    timedelta: The parsed timedelta object.
"""
def parse_interval(interval_str):
    units = {'d': 'days', 'h': 'hours', 'm': 'minutes', 's': 'seconds'}
    time_params = {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0}
    num = ''
    
    for char in interval_str:
        if char.isdigit():
            num += char
        elif char in units:
            if num:
                time_params[units[char]] += int(num)  # Use += to accumulate time units
                num = ''
            else:
                raise ValueError(f"Invalid interval format: {interval_str}")
        else:
            raise ValueError(f"Invalid character in interval format: {char}")
    
    if num:  # Handle the case where the string ends with a number
        raise ValueError(f"Invalid interval format: {interval_str}")
    
    return timedelta(**time_params)

"""
Rounds a datetime object to the nearest interval based on the provided delta.

This function calculates the total seconds in the delta and the seconds since the start of the day for the given datetime. It then rounds the datetime to the nearest interval by adding or subtracting the necessary seconds to align with the interval.

Parameters:
    dt (datetime): The datetime object to be rounded.
    delta (timedelta): The interval to which the datetime should be rounded.

Returns:
    datetime: The rounded datetime object.
"""
def round_time(dt, delta):
    round_to = delta.total_seconds()
    seconds = (dt - dt.min).seconds
    # Round to the nearest interval
    rounding = (seconds + round_to / 2) // round_to * round_to
    return dt + timedelta(0, rounding - seconds, -dt.microsecond)

"""
Generates OHLCV data from the cleaned data based on the specified interval.

This function takes the cleaned data and an interval string, parses the interval, and then iterates through the data to generate OHLCV (Open, High, Low, Close, Volume) data.

Parameters:
    data (list): The cleaned list of data.
    interval (str): The interval string (e.g., '1h', '5m', '30s').

Returns:
    list: The list of OHLCV data.
""" 
def generate_ohlcv(data, interval):
    interval_td = parse_interval(interval)
    ohlcv_data = []
    current_interval_start = None
    current_ohlcv = None

    for row in data:
        timestamp = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
        timestamp = round_time(timestamp, interval_td)  # Round the timestamp to the nearest interval
        price = float(row[1])
        volume = int(row[2])

        if current_interval_start is None:
            current_interval_start = timestamp
            current_ohlcv = [timestamp, price, price, price, price, volume]
        elif timestamp >= current_interval_start + interval_td:
            ohlcv_data.append(current_ohlcv)
            current_interval_start = timestamp
            current_ohlcv =1
        else:
            current_ohlcv[2] = max(current_ohlcv[2], price)  # High
            current_ohlcv[3] = min(current_ohlcv[3], price)  # Low
            current_ohlcv[4] = price  # Close
            current_ohlcv[5] += volume  # Volume

    if current_ohlcv:
        ohlcv_data.append(current_ohlcv)

    return ohlcv_data

"""
Filters the data by the specified start and end times.

This function takes the data and start and end times, converts them into datetime objects, and then iterates through the data to filter out rows that fall within the specified time range.

Parameters:
    data (list): The list of data to be filtered.
    start_time (str): The start time string in 'YYYY-MM-DD HH:MM:SS' format.
    end_time (str): The end time string in 'YYYY-MM-DD HH:MM:SS' format.
   
Returns:
    list: The filtered list of data.
"""
def filter_data_by_timeframe(data, start_time, end_time):
    start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S') 
    end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    
    print(f"Start datetime: {start_dt}, End datetime: {end_dt}")  # Debugging line
    
    filtered_data = []
    #O(n) - probably a better way to do this but this is the most readable and easiest (also the file size isnt huge do it doesnt matter that much)
    for row in data:
        try:
            row_time = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
            if start_dt <= row_time <= end_dt:
                filtered_data.append(row)
        except ValueError as e:
            print(f"Skipping row due to error: {row}, Error: {e}")  # Debugging line
    

    return filtered_data


"""
Saves the OHLCV data to a CSV file.

This function takes the OHLCV data and a filename, and then writes the data to a CSV file with the specified filename.

Parameters:
    data (list): The list of OHLCV data to be saved.
    filename (str): The name of the file to which the data should be saved.
 
Returns:
    None
"""
def save_to_csv(data, filename):
    with open(filename, 'w') as file:
        file.write('timestamp,open,high,low,close,volume\n')
        for row in data:
            file.write(','.join(map(str, row)) + '\n')


# '2024-09-18 09:30:00' '2024-09-18 16:00:00' '1m' = format
if __name__ == "__main__":
    if len(sys.argv) != 6: # needs to be 6 because sys.argv[0] is the name of the script
        print("Usage: python main.py <start_date> <start_time> <end_date> <end_time> <interval>")
        sys.exit(1)

    start_date = sys.argv[1]
    start_time = sys.argv[2]
    end_date = sys.argv[3]
    end_time = sys.argv[4]
    interval = sys.argv[5]

    start_datetime = f"{start_date} {start_time}"
    end_datetime = f"{end_date} {end_time}"

    filtered_data = filter_data_by_timeframe(cleaned_data, start_datetime, end_datetime)
    ohlcv_data = generate_ohlcv(filtered_data, interval)
    save_to_csv(ohlcv_data, 'ohlcv_data.csv')