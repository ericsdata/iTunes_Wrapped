# iTunes Wrapped - Quick Reference Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd C:\Users\eachr\Documents\Projects\iTunes_Wrapped
pip install -r requirements.txt
```

### Step 2: Load Data (if not already done)
```bash
python src/WORKER.py
```

### Step 3: Run the App
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 🎯 App Navigation

| Tab | What It Shows | Best For |
|-----|---------------|----------|
| 📊 **Overview** | Key stats, top songs/artists, recent adds | Getting a quick snapshot |
| ▶️ **Play Counts** | Listening trends, active periods | Understanding your play patterns |
| 📈 **Library Growth** | How your collection has grown | Tracking collection expansion |
| 🌍 **Seasonal** | Monthly/seasonal listening patterns | Finding seasonal trends |
| 👥 **Artists** | Individual artist deep dives | Exploring favorite artists |
| ⚙️ **Data Mgmt** | Database info, consistency checks | Data quality and cleanup |

---

## 📊 Understanding the Visualizations

### 1. **Cumulative Plays Over Time** (Line Chart)
- Shows total plays accumulating over your entire library history
- Steeper line = more active listening period
- Hover for exact dates and play counts

### 2. **Play Distribution** (Histogram)
- How many songs have been played 1x, 2x, 3x, etc.
- Most songs clustered on the left = casual listening
- Long right tail = favorite tracks with many plays

### 3. **Library Growth** (Area Chart)
- Cumulative count of songs added
- Steep sections = periods of active music acquisition
- Shows when you got most excited about buying music

### 4. **Monthly Additions** (Bar Chart)
- How many NEW songs you added each month
- Peaks show purchasing/acquiring sprees
- Troughs show months with minimal new additions

### 5. **Seasonal Patterns** (Bar Charts)
- Compare plays across months or seasons
- Identifies "summer hits" vs "winter listening"
- Year-over-year lines show if patterns repeat

### 6. **Artist Comparison** (Multi-line Chart)
- Top 10 artists' play counts over time
- Track which artists you're listening to when
- See when you discovered new favorites

---

## 🔍 Key Metrics Explained

| Metric | Meaning | Use Case |
|--------|---------|----------|
| **Total Plays** | Sum of all plays across library | Overall engagement |
| **Total Songs** | Unique tracks in library | Collection size |
| **Total Artists** | Unique artists represented | Diversity |
| **Library Span** | Years from first to last addition | History depth |
| **Average Plays/Song** | Mean plays across all songs | Typical engagement |
| **Play Differential** | Change in plays between snapshots | Recent activity |

---

## 🧹 Data Cleaning Tips

### When to Clean
- After importing new XML data
- If you see "duplicate" artist entries
- When play counts seem inconsistent

### What Gets Cleaned
- ✅ Artist names (removes "Deluxe", "Remaster" versions)
- ✅ Track names (removes version info like "Album Version")
- ✅ NULL values (replaces with 0 for counts)
- ✅ Invalid records (removes orphaned entries)

### How to Clean
1. Go to **Data Management** tab
2. Click **"Identify Duplicates"** to find problems
3. Click **"Clean Artist Names"** / **"Clean Track Names"**
4. Check the **Consistency Report** for overall health

---

## 💾 Database Structure

Your SQLite database has 2 main tables:

### metaMusic Table (Song Metadata)
```
persistent_id (PRIMARY KEY)  - Unique iTunes ID
title                        - Song name
artist                       - Artist name  
album                        - Album name
date_added                   - When added to library
play_count                   - Total lifetime plays
year                         - Album year
genre                        - Music genre
```

### activity Table (Play History)
```
persistent_id (FOREIGN KEY)  - Links to metaMusic
library_date                 - Date of snapshot
play_count                   - Total plays as of this date
skip_count                   - Total skips as of this date
```

---

## 🔄 Data Flow

```
iTunes App
    ↓
XML Export (monthly)
    ↓
lib_data/ folder (sample files)
    ↓
Library.py (parse XML)
    ↓
WORKER.py (load into DB)
    ↓
iTunes.db (SQLite database)
    ↓
app.py (Streamlit analysis)
    ↓
Interactive visualizations 📊
```

---

## ⚡ Performance Tips

1. **First Load**: App will take a moment to load data
2. **Caching**: Subsequent loads use cached data (1 hour TTL)
3. **Refresh**: Click **"Refresh Data"** in sidebar to clear cache
4. **Large DB**: If slow, consider time-filtering in sidebar

---

## 🐛 Troubleshooting

### App won't start
```bash
# Check if Streamlit is installed
pip show streamlit

# If not, install it
pip install -r requirements.txt
```

### "Database not found" error
```bash
# Make sure iTunes.db exists in project root
# Or set custom path:
set ITUNES_DB_PATH=C:\path\to\iTunes.db
streamlit run app.py
```

### No data showing
```bash
# Run data loading first
python src/WORKER.py

# Check database has data
python -c "import sqlite3; c=sqlite3.connect('iTunes.db'); print('Tables:', [row[0] for row in c.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall()])"
```

### Charts look empty
- Try clicking **"Refresh Data"** button
- Check if date range is filtering out data
- Verify multiple snapshots in database

---

## 📚 Useful Python Code Snippets

### Get your top 20 songs (Python script)
```python
from modules import load_music_data, get_top_tracks

metadata, activity = load_music_data('iTunes.db')
top_songs = get_top_tracks(activity, metadata, n=20)
print(top_songs[['title', 'artist', 'total_plays']])
```

### Generate consistency report
```python
from modules import load_music_data, generate_consistency_report

metadata, activity = load_music_data('iTunes.db')
report = generate_consistency_report(metadata, activity)
print(report)
```

### Find duplicate artists
```python
from modules import load_music_data, identify_duplicate_artists

metadata, _ = load_music_data('iTunes.db')
duplicates = identify_duplicate_artists(metadata)
print(duplicates)
```

---

## 🎨 Customization

### Change App Title/Logo
Edit `app.py` line ~60:
```python
st.set_page_config(
    page_title="Your Custom Title",
    page_icon="🎵",  # Change emoji here
    ...
)
```

### Change Colors/Theme
Add to `app.py` (after st.markdown):
```python
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .metric-card { background-color: #e0e0e0; }
    </style>
""", unsafe_allow_html=True)
```

### Add New Visualization
1. Add function to `modules/visualizations.py`
2. Call it from appropriate tab in `app.py`
3. Use `st.plotly_chart()` to display

---

## 🔐 Privacy & Security

- 🔒 All processing is local (no data sent anywhere)
- 💾 Database stays on your machine
- 🔑 No authentication needed (local use only)
- ⚠️ Be careful if sharing the `.db` file or app publicly

---

## 📞 Getting Help

1. **Check SETUP.md** for detailed setup instructions
2. **Check IMPLEMENTATION_SUMMARY.md** for architecture details
3. **Run examples.py** to see working code
4. **Check docstrings** in modules (each function has documentation)

---

## 🎯 Next Ideas

### Analysis Questions to Answer
- What's your most-played song of all time?
- Do you listen more in winter or summer?
- How does your artist diversity trend over time?
- Which artists peaked in play counts?
- What months do you add most music?

### Potential Enhancements
- 🎨 Genre-based analysis
- 📅 Album-focused deep dives
- 🏆 Decade-based statistics
- 📊 Skip rate analysis
- 💾 Export to CSV/PDF

### Integration Ideas
- Spotify API comparison
- Lyrics analysis
- Playlist recommendations
- Music discovery suggestions

---

## 📊 Quick Stats Your Data Probably Shows

- 🎵 Songs in library: ~5,000-50,000 typically
- 👥 Unique artists: ~1,000-10,000 typically  
- ▶️ Total plays: ~100,000-1,000,000 over years
- 📅 Data span: 5-10+ years for most users
- 🎯 Favorite artist plays: Often 1,000+ for top artist

---

Good luck exploring your iTunes library! 🎵🎧
