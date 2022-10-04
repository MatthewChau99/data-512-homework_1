import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

### Loading datasets
with open(os.path.join('data', 'dino_monthly_desktop_<start201501>-<end202201>.json'), 'r') as f:
    desktop_dict = json.load(f)

with open(os.path.join('data', 'dino_monthly_mobile_<start201501>-<end202201>.json'), 'r') as f:
    mobile_dict = json.load(f)

desktop_views = {
    article: {
        'views':[month['views'] for month in desktop_dict[article]],
        'months': [month['timestamp'][:-2] for month in desktop_dict[article]] 
    } for article in desktop_dict
}

mobile_views = {
    article: {
        'views':[month['views'] for month in mobile_dict[article]],
        'months': [month['timestamp'][:-2] for month in mobile_dict[article]] 
    } for article in mobile_dict
}


def plot_max_min_average():
    """
    Plots time series for the articles that have the highest average page requests and the lowest average page requests for desktop access and mobile access

    Outputs:
        /img/max_min_avg.png
    """
    max_desk = ('', -float('inf'), [])
    min_desk = ('', float('inf'), [])
    max_mob = ('', -float('inf'), [])
    min_mob = ('', float('inf'), [])

    for article, param in desktop_views.items():
        article_avg = np.mean(param['views'])
        months = param['months']
        if article_avg > max_desk[1]:
            max_desk = (article, article_avg, months)
        if article_avg < min_desk[1]:
            min_desk = (article, article_avg, months)
    
    for article, param in mobile_views.items():
        article_avg = np.mean(param['views'])
        months = param['months']
        if article_avg > max_mob[1]:
            max_mob = (article, article_avg, months)
        if article_avg < min_mob[1]:
            min_mob = (article, article_avg, months)

    sns.set(rc={'figure.figsize':(16.7,8.27)})

    sns.lineplot(x=pd.to_datetime(max_desk[2], format='%Y%m%d'), y=desktop_views[max_desk[0]]['views'], label=f'Desktop Max - {max_desk[0]}')
    sns.lineplot(x=pd.to_datetime(min_desk[2], format='%Y%m%d'), y=desktop_views[min_desk[0]]['views'], label=f'Desktop Min - {min_desk[0]}')
    sns.lineplot(x=pd.to_datetime(max_mob[2], format='%Y%m%d'), y=mobile_views[max_mob[0]]['views'], label=f'Mobile Max - {max_mob[0]}')
    sns.lineplot(x=pd.to_datetime(min_mob[2], format='%Y%m%d'), y=mobile_views[min_mob[0]]['views'], label=f'Mobile Max - {min_mob[0]}')
    
    plt.xticks(rotation=45)
    plt.title("Max and Min average for desktop and mobile")
    plt.xlabel('Date')
    plt.ylabel('Views')
    plt.savefig(os.path.join('img', 'max_min_avg.png'))
    plt.close()


def top_10_peak():
    """
    Plots time series for the top 10 article pages by largest (peak) page views over the entire time by access type

    Outputs:
        /img/top10peak.png
    """
    desktop_max = {
        article: {
            'views': desktop_views[article]['views'][np.argmax(desktop_views[article]['views'])],
            'months': desktop_views[article]['months'][np.argmax(desktop_views[article]['views'])]
        } for article in desktop_dict
    }

    mobile_max = {
        article: {
            'views': mobile_views[article]['views'][np.argmax(mobile_views[article]['views'])],
            'months': mobile_views[article]['months'][np.argmax(mobile_views[article]['views'])]
        } for article in mobile_dict
    }

    top_10_desktop = [(article, desktop_max[article]['views'], desktop_max[article]['months']) for article in desktop_max]
    top_10_mobile = [(article, mobile_max[article]['views'], mobile_max[article]['months']) for article in mobile_max]

    top_10_desktop = sorted(top_10_desktop, key=lambda x:x[1], reverse=True)[:10]
    top_10_mobile = sorted(top_10_mobile, key=lambda x:x[1], reverse=True)[:10]

    sns.set(rc={'figure.figsize':(16.7,8.27)})
    for article, _, _ in top_10_desktop:
        ax = sns.lineplot(x=pd.to_datetime(desktop_views[article]['months'], format='%Y%m%d'), y=desktop_views[article]['views'], linewidth=1, label=f'D: {article}')
    
    for article, _, _ in top_10_mobile:
        ax = sns.lineplot(x=pd.to_datetime(mobile_views[article]['months'], format='%Y%m%d'), y=mobile_views[article]['views'], linewidth=1, linestyle='--', label=f'M: {article}')

    plt.yscale('log')
    plt.xticks(rotation=45)
    plt.title("Top 10 for desktop and mobile")
    plt.xlabel('Date')
    plt.ylabel('Views')
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    plt.savefig(os.path.join('img', 'top10peak.png'))
    plt.close()


def fewest_month():
    """
    Plots time series for pages that have the fewest months of available data

    Outputs:
        /img/fewest_month.png
    """
    desktop_len = [(article, len(desktop_views[article]['views'])) for article in desktop_dict]
    mobile_len = [(article, len(mobile_views[article]['views'])) for article in mobile_dict]

    min_10_desktop_len = sorted(desktop_len, key=lambda x:x[1])[:10]
    min_10_mobile_len = sorted(mobile_len, key=lambda x:x[1])[:10]

    sns.set(rc={'figure.figsize':(16.7,8.27)})
    for article, _ in min_10_desktop_len:
        sns.lineplot(x=pd.to_datetime(desktop_views[article]['months'], format='%Y%m%d'), y=desktop_views[article]['views'], linewidth=1, label=f'Desktop: {article}')
    
    for article, _ in min_10_mobile_len:
        sns.lineplot(x=pd.to_datetime(mobile_views[article]['months'], format='%Y%m%d'), y=mobile_views[article]['views'], linewidth=1, linestyle='--', label=f'Mobile: {article}')

    plt.xticks(rotation=45)
    plt.title("Fewest month of data for desktop and mobile")
    plt.xlabel('Date')
    plt.ylabel('Views')
    plt.savefig(os.path.join('img', 'fewest_month.png'))
    plt.close()


if __name__ == '__main__':
    plot_max_min_average()
    top_10_peak()
    fewest_month()
    
