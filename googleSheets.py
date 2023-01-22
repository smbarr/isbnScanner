from __future__ import print_function

import sys
import os.path
import inspect
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets'
]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1x-GdRumb0zFBbZz6AZLbRmnBNQcWieJD9-bsjtEZ0zI'

def getCredentials(updateToken=False):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    if os.path.exists('/home/sbarr/.credentials/token.json'):
        creds = Credentials.from_authorized_user_file('/home/sbarr/.credentials/token.json', SCOPES)
    if not creds or not creds.valid or updateToken:
        if creds and creds.expired and creds.refresh_token and not updateToken:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/home/sbarr/.credentials/client_secret_841061229898-vaii159sgjmuouj9mc596991n6sqes65.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        """
        This can cause an error if the token expires. It should be deleted on an exception
        """
        with open('/home/sbarr/.credentials/token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def updateRemote(creds, data):
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    myRange = "Sheet1"

    try:
        """
        Erase table
        """
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=myRange).execute()
        values = result.get('values', [])
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID, 
            range=myRange, 
            valueInputOption="USER_ENTERED", 
            body={'values': [["", "", ""] for n in range(len(values))]}
        ).execute()
    except:
        return False
    """
    Write new values
    """
    body = {
        'values': data
    }
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID, 
        range=myRange, 
        valueInputOption="USER_ENTERED", 
        body=body
    ).execute()

    return True

def updateSheet():
    df = pd.read_csv("books.csv").sort_values(by="Title")
    df.fillna("", inplace=True)
    data = [["Author", "Title", "Format"]]
    for a, t, f in zip(df["Author"], df["Title"], df["Format"]):
        data.append([a,t,f])

    creds = getCredentials()
    success = updateRemote(creds, data)
    if not success:
        creds = getCredentials(updateToken=True)
        success = updateRemote(creds, data)
        if not success:
            print("Error updating google sheet")
            #print(err)

if __name__ == "__main__":
    updateSheet()
