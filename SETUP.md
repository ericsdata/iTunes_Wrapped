# iTunes Wrapped - Streamlit App Setup Guide

## Quick Start

### 1. Install Dependencies

From the project root directory:

```bash
pip install -r requirements.txt
```

This will install:
- **streamlit**: Web app framework
- **pandas**: Data manipulation
- **plotly**: Interactive visualizations
- **numpy**: Numerical computing

### 2. Prepare Your Data

Make sure you have:
1. Your iTunes database (SQLite) generated via `WORKER.py`
2. The database should be named `iTunes.db` or you can specify a custom path

To load new iTunes XML data:

```bash
python WORKER.py
```

### 3. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` in your default browser.

### 4. (Optional) Set Custom Database Path

If your database is not at `iTunes.db`, set an environment variable:

**Windows (PowerShell):**
```powershell
$env:ITUNES_DB_PATH = "C:\path\to\iTunes.db"
streamlit run app.py
```

**Windows (Command Prompt):**
```cmd
set ITUNES_DB_PATH=C:\path\to\iTunes.db
streamlit run app.py
```

**Mac/Linux:**
```bash
export ITUNES_DB_PATH=/path/to/iTunes.db
streamlit run app.py
```

---

## App Features

### 📊 Overview Page
- **Key Metrics**: Total songs, artists, plays, and library span
- **Top 10 Most Played**: Songs and artists with highest play counts
- **Recent Additions**: Most recently added songs

### ▶️ Play Count Analysis
- **Cumulative Plays Over Time**: Track total plays across your entire library timeline
- **Play Distribution**: Histogram showing how plays are distributed across songs
- **Most Active Periods**: Which dates had the most listening activity

### 📈 Library Growth
- **Cumulative Library Size**: How your collection has grown over time
- **Monthly Additions**: Bar chart of new songs added each month
- **Artist Growth**: How many unique artists you've added over time
- **Growth Stats**: Overall statistics and trends

### 🌍 Seasonal Trends
- **By Month**: See which months you listen to music most
- **By Season**: Winter, Spring, Summer, Fall analysis
- **Year-over-Year**: Compare listening patterns across different years

### 👥 Artist Analysis
- **Select an Artist**: Choose any artist to see detailed analysis
- **Play History**: Timeline showing plays over snapshots
- **Songs List**: All songs by artist with individual play counts
- **Artist Stats**: Total plays, average plays, and number of songs
- **Top 10 Comparison**: Compare top 10 artists over time

### ⚙️ Data Management
- **Database Info**: File size, table names, record counts
- **Data Quality**: Coverage percentage and data completeness
- **Consistency Checks**: Identify potential data issues
- **Duplicate Artists**: Find artist names that might be duplicates
- **Data Cleaning Preview**: See what cleaned data looks like

---

## Module Architecture

```
app.py                          # Main Streamlit application
requirements.txt                # Python dependencies
modules/
├── __init__.py                # Package initialization
├── data_loader.py             # Database loading functions
├── visualizations.py          # Plotly chart functions
└── data_cleaning.py           # Data standardization & cleaning
```

### data_loader.py

Core functions for loading and preparing data:

```python
# Load data from database
metadata, activity = load_music_data('iTunes.db', apply_cleaning=True)

# Get top tracks
top_tracks = get_top_tracks(activity, metadata, n=25)

# Get library growth over time
growth = get_library_growth(metadata)

# Calculate play differentials
activity_with_diff = calculate_play_differential(activity)
```

### visualizations.py

Functions for creating interactive charts:

```python
from visualizations import *

# Create various charts
fig_plays = plot_cumulative_plays_over_time(activity)
fig_size = plot_cumulative_library_size(metadata)
fig_seasonal = plot_seasonal_trends_by_month(activity, metric='plays')
fig_artist = plot_artist_play_history(activity, metadata, artist_name)
```

### data_cleaning.py

Functions for standardizing and validating data:

```python
from data_cleaning import *

# Identify potential duplicates
duplicates = identify_duplicate_artists(metadata)

# Generate consistency report
report = generate_consistency_report(metadata, activity)

# Clean artist names
clean_metadata = clean_artist_names(metadata)

# Get artist statistics
stats = get_artist_statistics(metadata, activity)
```

---

## Understanding Your Data

### Metadata Table (metaMusic)
Stores information about each song:
- `persistent_id`: Unique iTunes identifier
- `title`: Song title
- `artist`: Artist name
- `album`: Album name
- `date_added`: When song was added to library
- `play_count`: Total plays (cumulative)
- `year`: Album year
- `genre`: Music genre

### Activity Table (activity)
Tracks play activity at each snapshot:
- `persistent_id`: Links to song in metadata
- `library_date`: Date of the snapshot
- `play_count`: Total plays as of this date
- `skip_count`: Total skips as of this date

---

## Troubleshooting

### "Database not found" Error
- Check that `iTunes.db` exists in your project root
- Or set the `ITUNES_DB_PATH` environment variable
- Run `python WORKER.py` to load XML data into the database

### App crashes or won't load data
- Verify your database file is valid (try opening in SQLite browser)
- Check that all XML data has been loaded into database
- Try clearing the Streamlit cache: `streamlit run app.py --logger.level=debug`

### Missing data in visualizations
- Ensure you have multiple snapshots (dates) in your activity data
- Check data quality in the "Data Management" tab
- Run consistency checks to identify missing records

### Slow performance
- Clear cache: Delete `.streamlit/cache` folder
- Reduce date range using filters
- Check your database size in "Data Management" tab

---

## Tips for Best Results

1. **Regular Data Collection**: Export new library snapshots regularly (monthly recommended) for better time-series analysis
2. **Data Cleaning**: Run the "Identify Duplicates" check to find artist name variations
3. **Exploration**: Use the seasonal and artist analysis to discover patterns in your listening habits
4. **Sharing**: You can export charts by hovering and clicking the camera icon

---

## Performance Notes

- Data is cached for 1 hour by default
- First load may take a few seconds depending on database size
- Subsequent loads should be very fast
- Click "Refresh Data" to clear cache and reload

---

## Future Enhancements

Potential features to add:
- Genre-based analysis
- Album deep dives
- Recommendation engine based on your library
- Export data to CSV/PDF
- Sharing views via URL parameters
- Skip rate analysis
- Addition trends by genre/decade
