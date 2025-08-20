import pandas as pd
import json
import sys

def find_first_non_empty(row, prefixes):
    for prefix in prefixes:
        if prefix in row and pd.notna(row[prefix]) and str(row[prefix]).strip():
            return str(row[prefix]).strip()
    return ""

def convert_to_json(input_file, output_file, file_type='excel'):
    """
    Reads contact data from an Excel or CSV file and saves it in JSON format.
    """
    try:
        if file_type == 'csv':
            df = pd.read_csv(input_file)
        else:
            df = pd.read_excel(input_file, header=None)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found. Make sure the file exists.")
        return

    data_list = []

    if file_type == 'csv':
        # Find all columns whose names start with 'email' and 'phone'
        email_columns = [col for col in df.columns if str(col).startswith('email')]
        phone_columns = [col for col in df.columns if str(col).startswith('phone')]

        for _, row in df.iterrows():
            email = find_first_non_empty(row, email_columns)
            phone = find_first_non_empty(row, phone_columns)
            first_name = str(row['fn']) if 'fn' in row and pd.notna(row['fn']) else ""
            last_name = str(row['ln']) if 'ln' in row and pd.notna(row['ln']) else ""
            gender = str(row['gen']).lower() if 'gen' in row and pd.notna(row['gen']) else "male"

            record = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "message": "",
                "gender": gender if gender in ['male', 'female'] else "male"
            }

            data_list.append(record)

    else:  # Excel file (without headers)
        for _, row in df.iterrows():
            phone = str(row[1]) if pd.notna(row[1]) else ""
            email = str(row[2]) if pd.notna(row[2]) else ""

            record = {
                "first_name": "",
                "last_name": "",
                "email": email,
                "phone": phone,
                "message": "",
                "gender": "male"
            }

            data_list.append(record)

    # Save the data to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)

    print(f"Data was successfully saved to file '{output_file}'.")


# --- Command-line argument handling ---
if __name__ == '__main__':
    input_file = 'data/db.xlsx'
    output_file = 'clients.json'
    file_type = 'excel'

    if '-csv' in sys.argv:
        file_type = 'csv'
        input_file = 'data/db.csv'  # You can change this path as needed

    convert_to_json(input_file, output_file, file_type)
