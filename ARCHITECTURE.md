# iTunes Wrapped - Developer Architecture Guide

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT WEB APP                         │
│                       (app.py)                               │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │ Overview     │ Play Counts  │ Library      │             │
│  │ Growth       │ Seasonal     │ Artists      │             │
│  │ Data Mgmt    │              │              │             │
│  └──────────────┴──────────────┴──────────────┘             │
│                                                              │
│  Session State & Caching                                    │
│  (st.cache_data, st.cache_resource)                         │
└──────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                   PYTHON MODULES                             │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ data_loader.py                                         │ │
│  │ • load_music_data()          • get_top_artists()     │ │
│  │ • calculate_play_differential() • get_library_stats() │ │
│  │ • get_top_tracks()           • get_database_info()   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ visualizations.py                                      │ │
│  │ • plot_cumulative_plays_over_time()                   │ │
│  │ • plot_cumulative_library_size()                      │ │
│  │ • plot_seasonal_trends_*()                            │ │
│  │ • plot_artist_play_history()                          │ │
│  │ • plot_top_artists_comparison()                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ data_cleaning.py                                       │ │
│  │ • identify_duplicate_artists()                        │ │
│  │ • standardize_artist_names()                          │ │
│  │ • generate_consistency_report()                       │ │
│  │ • clean_artist_names()                                │ │
│  │ • identify_data_inconsistencies()                     │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────┐
│              PANDAS DataFrames (In Memory)                   │
│                                                              │
│  metadata.csv        activity.csv                           │
│  ──────────────────  ──────────────────                      │
│  persistent_id       persistent_id                          │
│  title               library_date                           │
│  artist              play_count                             │
│  album               skip_count                             │
│  date_added          ...                                    │
│  year                                                       │
│  ...                                                        │
└──────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                  SQLite Database                             │
│                    (iTunes.db)                               │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ metaMusic Table                                       │  │
│  │ (persistent_id: primary key)                         │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ activity Table                                        │  │
│  │ (persistent_id + library_date: composite key)        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ diffs Table (optional)                                │  │
│  │ (play count differentials)                            │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. **Application Start**
```
app.py starts
    ↓
Check if cached data exists
    ↓
If not: load_music_data('iTunes.db')
    ↓
Data is cached for 1 hour
    ↓
Render UI
```

### 2. **Data Loading Pipeline**
```
load_music_data()
    ├─ connect_db() → SQLite connection
    ├─ Read metaMusic table → metadata DataFrame
    ├─ Read activity table → activity DataFrame
    ├─ Convert data types (dates, numerics)
    ├─ Apply cleaning (if enabled)
    │   ├─ clean_metadata()
    │   ├─ clean_activity()
    │   └─ Standardize names, handle nulls
    └─ Return (metadata, activity)
```

### 3. **Visualization Pipeline**
```
User selects a chart
    ↓
Data preparation function runs
    (e.g., get_top_tracks)
    ↓
DataFrame manipulation
    (groupby, sort, slice)
    ↓
Visualization function
    (e.g., plot_cumulative_plays_over_time)
    ↓
Plotly Figure object created
    ↓
st.plotly_chart() renders to browser
```

---

## 📦 Module Dependency Graph

```
app.py (main)
├── imports data_loader
│   ├── sqlite3 (standard library)
│   ├── pandas
│   └── numpy
├── imports visualizations
│   ├── plotly
│   └── pandas
├── imports data_cleaning
│   ├── pandas
│   ├── difflib (standard library)
│   └── typing (standard library)
└── imports streamlit
```

**No circular dependencies** ✓

---

## 🎯 Key Design Decisions

### 1. **Modular Architecture**
- Each module has a single responsibility
- Functions are pure (no side effects)
- Easy to test and reuse

### 2. **Caching Strategy**
- `@st.cache_data(ttl=3600)` for data (1 hour)
- `@st.cache_resource` for database connection
- Balances freshness vs performance

### 3. **Error Handling**
- Try/except blocks in main data loading
- User-friendly error messages
- Detailed error info in expanders

### 4. **Data Type Conversions**
- Dates: ISO format → datetime64
- Numerics: String → int/float
- NULLs: Preserved or replaced with 0

### 5. **Plotly Over Matplotlib**
- ✓ Interactive (zoom, pan, hover)
- ✓ Responsive design
- ✓ Beautiful defaults
- ✓ No image saving needed

---

## 🔍 Function Reference

### data_loader.py

#### `load_music_data(db_path: str, apply_cleaning: bool = True) → Tuple[DataFrame, DataFrame]`
**Purpose**: Main entry point for loading data
**Steps**:
1. Connect to SQLite database
2. Read metaMusic table
3. Read activity table
4. Convert data types
5. Optionally clean data
6. Return tuple of dataframes

**Performance**: O(n) where n = number of records

#### `get_top_tracks(activity, metadata, n=25) → DataFrame`
**Purpose**: Get n most-played tracks
**Algorithm**:
1. Group activity by persistent_id
2. Sum play_count for each track
3. Merge with metadata for track info
4. Sort by play_count descending
5. Return top n

**Performance**: O(n log n) due to sorting

#### `calculate_play_differential(activity) → DataFrame`
**Purpose**: Calculate play count changes between snapshots
**Algorithm**:
1. Sort by (persistent_id, library_date)
2. Group by persistent_id
3. Calculate diff() on play_count
4. Fill first value (no previous snapshot)
5. Clip negatives to 0

**Performance**: O(n)

### visualizations.py

All plot functions follow this pattern:
1. Prepare data (filter, aggregate, transform)
2. Create base figure
3. Add trace(s) with styling
4. Update layout (title, axes, hover)
5. Return Figure object

**Performance**: O(n) for data prep + O(n log n) for rendering

### data_cleaning.py

#### `fuzzy_match_strings(s1: str, s2: str, threshold: float = 0.85) → bool`
**Algorithm**: SequenceMatcher from difflib
- Compares character sequences
- Returns similarity ratio
- Threshold-based matching

**Performance**: O(n*m) where n,m = string lengths

#### `identify_duplicate_artists(metadata) → DataFrame`
**Algorithm**:
1. Extract unique artists
2. Nested loop comparing all pairs
3. Fuzzy match with 0.80 threshold
4. Count occurrences
5. Return deduplicated results

**Performance**: O(a²) where a = number of artists

---

## 🧪 Testing Strategy

### Unit Test Examples

```python
# Test data loading
def test_load_music_data():
    metadata, activity = load_music_data('iTunes.db')
    assert len(metadata) > 0
    assert 'persistent_id' in metadata.columns
    assert activity['play_count'].dtype == 'int64'

# Test top tracks
def test_get_top_tracks():
    metadata, activity = load_music_data('iTunes.db')
    top = get_top_tracks(activity, metadata, n=5)
    assert len(top) == 5
    assert top['total_plays'].is_monotonic_decreasing

# Test fuzzy matching
def test_fuzzy_match():
    assert fuzzy_match_strings("The Beatles", "The Beatles") == True
    assert fuzzy_match_strings("Taylor Swift", "Taylor Swft") == True
    assert fuzzy_match_strings("Artist A", "Artist B") == False
```

### Integration Test

```python
# Full pipeline test
def test_full_pipeline():
    metadata, activity = load_music_data('iTunes.db')
    
    # Check data integrity
    orphaned = set(activity['persistent_id']) - set(metadata['persistent_id'])
    assert len(orphaned) == 0, f"Found {len(orphaned)} orphaned IDs"
    
    # Check consistency
    total_plays = activity['play_count'].sum()
    assert total_plays > 0
    
    # Check visualizations
    fig = plot_cumulative_plays_over_time(activity)
    assert len(fig.data) > 0
```

---

## 🚀 Performance Optimization

### Current Bottlenecks

| Operation | Time | Optimization |
|-----------|------|---------------|
| Load metadata | O(n) | ✓ Cached 1 hour |
| Calculate differentials | O(n) | Could add index on persistent_id |
| Duplicate detection | O(a²) | Could use clustering algorithm |
| Large plots | O(n) | Use aggregation for large datasets |

### Future Optimizations

1. **Database Indexing**
   ```sql
   CREATE INDEX idx_persistent_id ON metaMusic(persistent_id);
   CREATE INDEX idx_library_date ON activity(library_date);
   ```

2. **Data Aggregation**
   - Store monthly summaries instead of daily
   - Pre-calculate common queries
   - Use materialized views

3. **Query Optimization**
   - Push filtering to SQL layer
   - Limit result sets
   - Use LIMIT in SQL queries

---

## 🐛 Common Issues & Solutions

### Issue: Slow Data Loading
**Cause**: Large database, no caching
**Solution**: 
- Cache is set to 1 hour by default
- User can click refresh to reload
- Consider adding database indexes

### Issue: Memory Usage
**Cause**: Entire dataset in memory
**Solution**:
- Add date range filtering
- Stream data in chunks
- Aggregate on database side

### Issue: Visualization Performance
**Cause**: Too many data points (>10k)
**Solution**:
- Aggregate to monthly data
- Downsample time series
- Pre-calculate summaries

---

## 📝 Code Style Guidelines

### Naming Conventions
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private: prefix with `_`

### Documentation
Every function should have:
```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    Short description.
    
    Longer description with context.
    
    Args:
        param1: Description
        param2: Description
    
    Returns:
        Description of return value
    
    Examples:
        >>> result = function_name(arg1, arg2)
        >>> print(result)
    """
```

### Error Handling
```python
try:
    # Operation
    result = do_something()
except SpecificError as e:
    # Log or handle specifically
    raise ValueError(f"Clear error message: {e}")
except Exception as e:
    # Generic fallback
    raise Exception(f"Unexpected error: {e}")
```

---

## 🔐 Security Considerations

### Input Validation
- User inputs (dates, artist names) are validated
- SQL queries use parameterized queries
- No string concatenation in SQL

### Data Privacy
- All processing local to machine
- No data transmission
- SQLite is file-based (no server)

### Error Messages
- Don't expose sensitive file paths in production
- Log detailed errors internally
- Show user-friendly messages

---

## 📊 Extension Points

### Adding a New Visualization

1. **Add to visualizations.py**:
```python
def plot_my_custom_chart(data: pd.DataFrame) -> go.Figure:
    """Create custom visualization."""
    fig = go.Figure()
    fig.add_trace(...)
    fig.update_layout(...)
    return fig
```

2. **Use in app.py**:
```python
from visualizations import plot_my_custom_chart

# In appropriate tab:
fig = plot_my_custom_chart(activity)
st.plotly_chart(fig, use_container_width=True)
```

### Adding a New Analysis Function

1. **Add to data_loader.py**:
```python
def analyze_my_metric(metadata, activity) -> pd.DataFrame:
    """Calculate my custom metric."""
    result = (
        activity
        .merge(metadata, on='persistent_id')
        .groupby(...)
        .agg(...)
    )
    return result
```

2. **Use in app.py**:
```python
from data_loader import analyze_my_metric

result = analyze_my_metric(metadata, activity)
st.dataframe(result)
```

---

## 🎯 Development Roadmap

### Phase 1: Current (✓ Complete)
- Core data loading
- 15+ visualizations
- Data cleaning tools
- Streamlit UI

### Phase 2: Suggested Enhancements
- Genre-based analysis
- Album deep dives
- Playlist recommendations
- Export capabilities

### Phase 3: Advanced Features
- Predictive analytics
- Collaborative filtering
- Integration with Spotify
- Mobile app

---

## 📚 Related Resources

- Streamlit Docs: https://docs.streamlit.io/
- Plotly Docs: https://plotly.com/python/
- Pandas Docs: https://pandas.pydata.org/docs/
- SQLite Docs: https://www.sqlite.org/docs.html

---

## ✅ Checklist for Contributing

- [ ] Code follows style guidelines
- [ ] Functions have docstrings
- [ ] Error handling implemented
- [ ] Type hints included
- [ ] No hardcoded paths
- [ ] Performance acceptable
- [ ] Works with existing modules
- [ ] Tested locally

---

This document serves as the technical reference for understanding and extending the iTunes Wrapped application.
