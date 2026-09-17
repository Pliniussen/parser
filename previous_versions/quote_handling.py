from parser import read_csv_file

def parse_csv(text):
    rows = []
    row = []
    field = []
    inside_quotes = False
    i = 0

    while i < len(text):
        char = text[i]

        if char == '"':
            if inside_quotes and i + 1 < len(text) and text[i + 1] == '"':
                field.append('"')
                i += 1
            else:
                inside_quotes = not inside_quotes

        elif char == "," and not inside_quotes:
            row.append("".join(field))
            field = []

        elif char in "\r\n" and not inside_quotes:
            if char == "\r" and i + 1 < len(text) and text[i + 1] == "\n":
                i += 1

            row.append("".join(field))
            rows.append(row)
            row = []
            field = []

        else:
            field.append(char)

        i += 1

    if field or row:
        row.append("".join(field))
        rows.append(row)

    headers = rows[0]
    return [dict(zip(headers, values)) for values in rows[1:]]

parsed_data = parse_csv('"name","email","department","role","salary","start_date","office"\n"Marcus ""GOAT"" Chen","marcus.chen@example.com","Engineering","Senior Software Engineer, Backend","155000","2019-03-15","San Francisco"')
print(parsed_data)