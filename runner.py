from parser import parse_csv_json

try:
    print(parse_csv_json('"name","role"\n"Ada Lovelace","Engineer"\n'))
except ValueError as error:
    print(f"Error: {error}")
