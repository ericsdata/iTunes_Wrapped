### Intro

This was one of my earliest data projects that has taken many lives. Originally written in base R when I started my analytics journey in 2017, I revisited and revised in 2020 to use Python for data processing, and to push the data into a relational database (SQLite), which made analysis much faster. 

Loaded into the relational databse, my iTunes listening habits are much more accessible, allowing simple SQL queries to answer complex data questions, like what were my favorite artists of the year or seasonal trends to songs on particular albums. 

### The Project

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


## Play with it

The `WORKER.py` file shows a possible workflow for cleansing and loading the iTunes data. 

SQL Scripts or Exploratory data analysis with R would be opportunities to start exploring this data.