#!/usr/bin/python

import argparse
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import re
import requests
import unicodedata


BUS_STOPS = {
    'asanacny-podnik': 63,
    'autobusove-nastupiste': 207,
    'bagarova': 69,
    'banova-colnica': 1,
    'banovska-cesta': 140,
    'bernolakova': 230,
    'bratislavska': 21,
    'brodnanska': 10,
    'brodno': 11,
    'budatinska': 100,
    'bytcianska': 43,
    'bytcianska-sts': 44,
    'bytcica': 160,
    'carrefour': 119,
    'centralna': 76,
    'cestarska': 22,
    'chlmecka': 45,
    'cintorinska': 84,
    'dolna': 14,
    'dolna-trnovska': 85,
    'farebna': 164,
    'fatranska': 92,
    'furdekova': 67,
    'halkova': 23,
    'hlinska': 50,
    'holleho': 24,
    'horecka': 123,
    'horna-trnovska': 86,
    'hricovska': 81,
    'hurbanova': 25,
    'hviezdoslavova': 300,
    'hyza': 64,
    'internatna': 162,
    'jasenova': 77,
    'jedlova': 2,
    'k-cintorinu': 3,
    'kamenna-domace-potreby': 56,
    'kamenna-kovosrot': 57,
    'kamenna-obchodne-centrum': 60,
    'kamenna-prius': 58,
    'kia-site': 200,
    'koliba': 12,
    'komenskeho': 27,
    'kortinska': 103,
    'kosicka-tesco-hyp-': 28,
    'kragujevska': 29,
    'kulturny-dom': 18,
    'kvacalova-dpmz': 112,
    'kysucka': 30,
    'labutia': 142,
    'letna': 15,
    'limbova': 78,
    'magocovska': 87,
    'mateja-bela': 120,
    'matice-slovenskej': 93,
    'mobis': 202,
    'mostna': 51,
    'motel-sibenice': 70,
    'na-chotari': 113,
    'na-horevazi-tesco-hyper-': 31,
    'na-lany': 16,
    'na-stanicu': 19,
    'na-stranik': 109,
    'namestie-hrdinov': 17,
    'namestie-sv-j-bosca': 4,
    'obchodna': 94,
    'oceliarska': 68,
    'oslobodenia': 5,
    'ovocinarska': 88,
    'pazite': 20,
    'pietna-krematorium': 114,
    'pod-hajom': 126,
    'pod-kozinom': 104,
    'pod-vinicou': 116,
    'pod-zahradkou': 105,
    'policia': 33,
    'polna': 52,
    'postova': 95,
    'potoky': 89,
    'predmestska': 34,
    'pri-celulozke': 47,
    'pri-kysuci': 46,
    'priehrada': 106,
    'priehradna': 82,
    'prielozna': 83,
    'priemyselna': 35,
    'pripojna': 102,
    'rajecka-elv': 53,
    'rajecka-mliekarne': 62,
    'rajecka-stavomontaze': 54,
    'rakove': 90,
    'razcestie-hricov': 107,
    'razusova': 36,
    'rosinky': 71,
    'rosinska-plem-podnik': 73,
    'rosinska-vuvt': 72,
    'rudnayova': 6,
    'rybne-namestie': 66,
    'salas': 110,
    'salezianska': 55,
    'slnecne-namestie': 122,
    'smrekova': 79,
    'spanyolova-nemocnica': 37,
    'stodolova': 49,
    'sv-cyrila-a-metoda': 96,
    'sibenice-stk': 74,
    'stefanikovo-namestie': 38,
    'tajovskeho': 7,
    'tulipanova': 8,
    'udolna': 101,
    'univerzitna': 501,
    'varin-zel-stanica': 290,
    'velka-okruzna': 40,
    'velka-okruzna-aupark': 39,
    'vysokoskolakov-plavaren': 9,
    'vzdelavacie-centrum': 289,
    'zabrezna': 13,
    'zastranie-stara-dedina': 115,
    'zavodska': 41,
    'zavodskeho': 124,
    'zvolenska': 75,
    'zeleznicna-stanica': 42,
    'zilinska-lehota': 159,
    'zilinska-univerzita': 91,
    'zitna': 125
}


def load_soup(response):
    return BeautifulSoup(response.content, 'html.parser')


def find_cells(row_soup):
    return [td.get_text().strip() for td in row_soup.find_all('td')]


def prepare_params(start, end, date, time):
    return dict(
        odkial=start,
        kam=end,
        datum=date,
        cas=time,
        odchod='1',
        prestup='2',
        x='52',
        y='14'
    )


def print_all_bus_stops(soup):
    for o in soup.find('select', {'class':'s1'}).find_all('option'):
        t = o.get_text().strip().lower()
        t = unicodedata.normalize('NFKD', t)
        t = t.replace(' ', '-').replace(',', '-').replace('.', '-')
        t = t.replace('--', '-')
        t = t.replace('--', '-')
        t = re.sub('[^A-Za-z0-9_-]+', '', t)
        print '\'' + t + '\': ' +  o['value'] + ','


def run(args):
    start = BUS_STOPS[args.start]
    end = BUS_STOPS[args.end]

    date = args.date
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    time = args.time
    if not time:
        time = datetime.now().strftime('%H:%M')

    print args.start + '(' + str(start) + ')' , args.end + '(' + str(end) + ')', date, time

    params = prepare_params(start, end, date, time)
    response = requests.post('http://www.dpmz.sk/vyhladavanie/', data=params)

    if response.status_code != 200:
        print 'FAILED'
        sys.exit(1)

    soup = load_soup(response)
    print soup.title.string

    table = soup.find(id='column_2').find('table')
    if table:
        rows = table.find_all('tr')
        for row in rows:
            print ' | '.join(find_cells(row))
    else:
        print 'No buses found'


#
# Examples:
#   python dpmz.py -s limbova -e policia
#   python dpmz.py -s limbova -e policia -t 6:00
#   python dpmz.py -s limbova -e policia -d 2017-01-31 -t 6:00
#
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', required=True)
    parser.add_argument('-e', '--end', required=True)
    parser.add_argument('-d', '--date', required=False)
    parser.add_argument('-t', '--time', required=False)
    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
