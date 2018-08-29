

def write_to_csv_file(file_name, column_names, data):
    file = open(file_name + '.csv', 'w')

    # write header line:
    separator = ''
    for name in column_names:
        file.write(separator)
        file.write(name)
        separator = ','
    file.write('\n')

    # write actual data:
    for row in data:
        separator = ''
        for field in row:
            file.write(separator)
            file.write(field)
            separator = ','
        file.write('\n')
    file.close()