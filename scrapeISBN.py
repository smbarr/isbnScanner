import json
import requests

base_url = "https://openlibrary.org/"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0",
}

def scrapeISBN(isbn, return_detailed=False):
    bookurl = "%s/isbn/%d.json"%(base_url, isbn)
    bookpage = requests.get(bookurl, headers=headers)
    detailed_info = json.loads(bookpage.content.decode('utf-8'))
    authorurl = "%s/%s.json"%(base_url, detailed_info["authors"][0]["key"])
    authorpage = requests.get(authorurl, headers=headers)
    author = json.loads(authorpage.content.decode('utf-8'))["name"]
    info = {
        "author": author,
        "title": detailed_info["title"],
        "isbn": detailed_info["isbn_13"][0],
        "format": detailed_info["physical_format"]
    }
    if return_detailed:
        return detailed_info
    else:
        return info

if __name__ == "__main__":
    isbn = 9781558585362
    bookinfo = scrapeISBN(isbn)
    print(json.dumps(bookinfo, indent=2))
