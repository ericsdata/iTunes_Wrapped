## Intro

This was one of my earliest data projects that has taken many lives. Originally written in base R when I started my analytics journey in 2017, I revisited and revised in 2020 to use Python for data processing, and to push the data into a relational database (SQLite), which made analysis much faster. 

Loaded into the relational databse, my iTunes listening habits are much more accessible, allowing simple SQL queries to answer complex data questions, like what were my favorite artists of the year or seasonal trends to songs on particular albums. 

## The Project

As one of the standouts who still maintains a digital music library (and accompa·nying, fully-functional iPod Classic), the Spotify Wrapped that is released each year lacks the full picture of my musical tastes.

So I developed this code to manage data exported out of my iTunes library (manual monthly snapshots dating back to 2017). The base iTunes data includes:

- Song Info (Title, Artist, Album, Year)
- Play Information (Number of Times Played, Times Skipped, Most Recent Play)
- Metadata (Date Added, Location)


These features allow for a deep dive into my listening habits -- similar to the Spotify Wrapped. 

### The Process

This repository contains code that transforms raw iTunes data (exported manually into XML) into relational data tables that can then be used as the basis for exploratory data analysis.

A Tableau layer was built on top of the SQLite database, however my Tableau license has since expired leaving it locked in SaaS graveyard until I am again blessed with a personal license. 

#### Data Collection

Data is collected manually by exporting XML data directly from iTunes. I first started in August 2017, and eventually came to regularly export these snapshots by month end. I sample of these files exists in the `lib_data` folder 

#### Data Set up

The file `DBM.py` handles the connection to the database, including the creation of tables and functions necessary to insert data into the tables. 

#### Data Cleansing and Loading

The file `Library.py` handles process of raw XML data into data to feed into the new relational databases. 


### Play with it

#### Interactive Streamlit App (NEW! 🎉)

A new interactive web app has been built using **Streamlit** for exploring your iTunes data:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app includes the following features:

- **Overview Dashboard**: View key statistics about your library (total songs, artists, play counts)
- **Play Count Analysis**: Explore cumulative plays, distribution, and most active listening periods
- **Library Growth**: Track how your music collection has grown over time, with monthly additions and artist growth
- **Seasonal Trends**: Analyze listening patterns by month and season, including year-over-year comparisons
- **Artist Analysis**: Deep dive into individual artists' play history and compare top artists over time
- **Data Management**: View database statistics, run consistency checks, and identify potential duplicate artist names

#### Features

- **Interactive Visualizations**: All charts are built with Plotly for interactive exploration
- **Data Cleaning**: Automatic cleaning with option to standardize artist/track names
- **Consistency Checking**: Identify data issues like orphaned records, missing metadata, etc.
- **Time-based Filtering**: Analyze data within custom date ranges
- **Performance**: Results are cached for fast interactions

#### Environment Variables

You can optionally set the database path via environment variable:

```bash
set ITUNES_DB_PATH=path\to\iTunes.db
streamlit run app.py
```

If not set, defaults to `iTunes.db` in the project root.

#### Data Pipeline

The existing Python infrastructure (`WORKER.py`, `Library.py`, `DBM.py`) remains unchanged:

1. Export XML data from iTunes
2. Run `WORKER.py` to load data into SQLite database
3. Launch the Streamlit app to explore

The `modules/` folder contains reusable Python functions for:
- **data_loader.py**: Database connections and data loading
- **visualizations.py**: Plotly chart generation
- **data_cleaning.py**: Data standardization and consistency checking