import os
from datetime import datetime, timedelta
import sys

# Read the CSV file and return the data
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

# Process the data from the CSV files
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


# Remove invalid prices
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

# Remove duplicate timestamps
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

# Clean the data
def clean_data(data):
    data = remove_invalid_prices(data)
    data = remove_duplicate_timestamps(data)
    
    return data

cleaned_data = clean_data(combined_data)

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


def round_time(dt, delta):
    """Round a datetime object to the nearest interval."""
    round_to = delta.total_seconds()
    seconds = (dt - dt.min).seconds
    # Round to the nearest interval
    rounding = (seconds + round_to / 2) // round_to * round_to
    return dt + timedelta(0, rounding - seconds, -dt.microsecond)


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

# Filter the data by timeframe
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