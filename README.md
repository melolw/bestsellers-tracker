# NYT Bestseller Tracker
a data pipeline that collects weekly New York Times bestseller lists to analyze how books rise, fall and stay on the charts

## about

This project builds a data pipeline around the New York Times Best Sellers lists.
Each week, it collects every list from the [NYT Books API](https://developer.nytimes.com/docs/books-product/1/overview),
stores the raw data, and turns it into a clean table of one row per book, per list, per week.

With enough weeks collected, the data can show how bestsellers behave over time:
whether strong debuts last, whether books that enter low ever climb, and which lists change the fastest.


## project status

- [x] explore the API's data to get a feeling on how it is structured, what data is relevant for me and what some of these actually mean
- [ ] formulate some questions I want to answer using the data
- [ ] write my first scripts to start having a pipeline that stores the data for later analysis
