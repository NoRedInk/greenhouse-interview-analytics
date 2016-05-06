# greenhouse-interview-analytics

Download scorecards to a local SQLite database and analyze them through interactive charts based on [dc.js](https://dc-js.github.io/dc.js/).

```
$ python fetch.py --token yourgreenhousetoken --department=Engineering
$ python webapp.py # open http://localhost:5000/
```

## `fetch.py`

Scrape scorecard data from Greenhouse.

By default, updates scorecards for applications with new activities. Run with `--all` to refetch everything.

## `webapp.py`

Explore the dataset through interactive charts.

## `analyze.py`

Query the database for useful information:

* Overall recommendation breakdown by tag
