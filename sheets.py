import os
import json

import gspread
from google.oauth2.service_account import Credentials

google_sheet_credentials = os.getenv('GOOGLE_SHEET_CREDENTIALS')
credentials_dict = json.loads(google_sheet_credentials)


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
gc = gspread.authorize(credentials)

service_account_email = credentials.service_account_email

# print(credentials, service_account_email)

def create_sheet(sheet_name, worksheet_name):
    spreadsheet = gc.create(sheet_name)
    spreadsheet.share(service_account_email, perm_type='user', role='writer')
    worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=100, cols=20)
    return spreadsheet

def open_sheet(sheet_name):
    return gc.open(sheet_name)

def open_worksheet(sheet, worksheet_name):
    return sheet.worksheet(worksheet_name)

def add_data_as_list(worksheet, data, link):
    worksheet.append_row(data)
    print(f"🟢 > Adding to list: {link}")

def read_sheet(worksheet, range:str):
    # data = sheet.values_get(range)
    data = worksheet.get(range)
    return data

def check_link_exists(link:str, data:list, column_index):
    for data_row in data:
        if link == data_row[column_index]:
            return True

    return False
