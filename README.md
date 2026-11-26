# NYT bestseller tracker
*a data pipeline that collects weekly New York Times bestseller lists to analyze how books rise, fall and stay on the charts*

## about

This project builds a data pipeline around the New York Times Best Sellers lists.
Each week, it collects every list from the [NYT Books API](https://developer.nytimes.com/docs/books-product/1/overview),
stores the raw data, and turns it into a clean table of one row per book, per list, per week.

With enough weeks collected, the data can show how bestsellers behave over time:
whether strong debuts last, whether books that enter low ever climb, and which lists change the fastest.

## questions

1. **Do strong debuts last?**
   Of the books that debut in the top 3 of a list (`weeks_on_list == 1` and `rank <= 3`), what share is still on that list without interruption 1, 2, 3, … weeks later? A book counts as gone from the first week it drops off, even if it re-enters later. For each N, only debuts with at least N weeks of data after them are counted.
   Re-entries (`rank_last_week == 0` with `weeks_on_list > 1`) are not counted as debuts.

2. **Do books that enter low ever climb?**
   Of the books that debut in the bottom 4 ranks of their list, what share later reaches a better rank than its debut rank in any following week? Because lists have different lengths (e.g. 10 or 15 books), "bottom 4" is defined per list.

3. **Which lists change the fastest?**
   For each list, the turnover rate is the share of books that are new each week
   (`weeks_on_list == 1`), averaged over all collected weeks. Lists published
   monthly are compared per issue, not per week.

## how to run

1. Clone the repo and create a virtual environment:
   ```bash
   git clone https://github.com/melolw/bestsellers-tracker.git
   cd bestsellers-tracker
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Get a free API key at [developer.nytimes.com](https://developer.nytimes.com) (enable the Books API),
   then create a `.env` file in the project root:
   ```
   NYT_API_KEY=your-key-here
   ```

3. Run the pipeline from the project root:
   ```bash
   python src/extract.py     # fetches the latest weeks into data/raw/ (skips weeks already saved)
   python src/transform.py   # builds data/processed/bestsellers.csv
   ```

## project status

- [x] explore the API's data to get a feeling on how it is structured, what data is relevant for me and what some of these actually mean
- [x] formulate some questions I want to answer using the data
- [x] write my first scripts to start having a pipeline that stores the data for later analysis
- [ ] backfill more weeks of history (e.g. 6 months)
- [ ] analysis notebook answering the three questions
- [ ] load the processed data into Postgres (Docker)
- [ ] run the pipeline automatically every week with GitHub Actions
