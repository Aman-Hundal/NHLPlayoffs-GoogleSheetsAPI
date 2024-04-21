import gspread
import os
import datetime
from dotenv import load_dotenv
import requests
import json

load_dotenv()

#create env variables from google_servce_account.json
# data = json.load(open('google_service_account.json'))
# f = open(".envjson", "x")
# for key, value in data.items():
#     f.write(f"{key.upper()}={value}\n")
print("Test")
#create gsheet credentials dict
def create_keyfile_dict():
    variables_keys = {
        "type": os.environ["TYPE"],
        "project_id": os.environ["PROJECT_ID"],
        "private_key_id": os.environ["PRIVATE_KEY_ID"],
        "private_key": os.environ["PRIVATE_KEY"],
        "client_email": os.environ["CLIENT_EMAIL"],
        "client_id": os.environ["CLIENT_ID"],
        "auth_uri": os.environ["AUTH_URI"],
        "token_uri": os.environ["TOKEN_URI"],
        "auth_provider_x509_cert_url": os.environ["AUTH_PROVIDER_X509_CERT_URL"],
        "client_x509_cert_url": os.environ["CLIENT_X509_CERT_URL"]
    }
    return variables_keys
credentials = create_keyfile_dict()

#Connect to google service account
service_acct = gspread.service_account_from_dict(credentials)
#Connect to a google sheet
gsheet = service_acct.open(os.environ["GOOGLE_SHEETS_NAME"])
worksheet = gsheet.worksheet("Players")
total_worksheet = gsheet.worksheet("Total")

#Script Logic to update Google Sheets with NHL Players Stats API
#API call to gather new values for Google sheets (get goals for all players currently in google sheets)
worksheet_data = worksheet.get_all_records()
# print("DATA", worksheet_data)
for player in worksheet_data:
    player_id = player["PlayerId"]
    #make get request to get players total goals for 2022/2023 playoffs
    res = requests.get(f"https://api-web.nhle.com/v1/player/{player_id}/landing")
    player_stats = res.json()["featuredStats"]
    if ("playoffs" in player_stats):
        player_stats_playoffs = player_stats["playoffs"]
        player_goals = player_stats_playoffs["subSeason"]["goals"]
        player["Goals"] = player_goals

#update googlesheet information new values (WIP add VLOOKUP or INDEX/MATCH logic to find and update cells with new data)
for num in range(len(worksheet_data)):
    cell = f"C{num+2}"
    new_val = worksheet_data[num]["Goals"]
    worksheet.update(cell, new_val)

#provide audit date for last update of sheet
today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
total_worksheet.update("A9", today)
total_worksheet.sort((2, "des"))
print("Today's date:", today)

# BASIC GOOGLE SHEET API REVIEW
#READING METHODS
# #.acell method to get the value of a certain cell (A9)
# print(worksheet.acell("A9").value)

# #.cell method to get the value of 3 rows down 2 columns over
# print(worksheet.cell(3,3).value)

# #.get method to get more than one row (pass in a range of cells). You return a list of lists
# print(worksheet.get("A2:C10"))

# #.get_all_records method that gets all the data in your sheet. You return a list of dicts (for each dict, keys are headers, values are the cell values)
# print(worksheet.get_all_records())

# #.get_all_values method that gets all the data in your sheet. You return a list of lists (same data as above, but list of lists)
# print(worksheet.get_all_values())

#WRITING METHODS
# #Update a single cell with .update method
# worksheet.update("A2", "Aman")

# #Update multiple rows (same idea as using the rectangle visualtions on line 19 ). This will update A2 and B2 to Aman, Test and A3 and B3 to Hundal and HELLO respectively
# worksheet.update("A2:B3", [["Aman", "TEST"], ["Hundal", "HELLO"]])

#Update method with using formulas. In this case we will pass in an excel formula and write the result to cell F3. Raw=False is needed and valuates the formula passed in
# worksheet.update("F2", "=UPPER(A2)", raw=False)

# #Deleting a particular row (ie. row 10)
# worksheet.delete_rows(10)