# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 17:06:50 2019

@author: yuanq
"""

# Protocol for robots.txt can be found at http://www.robotstxt.org
# Sitemap standard is defined at http://www.sitemaps.org/protocol.html

# Road Map
# 1. check robots.txt
# 2. check sitemap
# 3. estimating size of website
#    - search for 'site:example.webscraping.com'; number of results will 
#      provide rought indication on size of website
#    - can try to use google api to automate this process
#      (https://developers.google.com/api-client-library/python/start/get_started)
# 4. get web technologies to determine scraping methods
# 5. get web owner to determine if domain is known to block crawlers
# 6. download web pages
# 7. crawl web pages

#import requests
#import urllib.request
#import time
#from bs4 import BeautifulSoup
#import re
#
#url = 'http://web.mta.info/developers/turnstile.html'
#response = requests.get(url)
#
#soup = BeautifulSoup(response.text, 'html.parser')
#results = soup.findAll('a')
#lst_results = list(results)
#
#for i in range(len(lst_results)):
#    
#    if re.findall('turnstile_[0-9]+.txt',str(lst_results[i])):
#        counter = i
#        break
#
#print(counter)

import builtwith as bw
import whois
import urllib3
from bs4 import BeautifulSoup
import re

class WebScrape():
    def __init__(self, str_url, 
                 bln_scrape_sitemap = False, 
                 bln_verbose = False):
        self.__str_url = str_url
        self.__bln_verbose = bln_verbose
    
    def __del__(self):
        pass
    
    def __len__(self):
        pass
    
    def __repr__(self):
        pass
    
    def get_web_tech(self):        
        return bw.parse(self.__str_url)

    def get_web_owner(self):
        return whois.whois(self.__str_url)    
    
    def get_sitemap_urls(self, str_sitemap_url):
        sitemap = self.get_web_page(str_sitemap_url)
        print(sitemap)
        links = re.findall('<loc>(.*?)</loc>', sitemap)
        return links
    
    def get_web_page(self, 
                     str_user_agent = 'wswp',
                     int_retries = 5):
        
    # https://stackoverflow.com/questions/630453/put-vs-post-in-rest
    
        if self.__bln_verbose:
            print('Downloading: ' + self.__str_url)
        
        headers = {'User-agent': str_user_agent}
        http = urllib3.PoolManager()
        response = http.request('GET', self.__str_url, headers = headers)            
        print(response.status)
        if response.status == 200:
            html = response.data.decode('utf-8') 
        else:
            if response.status >= 500 and response.status < 600:
                response = http.request('GET', self.__str_url, retries=int_retries)            
                if response.status != 200:
                    if self.__bln_verbose:
                        print('Download Error: ' + str(response.status))
                    html = None
                else:
                    html = response.data.decode('utf-8')
            else:
                if self.__bln_verbose:
                        print('Download Error: ' + str(response.status))
                html = None
        return html
        

if __name__ == '__main__':

    scrape = WebScrape('https://www.careers.gov.sg')
    print(scrape.get_web_tech())
    #scrape = WebScrape('http://www.bloomberg.com/')
    #print(scrape.get_web_tech())
    #print(scrape.get_web_page())
    
    #links = scrape.get_sitemap_urls('https://www.bloomberg.com/feeds/bbiz/sitemap_index.xml')
    #print(links)