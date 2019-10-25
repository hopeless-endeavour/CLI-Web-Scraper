import webbrowser
from contextlib import closing
import argparse

from requests import get
from requests.exceptions import RequestException
from bs4 import BeautifulSoup


def get_url(url, unit):
    """Gets relevantideas topic url."""

    new_url = ''
    topics = ['famille', 'cyber', 'benevolat', 'patrimonie', 'musique', 'cinema',
              'diversite', 'marginal', 'criminels', 'politique', 'manifestations', 'immigration']

    topics_url = ['1-famille-documents.html', '2-cyber-documents.html', '3-beacuteneacutevolat-documents.html',
                  '4-patrimoine-documents.html', '5-musique-documents.html', '6-cineacutema-documents.html',
                  '1-diversiteacute-documents.html', '2-marginal-documents.html', '3-criminels-documents.html',
                  '4-politique-documents.html', '5-manifestations-documents.html', '6-immigation-documents.html']

    for i in range(0, len(topics)):
        if unit == topics[i]:
            new_url = url + topics_url[i]
            break

    return new_url


def simple_get(url):
    """Attempts to get content of url using get and returns content if successful, else returns none."""

    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """Returns true if response is html."""
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def rideas_scrape(content):
    """Scrapes contents of revelantideas topic url to find linked articles and perform chosen option."""

    soup = BeautifulSoup(content, 'html.parser')
    elems = soup.find_all('a', class_='wsite-button wsite-button-small wsite-button-normal')
    links = []
    for i in range(len(elems)):
        link = elems[i].get("href")
        if 'http' not in link:  # doesn't add false href's
            pass
        else:
            links.append(link)

    return links


def frinfo_scrape(content):
    """Scrapes francetvinfo for articles with keyword"""

    soup = BeautifulSoup(content, 'html.parser')
    # elems = soup.find_all('a', href=True)
    elems = soup.select('.flowItem a[href]')
    links = []
    for i in range(len(elems)):
        link = elems[i].get("href")
        if 'http' not in link:  # doesn't add false href's
            link = "https://www.francetvinfo.fr" + elems[i].get("href")
        links.append(link)

    return links


def lemonde_scrape(content):
    """Scrapes lemonde.fr for articles with keyword"""

    soup = BeautifulSoup(content, 'html.parser')
    elems = soup.find_all('a', class_='teaser__link teaser__link--kicker', href=True)
    links = []
    for i in range(len(elems)):
        link = elems[i].get("href")
        if 'http' not in link:  # doesn't add false href's
            pass
        else:
            links.append(link)

    return links


def figaro_scrape(content):
    """Scrapes lefigaro.fr for articles with keyword."""

    soup = BeautifulSoup(content, 'html.parser')
    elems = soup.select(".fig-profil-headline a[href]")
    links = []
    for i in range(len(elems)):
        link = elems[i].get("href")
        if 'http' not in link:  # doesn't add false href's
            pass
        else:
            links.append(link)

    return links


def open_links(lists, num):
    """Opens chosen number of top links."""

    if num is not None:
        for i in range(num):
            webbrowser.open(lists[i])


def save_links(lists, filename):
    """Save links to specified file."""

    if filename is not None:
        f = open(filename, 'w')
        for i in range(len(lists)):
            f.write(lists[i] + '\n')
        f.close()


def main():
    # options
    ap = argparse.ArgumentParser(prog='scraper', description='French article web scraper.')
    ap.add_argument('-t', '--topic', help="choose a topic to scrape for",
                    choices=['famille', 'cyber', 'benevolat', 'patrimonie', 'musique', 'cinema', 'diversite',
                             'marginal', 'criminels', 'politique', 'manifestations', 'immigration'])
    ap.add_argument('-o', '--ofile', help='output resulting links to chosen file')
    ap.add_argument('-n', '--number', choices=range(1, 11), help='choose number of top links to open', type=int)
    # ap.add_argument('-dp', '--displayprev', help='display preview of articles')
    ap.add_argument('-k', '--keyword', nargs='*', help='keyword to search for on domain search page')
    ap.add_argument('-d', '--domain', default='https://relevantideas.weebly.com/',
                    choices=['relevantideas', 'francetvinfo', 'lemonde', 'lefigaro'],
                    help='domain to scrape')
    # domains to add if bothered: https://www.lesechos.fr, https://www.lexpress.fr, https://www.humanite.fr/,
    # https://www.liberation.fr/, https://www.lindependant.fr/,
    # https://www.monde-diplomatique.fr/, https://www.20minutes.fr/
    ap.add_argument('-s', '--searchpage', help='open search page of domain', action='store_true')

    args = ap.parse_args()

    topic = args.topic
    ofile = args.ofile
    number = args.number
    domain = args.domain
    keyword = args.keyword
    open_search = args.searchpage

    if keyword is not None:
        search = keyword
    else:
        search = topic

    if type(search) is list:
        word = search[0]
        for i in range(1, len(search)):
            word += '+' + search[i]
        search = word

    if domain == 'francetvinfo':
        path = "https://www.francetvinfo.fr/recherche/?request=" + search
        raw_html = simple_get(path)
        urls = frinfo_scrape(raw_html)
    elif domain == 'lemonde':
        path = "https://www.lemonde.fr/recherche/?search_keywords=" + search \
              + "&start_at=19%2F12%2F1944&end_at=21%2F10%2F2019&search_sort=date_desc"
        raw_html = simple_get(path)
        urls = lemonde_scrape(raw_html)
    elif domain == 'lefigaro':
        path = "https://recherche.lefigaro.fr/recherche/" + search
        raw_html = simple_get(path)
        urls = figaro_scrape(raw_html)
    else:
        path = get_url(domain, topic)
        raw_html = simple_get(path)
        urls = rideas_scrape(raw_html)

    open_links(urls, number)
    save_links(urls, ofile)
    if open_search:
        webbrowser.open(path)


main()

