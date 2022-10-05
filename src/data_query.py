"""
This module contains functions to 
"""
import json
import os
import time
import urllib

import pandas as pd
import requests
import tqdm

#########
#
#    CONSTANTS
#

# The REST API 'pageviews' URL - this is the common URL/endpoint for all 'pageviews' API requests
API_REQUEST_PAGEVIEWS_ENDPOINT = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/'

# This is a parameterized string that specifies what kind of pageviews request we are going to make
# In this case it will be a 'per-article' based request. The string is a format string so that we can
# replace each parameter with an appropriate value before making the request
API_REQUEST_PER_ARTICLE_PARAMS = 'per-article/{project}/{access}/{agent}/{article}/{granularity}/{start}/{end}'

# The Pageviews API asks that we not exceed 100 requests per second, we add a small delay to each request
API_LATENCY_ASSUMED = 0.002       # Assuming roughly 2ms latency on the API and network
API_THROTTLE_WAIT = (1.0/100.0)-API_LATENCY_ASSUMED

# When making a request to the Wikimedia API they ask that you include a "unique ID" that will allow them to
# contact you if something happens - such as - your code exceeding request limits - or some other error happens
REQUEST_HEADERS = {
    'User-Agent': '<uwnetid@uw.edu>, University of Washington, MSDS DATA 512 - AUTUMN 2022',
}

# This is just a list of English Wikipedia article titles that we can use for example requests
article_df = pd.read_csv(os.path.join('data', 'data_raw', 'dinosaur_genera.cleaned.SEPT.2022.csv'))
ARTICLE_TITLES = article_df['name']
ARTICLE_TITLES[0] = '"Coelosaurus" antiquus'
ARTICLE_URLS = article_df['url']

# This template is used to map parameter values into the API_REQUST_PER_ARTICLE_PARAMS portion of an API request. The dictionary has a
# field/key for each of the required parameters. In the example, below, we only vary the article name, so the majority of the fields
# can stay constant for each request. Of course, these values *could* be changed if necessary.
ARTICLE_PAGEVIEWS_PARAMS_TEMPLATE = {
    "project":     "en.wikipedia.org",
    "access":      "desktop",      # this should be changed for the different access types
    "agent":       "user",
    "article":     "",             # this value will be set/changed before each request
    "granularity": "monthly",
    "start":       "2015010100",
    "end":         "2022100100"    # this is likely the wrong end date
}


def request_pageviews_per_article(article_title = None, 
                                  endpoint_url = API_REQUEST_PAGEVIEWS_ENDPOINT, 
                                  endpoint_params = API_REQUEST_PER_ARTICLE_PARAMS, 
                                  request_template = ARTICLE_PAGEVIEWS_PARAMS_TEMPLATE,
                                  headers = REQUEST_HEADERS):
    # Make sure we have an article title
    if not article_title: return None
    
    # Titles are supposed to have spaces replaced with "_" and be URL encoded
    article_title_encoded = urllib.parse.quote(article_title.replace(' ','_'))
    request_template['article'] = article_title_encoded
    
    # now, create a request URL by combining the endpoint_url with the parameters for the request
    request_url = endpoint_url + endpoint_params.format(**request_template)
    
    # make the request
    try:
        # we'll wait first, to make sure we don't exceed the limit in the situation where an exception
        # occurs during the request processing - throttling is always a good practice with a free
        # data source like Wikipedia - or other community sources
        if API_THROTTLE_WAIT > 0.0:
            time.sleep(API_THROTTLE_WAIT)
        response = requests.get(request_url, headers=headers)
        json_response = response.json()
    except Exception as e:
        print(e)
        json_response = None
    return json_response


def generate_monthly_desktop_access():
    """
    Generates Monthly desktop page traffic with Pageviews API

    Outputs:
        /data/data_clean/dino_monthly_desktop_<start201501>-<end202210>.json containing the data in JSON format
    """
    print("======== Creating monthly desktop access data ========")
    result_json = {}
    error_articles = {"titles": []}

    for article_title in tqdm.tqdm(ARTICLE_TITLES):
        json_response = request_pageviews_per_article(article_title=article_title)
        
        # Empty response
        if not json_response:
            print(f'{article_title} has empty response. Please check.')
            continue
        
        try:
            result_json.update({article_title: json_response['items']})
        except KeyError:
            print(f'{article_title} has error. Please check.')
            error_articles['titles'].append(article_title)
    
    # Creates output
    if not os.path.exists('data'):
        os.mkdir('data')
    
    with open(os.path.join("data", "data_clean", "dino_monthly_desktop_<start201501>-<end202210>.json"), "w") as f:
        json.dump(result_json, f, indent=4)

    print("==== Data saved to /data/data_clean/dino_monthly_desktop_<start201501>-<end202210>.json ====")
    return result_json

def generate_monthly_mobile_access():
    """
    Generates Monthly mobile page traffic with Pageviews API from both mobile app and mobile web

    Outputs:
        /data/data_clean/dino_monthly_mobile_<start201501>-<end202210>.json containing the data in JSON format
    """
    print("======== Creating monthly mobile access data ========")
    result_json = {}
    error_articles = {"titles": []}

    for article_title in tqdm.tqdm(ARTICLE_TITLES):
        mobile_req_params = ARTICLE_PAGEVIEWS_PARAMS_TEMPLATE.copy()
        
        # Mobile-app response
        mobile_req_params['access'] = 'mobile-app'
        app_json_response = request_pageviews_per_article(article_title=article_title, request_template=mobile_req_params)

        # Mobile-web response
        mobile_req_params['access'] = 'mobile-web'
        web_json_response = request_pageviews_per_article(article_title=article_title, request_template=mobile_req_params)
        
        # Empty response for each API request
        if not app_json_response:
            print(f'{article_title} mobile app has empty response. Please check.')
            continue

        if not web_json_response:
            print(f'{article_title} mobile web has empty response. Please check.')
            continue

        try:
            # Combine the web and app results
            comb_json_response = [{
            'project': web['project'],
            'article': web['article'],
            'granularity': web['granularity'],
            'timestamp': web['timestamp'],
            'access': 'mobile',
            'agent': 'user',
            'views': web['views'] + app['views']
        } for web, app in zip(web_json_response['items'], app_json_response['items'])]
            
            # Add to result json
            result_json.update({article_title: comb_json_response})

        except KeyError:
            print(f'{article_title} has error. Please check.')
            error_articles['titles'].append(article_title)
    
    # Creates output
    if not os.path.exists('data'):
        os.mkdir('data')

    with open(os.path.join("data","data_clean", "dino_monthly_mobile_<start201501>-<end202210>.json"), "w") as f:
        json.dump(result_json, f, indent=4)

    print("==== Data saved to /data/data_clean/dino_monthly_mobile_<start201501>-<end202210>.json ====")
    
    return result_json


def generate_monthly_cumulative():
    """
    Generates Accumulative Monthly page traffic with Pageviews API from both mobile and desktop

    Outputs:
        /data/data_clean/dino_monthly_cumulative_<start201501>-<end202210>.json containing the data in JSON format
    """
    print("======== Creating monthly cumulative access data ========")
    result_json = {}
    error_articles = {"titles": []}

    for article_title in tqdm.tqdm(ARTICLE_TITLES):
        mobile_req_params = ARTICLE_PAGEVIEWS_PARAMS_TEMPLATE.copy()
        
        # Mobile app response
        mobile_req_params['access'] = 'mobile-app'
        app_json_response = request_pageviews_per_article(article_title=article_title, request_template=mobile_req_params)

        # Mobile web response
        mobile_req_params['access'] = 'mobile-web'
        web_json_response = request_pageviews_per_article(article_title=article_title, request_template=mobile_req_params)
        
        # Desktop response
        desktop_json_response = request_pageviews_per_article(article_title=article_title, request_template=ARTICLE_PAGEVIEWS_PARAMS_TEMPLATE)

        # Empty response for each
        if not app_json_response:
            print(f'{article_title} mobile app has empty response. Please check.')
            continue

        if not web_json_response:
            print(f'{article_title} mobile web has empty response. Please check.')
            continue

        if not desktop_json_response:
            print(f'{article_title} desktop has empty response. Please check.')
            continue
        
        try:
            # Combine results from all three responses
            comb_json_response = [{
            'project': web['project'],
            'article': web['article'],
            'granularity': web['granularity'],
            'timestamp': web['timestamp'],
            'agent': 'user',
            'views': web['views'] + app['views'] + desktop['views']
        } for web, app, desktop in zip(web_json_response['items'], app_json_response['items'], desktop_json_response['items'])]
            
            # Accumulate the views
            for i, comb in enumerate(comb_json_response):
                if i > 0:
                    prev_comb = comb_json_response[i - 1]
                    comb['views'] += prev_comb['views']

            result_json.update({article_title: comb_json_response})
        except KeyError:
            print(f'{article_title} has error. Please check.')
            error_articles['titles'].append(article_title)
    
    # Creates output
    if not os.path.exists('data'):
        os.mkdir('data')

    with open(os.path.join("data", "data_clean", "dino_monthly_cumulative_<start201501>-<end202210>.json"), "w") as f:
        json.dump(result_json, f, indent=4)

    print("==== Data saved to /data/data_clean/dino_monthly_cumulative_<start201501>-<end202210>.json ====")

    return result_json



if __name__ == '__main__':
    generate_monthly_desktop_access()
    generate_monthly_mobile_access()
    generate_monthly_cumulative()
