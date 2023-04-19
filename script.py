import gspread
import os
from datetime import date
from dotenv import load_dotenv
import requests
load_dotenv()

#Connect to google service account
service_acct = gspread.service_account(filename="google_service_account.json")
#Connect to a google sheet
gsheet = service_acct.open(os.getenv("GOOGLE_SHEETS_NAME"))
worksheet = gsheet.worksheet("Players")

#Script Logic to update Google Sheets with NHL Players Stats API
#API call to gather new values for Google sheets (get goals for all players currently in google sheets)
worksheet_data = worksheet.get_all_records()
for player in worksheet_data:
    player_id = player["PlayerId"]

    #make get request to get players total goals for 2022/2023 playoffs
    res = requests.get(f"https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats?stats=statsSingleSeasonPlayoffs&season=20222023")
    playerStats = res.json()["stats"][0]["splits"]
    if (len(playerStats) > 0):
        goals = playerStats[0]["stat"]["goals"]
        player["Goals"] = goals

#update googlesheet information new values (can probably use excel vlookup logic to update data instead of using this number string iterpolation logic)
for num in range(len(worksheet_data)):
    cell = f"C{num+2}"
    new_val = worksheet_data[num]["Goals"]
    worksheet.update(cell, new_val)
today = date.today()
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