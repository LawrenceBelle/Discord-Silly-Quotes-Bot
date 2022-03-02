import requests
from bs4 import BeautifulSoup as bs
import random
from exceptions import TemplateError, QuoteError
from retry import retry


class QuozioImageCollector:
    def __init__(self, template_file, quote, author):
        self.url = 'https://quozio.com/api/v1/quotes'
        self.quote = quote
        self.author = author

        self.timeout_tol = 10
        self.valid_templ_file = template_file

        self.format_payload()

        self.headers = {
            'authority': 'quozio.com',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json;charset=UTF-8',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://quozio.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://quozio.com/',
            'accept-language': 'en-GB,en;q=0.9',
            'cookie': '_ga=GA1.2.880283838.1642709613; _gid=GA1.2.1615379592.1642709613; _gat=1',
        }

        try:
            self.response = self.post_request(self.url, data=self.payload, headers=self.headers, timeout=self.timeout_tol)

        except Exception as e:
            print(e)
            raise QuoteError("Could not send quote and author to Quozio.com")

        self.id = self.response.json()['quoteId']
        self.slug = self.response.json()['slug']

        self.session = requests.Session()   # session used for all get requests 

    @retry
    def get_request(self, url, **kwargs):
        r = self.session.get(url, **kwargs)
        return r

    @retry
    def post_request(self, url, **kwargs):
        r = requests.post(url, **kwargs)
        return r

    # Puts the quote and author into the payload for the original post request
    def format_payload(self):
        dummy = ')T$GWhwY'      # String that wouldn't appear in any inputted quotes or authors

        self.quote = self.quote.replace("'", dummy)
        self.author = self.author.replace("'", dummy)

        self.payload = {"quote" : self.quote, "author" : self.author}

        self.payload = str(self.payload)
        self.payload = self.payload.replace("'", '"')
        self.payload = self.payload.replace(dummy, "\'")

    def format_response(self):
        # self.template_id is a value of at least 1000, up to 1357 but not every value inbetween

        self.quote_url = f"https://quozio.com/quote/{self.id}/{self.template_id}/{self.slug}"
        self.edit_url = f"https://quozio.com/quote/{self.id}/edit"

    # Finds the image in the webpage
    def get_img_link(self):
        try:
            r = self.get_request(self.quote_url, timeout=self.timeout_tol)
            self.soup = bs(r.content, features='lxml')
            image = self.soup.find("img", attrs={"id":"quote-view-image"})

            return image["src"]
        except Exception as e:
            print(e)
            raise QuoteError('Could not connect to templated quote page')

    # Looks through urls with different template IDs to find which values return valid images
    def list_tmpl_ids(self):
        # clear file
        id_file = open(self.valid_templ_file, 'w')
        id_file.close()

        try:
            for t_id in range(1000, 1358): # Values found from looking at webpage source
                self.template_id = t_id
                self.format_response()

                image_url = self.get_img_link()
                image_r = self.get_request(image_url, timeout=self.timeout_tol)

                if image_r.status_code == requests.codes.ok:
                    with open(self.valid_templ_file, 'a') as f:
                        f.write(f"{self.template_id}\n")
                    print(f"{self.template_id} is a valid Id")
                else:
                    print(f"{self.template_id} is not a valid Id")

        except Exception as e:
            print(e)
            raise QuoteError("Could not fetch all available templates")

    def get_valid_id(self):
        try:
            with open(self.valid_templ_file, 'r') as f:
                valid_ids = f.readlines()
                if not valid_ids:
                    raise TemplateError
            return int(random.choice(valid_ids))

        except Exception as e:
            print(e)
            raise TemplateError

    def collect(self, file_name):
        self.template_id = self.get_valid_id()
        self.format_response()

        image_url = self.get_img_link()

        image_r = self.get_request(image_url, timeout=self.timeout_tol)
        # Maybe make image file name a parameter
        with open(file_name, 'wb') as f:
            f.write(image_r.content)


if __name__ == '__main__':
    q = QuozioImageCollector("Quote", "-Author")
    q.collect('quote_image.jpeg')
    # q.list_tmpl_ids()