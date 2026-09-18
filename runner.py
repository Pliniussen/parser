from parser import parse_csv, read_csv_file

print(parse_csv(read_csv_file("data/employees.ascii.csv")))
