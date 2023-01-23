import requests
from requests.exceptions import RequestException
import send_message
from bs4 import BeautifulSoup
import os
from bot_mongo import LinkCheckerDB
import lxml
from dotenv import load_dotenv
load_dotenv()

urls=[]

mongo_work = LinkCheckerDB()

def check_url(urls):
    result = []
    for i_url in urls:
        try:
            resp = requests.get(i_url)
            status = str(resp.status_code)
            print('Info:', i_url, resp.status_code)
            result.append({'url': i_url, 'status': status})
            if resp.status_code != 200:
                send_message.send_message(i_url, status)
        except RequestException as e:
            print('Error:', i_url, e)
            send_message.send_message(i_url, str(e))
    mongo_work.log_check(result)
    result = []
    urls= []

def create_links(sitemaps):
    for url in sitemaps:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, features="html")
        loc_tags = soup.find_all('loc') 
        links = [tag.text for tag in loc_tags]
        for link in links:
            urls.append(link)
    check_url(urls)
    
def create_sitemap(event, context):
    url = os.environ['SITEMAP_URI']
    page = requests.get(url)
    soup = BeautifulSoup(page.content, features="html")
    loc_tags = soup.find_all('loc') 
    sitemaps = [tag.text for tag in loc_tags]   
    create_links(sitemaps)
 


