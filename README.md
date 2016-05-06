# greenhouse-interview-analytics

![image](https://cloud.githubusercontent.com/assets/21108/15075461/54b5ff9c-1359-11e6-897a-96b6891fa950.png)


Download scorecards to a local SQLite database and analyze them through interactive charts based on [dc.js](https://dc-js.github.io/dc.js/).

```
$ python fetch.py --token yourgreenhousetoken --department=Engineering
$ python webapp.py # open http://localhost:5000/
```

## scripts

### `fetch.py`

Scrape scorecard data from Greenhouse.

By default, updates scorecards for applications with new activities. Run with `--all` to refetch everything.

### `webapp.py`

Explore the dataset through interactive charts.

There are a few configuration options in `default_settings.py`. (For now, there's no way to override this but to edit it directly.)

### `analyze.py`

Query the database from the command line:

* Overall recommendation breakdown by tag
