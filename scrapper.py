import requests
from requests_html import HTML
import boto3
import re
import os
from datetime import datetime

import json

client = boto3.client('ssm')
dynamodb = boto3.client('dynamodb')


def get_html(url):
    r = requests.get(url)
    if r.status_code == 200:
        html_text = r.text
        return html_text
    return None


def parse(data_object):
    # get the html data
    html_data = HTML(html=data_object)

    # get the table with contain the data
    css_class = ".result-count"
    result_count = html_data.find(css_class)
    total_forclosures = (re.findall('\d+', result_count[0].text))[0]
    print(total_forclosures)
    return total_forclosures


def get_secret(key):
    resp = client.get_parameter(
        Name=key,
        WithDecryption=True
    )
    return resp['Parameter']['Value']


def total(url):
    html_text = get_html(url)
    if html_text is None:
        print(f'URL request failed: {url}')
        return None
    return parse(html_text)


def handler(event, context):
    # scrap throw proxycrawl to avoid recaptcha

    url_miami_dade = f"https://api.proxycrawl.com/?token={get_secret('PROXY_CRAWL_TOKEN')}&url=https://www.zillow.com/miami-dade-county-fl/foreclosures/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22Miami-Dade%20County%2C%20FL%22%2C%22mapBounds%22%3A%7B%22west%22%3A-90.99998347851562%2C%22east%22%3A-69.73045222851562%2C%22south%22%3A18.76431887290778%2C%22north%22%3A33.7914437141665%7D%2C%22mapZoom%22%3A6%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A2964%2C%22regionType%22%3A4%7D%5D%2C%22filterState%22%3A%7B%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22pf%22%3A%7B%22value%22%3Afalse%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22isMapVisible%22%3Atrue%7D"
    url_FL = f"https://api.proxycrawl.com/?token={get_secret('PROXY_CRAWL_TOKEN')}&url=https://www.zillow.com/homes/FL_rb/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22FL%22%2C%22mapBounds%22%3A%7B%22west%22%3A-94.9392435546875%2C%22east%22%3A-73.3840677734375%2C%22south%22%3A14.904433158518971%2C%22north%22%3A37.65076387653836%7D%2C%22isMapVisible%22%3Atrue%2C%22mapZoom%22%3A6%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A14%2C%22regionType%22%3A2%7D%5D%2C%22filterState%22%3A%7B%22pmf%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22pf%22%3A%7B%22value%22%3Afalse%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D"

    total_miami_dade_forclosures = total(url_miami_dade)
    total_florida_forclosures = total(url_FL)

    dynamodb.put_item(TableName=os.environ['tableName'], Item={
        "id": {'S': datetime.now().strftime("%m-%d-%Y, %H:%M:%S")},
        "fl_forclosures": {'S': total_florida_forclosures},
        "md_forclosures": {'S': total_miami_dade_forclosures}
    })

    print(f'{total_miami_dade_forclosures} Miami Dade forclosures')
    print(f'{total_florida_forclosures} Miami Dade forclosures')
