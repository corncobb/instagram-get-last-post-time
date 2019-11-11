#!/usr/bin/python3
# -*- coding: utf-8 -*-
from random import choice
import json
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from datetime import datetime
 
_user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
]
 
 
class InstagramScraper:
 
    def __init__(self, user_agents=None, proxy=None):
        self.user_agents = user_agents
        self.proxy = proxy
 
    def __random_agent(self):
        if self.user_agents and isinstance(self.user_agents, list):
            return choice(self.user_agents)
        return choice(_user_agents)
 
    def __request_url(self, url):
        try:
            response = requests.get(url, headers={'User-Agent': self.__random_agent()}, proxies={'http': self.proxy,
                                                                                                 'https': self.proxy})
            response.raise_for_status()
        except requests.HTTPError:
            raise requests.HTTPError('Received non 200 status code from Instagram')
        except requests.RequestException:
            raise requests.RequestException
        else:
            return response.text
 
    @staticmethod
    def extract_json_data(html):
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('body')
        script_tag = body.find('script')
        raw_string = script_tag.text.strip().replace('window._sharedData =', '').replace(';', '')
        return json.loads(raw_string)
 
    def profile_page_metrics(self, profile_url):
        results = {}
        try:
            response = self.__request_url(profile_url)
            json_data = self.extract_json_data(response)
            metrics = json_data['entry_data']['ProfilePage'][0]['graphql']['user']
        except Exception as e:
            raise e
        else:
            for key, value in metrics.items():
                if key != 'edge_owner_to_timeline_media':
                    if value and isinstance(value, dict):
                        value = value['count']
                        results[key] = value
                    elif value:
                        results[key] = value
        return results
 
    def profile_page_recent_posts_time(self, profile):
        profile_url = 'https://www.instagram.com/{}/'.format(profile)
        results = []
        try:
            response = self.__request_url(profile_url)
            json_data = self.extract_json_data(response)
            metrics = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']["edges"]
            for node in metrics:
                node = node.get('node')
                if node and isinstance(node, dict):
                    results.append(node)
            time_difference = datetime.now() - datetime.fromtimestamp(int(results[0]['taken_at_timestamp']))
            print('{:<25s} posted {:>12s} ago'.format(profile, str(time_difference)))
    
        except:
            print("Trouble finding info for " + profile_url)

def main():
    obj = InstagramScraper()

    # Reads file instead of copy and paste method below
    username_list = [line.rstrip() for line in open('usernames.txt')]

    print(username_list)

    '''
    print("Enter/Paste elements, press[Enter], then press Ctrl-D to save it and run program.")

    while(True):
        
        try:
            user = input()
          
        except EOFError:
            break
        
        for x in user.split():
            username_list.append(x)
    '''
    for x in username_list:
        obj.profile_page_recent_posts_time(x)

if __name__ == '__main__':
    main()
