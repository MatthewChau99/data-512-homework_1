# Professionalism & Reproducibility
The goal of the project is to construct, analyze, and publish a dataset of monthly article traffic for a select set of pages from English Wikipedia from January 1, 2015 through September 30, 2022. The subset is limited to all dinosaur related articles for dataset generation, and only user requests are being considered for this project.

## Data
The source data is obtained through Pageviews API, which provides access to desktop, mobile web, and mobile app trafic data of English Wikipedia. The links are as shown below:
- Documentation: https://wikitech.wikimedia.org/wiki/Analytics/AQS/Pageviews
- Endpoint: https://wikimedia.org/api/rest_v1/#!/Pageviews_data/get_metrics_pageviews_aggregate_project_access_agent_granularity_start_end

### Dinosaur Related Articles List
The list of dinosaur names and urls are in `/data/data_raw/dinosaur_genera.cleaned.SEPT.2022.csv`

## Data Processing
For this project, three datasets are generated:
1. Monthly mobile access: the dataset contains monthly user traffic for both mobile-app and mobile-web access. This is stored in `data/data_clean/dino_monthly_mobile_<start201501>-<end202210>.json`
2. Monthly desktop access: the dataset contains monthly user traffic accessed from desktop. This is stored in `data/data_clean/dino_monthly_desktop_<start201501>-<end202210>.json`
3. Monthly cumulative: the dataset contains cumulative monthly user traffic both accessed from mobile and desktop. This is stored in `data/data_clean/dino_monthly_cumulative_<start201501>-<end202210>.json`.

Each JSON file uses the title names as keys, and the values are a list of time-series data collected from the requests on a monthly basis.

## Data Visualization
Three visualizations are created using seaborn lineplots as a basic visual analysis:
1. Maximum Average and Minimum Average
    This graph contains time series for articles with the highest average page requests and lowest average page requests for both desktop and mobile access.
2. Top 10 Peak Page Views
    This graph contains time series for the top 10 article pages by peak page views over the entire time by access type.
3. Fewest Months of Data
    This graph shows the pages with the fewest months of available data. Some of them have only one month of data.