#!/usr/bin/env python3
"""FEB public rankings first-page CSV importer. Not a complete league crawler.
Usage: python feb_scouting_importer_v4.py --league tercera-feb --output rankings.csv
Dependencies: pip install requests beautifulsoup4
Review website terms and access permissions before automated use.
"""
import argparse,csv,re,sys
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
HEADERS=['rank','player','team','games','minutes','points','2pm','2pa','2pct','3pm','3pa','3pct','ftm','fta','ftpct','oreb','dreb','reb','ast','stl','blk','turnovers','fouls','efficiency','plus_minus','source_url']
def parse_page(html, url):
    soup=BeautifulSoup(html,'html.parser')
    output=[]
    for tr in soup.select('tr'):
        cells=tr.find_all(['td'],recursive=False)
        if len(cells)<25: continue
        values=[re.sub(r'\s+',' ',c.get_text(' ',strip=True)).strip() for c in cells]
        if not values[0].isdigit(): continue
        # Position + 24 basketball columns; preserve raw tokens, including em dashes.
        if len(values)>25: values=values[:25]
        row=dict(zip(HEADERS[:-1],values));row['source_url']=url
        a=cells[1].find('a',href=True)
        if a:row['player_url']=urljoin(url,a['href'])
        output.append(row)
    return output

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--league',choices=['primera-feb','segunda-feb','tercera-feb'],default='tercera-feb')
    p.add_argument('--output',default='feb_rankings_page1.csv')
    a=p.parse_args()
    url=f'https://beta.competiciones.feb.es/{a.league}/rankings'
    try:
        r=requests.get(url,timeout=25,headers={'User-Agent':'ScoutingResearch/1.0 (public data validation)'})
        r.raise_for_status()
        results=parse_page(r.text,url)
    except requests.RequestException as e:
        print('NETWORK ERROR: '+str(e),file=sys.stderr);sys.exit(2)
    if not results:
        print('NO ROWS: site may render via JS or use a different table; inspect permitted API/export first.',file=sys.stderr)
        sys.exit(3)
    keys=HEADERS+['player_url']
    with open(a.output,'w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(results)
    print(f'Exported {len(results)} visible rows from {url} to {a.output}. Not a complete league roster.')
if __name__=='__main__':main()
