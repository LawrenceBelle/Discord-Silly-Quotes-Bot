import requests
import json
import random
from exceptions import AuthorError, QuoteError


# Retreives quote from api
def get_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=5)
        json_data = json.loads(response.text)
        quote = json_data[0]['q']
        return quote

    except Exception as e:
        print(e)
        raise QuoteError("Could not connect to quote API")


# Selects random name from author names text file
def get_author(names_file):
    try:
        with open (names_file, 'r') as file:
            names = file.readlines()
            if not names:
                raise AuthorError("Author file empty")
            author = random.choice(names)
        return author

    except Exception as e:
        print(e)
        raise AuthorError("No author file in directory")
