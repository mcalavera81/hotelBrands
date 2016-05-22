import  requests, logging, bs4, time


def get_contents(url):
    if url:
        try:
            if not url.startswith('http'):
                url = 'http://'+url
            response = requests.get(url)
        except Exception as exc:
            logging.warning("%s:%s"%(url,exc))
            return None
        else:
            return response


def get_url_soup(url):
    if url:
        try:
            time.sleep(0.5)
            response = requests.get(url.replace('#!/',''),  allow_redirects=False)
            if response.status_code == 200:
                return bs4.BeautifulSoup(response.text, "html.parser")
        except Exception as exc:
            logging.warning("%s : %s" % (url, exc))
            return None
