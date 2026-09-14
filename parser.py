
def read_csv_file(filepath):
    with open(filepath, encoding="utf-8") as file:
        return file.read()

def parse_csv(text):
    lines = text.splitlines()
    headers = lines[0].split(",")

    data = []
    for line in lines[1:]:
        values = line.split(",")
        row = dict(zip(headers, values))
        data.append(row)

    return data

print(parse_csv(read_csv_file("data/employees.ascii.csv")))