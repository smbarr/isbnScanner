import sys
import json
import requests
import select
import pandas as pd
from googleSheets import updateSheet

base_url = "https://openlibrary.org/"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0",
}

def scrapeISBN(isbn, return_detailed=False):
    bookurl = "%s/isbn/%d.json"%(base_url, isbn)
    bookpage = requests.get(bookurl, headers=headers)
    detailed_info = json.loads(bookpage.content.decode('utf-8'))
    if "authors" in detailed_info:
        authorurl = "%s/%s.json"%(base_url, detailed_info["authors"][0]["key"])
        authorpage = requests.get(authorurl, headers=headers)
        author = json.loads(authorpage.content.decode('utf-8'))["name"]
    else:
        author = "None"
    if "physical_format" in detailed_info:
        form = detailed_info["physical_format"]
    else:
        form = ""
    info = {
        "Author": author,
        "Title": detailed_info["title"],
        "Format": form
    }
    if return_detailed:
        return info, detailed_info
    else:
        return info

if __name__ == "__main__":
    """
    Read the database containing the books already scanned
    """
    books = pd.read_csv("books.csv", index_col=0)

    while True:
        res = input()
        #try:
        """
        Get ISBN from stdin
        """
        isbn = int(res)
        bookinfo, detailed_info = scrapeISBN(isbn, return_detailed=True)
        print("%s by %s"%(bookinfo["Title"], bookinfo["Author"]))

        """
        Check if book is already stored, if not append it to database
        """
        if not isbn in books.index:
            df = pd.DataFrame(index=[isbn], data=bookinfo)
            books = pd.concat([books, df])
            books.fillna("", inplace=True)
            books.to_csv("books.csv")
            updateSheet()

        """
        Save detailed info to a separate json file
        """
        with open("bookdata/%d.json"%(isbn), "w") as f:
            f.write(json.dumps(detailed_info, indent=2))
        #except:
        #    print("Error reading: %s"%(res))
