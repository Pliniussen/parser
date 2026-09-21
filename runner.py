from parser import parse_csv, read_csv_file

try:
    print(parse_csv('"name","name"\n"Ada Lovelace","Engineer"\n'))
except ValueError as error:
    print(f"Error: {error}")
