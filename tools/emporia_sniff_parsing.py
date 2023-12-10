import argparse
import csv
from collections import defaultdict
import re
from datetime import datetime

def parse_sniffed_packet(csv_data):
    # Regular expression pattern for the timestamp
    pattern = r'("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",)'
    # Split the data using the pattern, keeping the delimiters
    entries = re.split(pattern, csv_data)[1:] # first element is always empty

    parsed_data = {}
    for i in range(0, len(entries), 2):
        timestamp_str = entries[i].strip('",')
        value = entries[i + 1]

        # Parse the timestamp string into a datetime object
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

        if timestamp in parsed_data:
            # Concatenate value if timestamp already exists
            parsed_data[timestamp] += value
        else:
            # Otherwise, just add the new entry
            parsed_data[timestamp] = value

    return parsed_data

def parse_emporia(csv_data):
    parsed_data = {}
    last_value = None

    reader = csv.reader(csv_data.splitlines())
    for row in reader:
        # print(row)
        # Skip blank lines
        if not row or len(row) < 2:
            continue

        timestamp_str, value = row

        # Skip if the value is the same as the last one
        if value == last_value:
            continue

        # Parse the timestamp string into a datetime object
        try:
            timestamp = datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S')
        except ValueError:
            continue

        # Update the last value and add the new entry
        last_value = value
        parsed_data[timestamp] = value

    return parsed_data

def find_nearest_before(from_emporia, sniffed):
    result = []
    for keyA, valueA in from_emporia.items():
        # Initialize nearest datetime and its value
        nearest_time = None
        nearest_value = None
        # Go through each item in sniffed
        for keyB, valueB in sniffed.items():
            # Check if keyB is before keyA and within 1-5 seconds
            if 0 < (keyA - keyB).total_seconds() <= 5:
                # Update nearest_time if it's closer to keyA than the previous nearest_time
                if nearest_time is None or (keyA - keyB) < (keyA - nearest_time):
                    nearest_time = keyB
                    nearest_value = valueB
        # Append to result if a match is found
        if nearest_time:
            result.append((nearest_time, valueA, nearest_value))
    return result

def find_nearest_after(sniffed, from_emporia):
    result = []
    for keyA, valueA in sniffed.items():
        # Initialize nearest datetime and its value
        nearest_time = None
        nearest_value = None
        # Go through each item in dictB
        for keyB, valueB in from_emporia.items():
            # Check if keyB is after keyA and within 1-5 seconds
            if 1 < (keyB - keyA).total_seconds() <= 5:
                # Update nearest_time if it's closer to keyA than the previous nearest_time
                if nearest_time is None or (keyB - keyA) < (nearest_time - keyA):
                    nearest_time = keyB
                    nearest_value = valueB
        # Append to result if a match is found
        if nearest_time:
            result.append((keyA, valueA, nearest_value))
        else:
            print('have time', keyA, 'that doesnt have a nearest value')
    return result

def swap_endianness(hex_string):
    # Split the string into bytes (two characters each)
    bytes_list = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
    # Reverse the list of bytes and join them back into a string
    reversed_hex = ''.join(reversed(bytes_list))
    return reversed_hex

def hex_to_decimal(hex_string):
    try:
        # First, swap the endianness
        swapped_hex = swap_endianness(hex_string)
        # Then, convert the hexadecimal string to decimal
        return int(swapped_hex, 16)
    except ValueError:
        return "Invalid hexadecimal number"

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def main():
    parser = argparse.ArgumentParser(description="Merge the data.")
    parser.add_argument("--sniffed_data", required=True, help="Filepath to the sniffed UART traffic.")
    parser.add_argument("--emporia_csv", required=True, help="Filepath to the Emporia 1SEC CSV.")

    args = parser.parse_args()

    sniffed_data = read_file(args.sniffed_data)
    parsed_sniff = parse_sniffed_packet(sniffed_data)

    emporia_data = read_file(args.emporia_csv)
    parsed_emporia = parse_emporia(emporia_data)

    hex3_to_watts = defaultdict(list)
    result = find_nearest_after(parsed_sniff, parsed_emporia)
    for timestamp, packet, watts in result:
        hex3 = packet[90:96]
        hex3_to_watts[hex3].append((watts, packet))

    for hex3, watts in hex3_to_watts.items():
        print('Hex3:', hex3, 'Calculated W:', hex_to_decimal(hex3), 'Pairing:', watts)

if __name__ == "__main__":
    main()