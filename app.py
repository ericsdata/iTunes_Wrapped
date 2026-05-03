"""
iTunes Wrapped - Streamlit App
An interactive data exploration tool for analyzing iTunes library history.
Explore play counts, library growth, artist trends, and seasonal patterns.
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / 'modules'))

from data_loader import (
    load_music_data, calculate_play_differential, get_top_tracks,
    get_top_artists, get_library_stats_by_date, get_library_growth,
    get_database_info, query_database
)
from visualizations import (
    plot_cumulative_plays_over_time, plot_plays_distribution,
    plot_cumulative_library_size, plot_new_additions_per_month,
    plot_artist_growth, plot_seasonal_trends_by_month,
    plot_seasonal_trends_by_season, plot_year_over_year_comparison,
    plot_artist_play_history, plot_top_artists_comparison
)
from data_cleaning import (
    identify_duplicate_artists, generate_consistency_report,
    get_artist_statistics, clean_artist_names, clean_track_names,
    identify_collection_gaps
)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="iTunes Wrapped",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# SESSION STATE & INITIALIZATION
# ============================================================================

@st.cache_resource
def get_database_path():
    """Get the database path, allowing user override via env var."""
    import os
    return os.getenv('ITUNES_DB_PATH', 'iTunes.db')


DB_PATH = get_database_path()


@st.cache_data(ttl=3600)
def load_data(db_path, apply_cleaning):
    """Load data from database with caching."""
    return load_music_data(db_path, apply_cleaning=apply_cleaning)


# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

st.sidebar.title("🎵 iTunes Wrapped")
st.sidebar.markdown("---")

# Database path display
st.sidebar.info(f"📁 Database: `{DB_PATH}`")

# Data cleaning toggle
apply_cleaning = st.sidebar.checkbox("Apply Data Cleaning", value=True)

# Refresh button
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")

# Navigation
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio(
    "Select a page:",
    ["Overview", "Play Counts", "Library Growth", "Seasonal Trends", "Artist Analysis", "Data Management"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")


# ============================================================================
# MAIN CONTENT
# ============================================================================

try:
    # Load data
    metadata, activity = load_data(DB_PATH, apply_cleaning)
    
    if metadata.empty or activity.empty:
        st.error("❌ Failed to load data from database. Please check the database path and try again.")
        st.stop()
    
    # ====== PAGE: OVERVIEW ======
    if page == "Overview":
        st.header("📊 Library Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Songs", f"{len(metadata):,}")
        
        with col2:
            st.metric("Total Artists", f"{metadata['artist'].nunique():,}")
        
        with col3:
            total_plays = activity['play_count'].sum()
            st.metric("Total Plays", f"{total_plays:,}")
        
        with col4:
            date_added = pd.to_datetime(metadata['date_added_simple'])
            years_span = (date_added.max() - date_added.min()).days / 365.25
            st.metric("Library Span", f"{years_span:.1f} years")
        
        st.markdown("---")
        
        # Top songs and artists
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top 10 Most Played Songs")
            top_songs = get_top_tracks(activity, metadata, n=10)
            display_songs = top_songs[['title', 'artist', 'total_plays']].copy()
            display_songs.columns = ['Title', 'Artist', 'Plays']
            st.dataframe(display_songs, use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader("👥 Top 10 Artists")
            top_artists_df = get_top_artists(activity, metadata, n=10)
            display_artists = top_artists_df[['artist', 'total_plays', 'n_songs']].copy()
            display_artists.columns = ['Artist', 'Plays', 'Songs']
            st.dataframe(display_artists, use_container_width=True, hide_index=True)
        
        # Recent additions
        st.subheader("📅 Recently Added Songs")
        recent = metadata.nlargest(10, 'date_added')[['title', 'artist', 'album', 'date_added_simple']].copy()
        recent.columns = ['Title', 'Artist', 'Album', 'Date Added']
        st.dataframe(recent, use_container_width=True, hide_index=True)
    
    
    # ====== PAGE: PLAY COUNTS ======
    elif page == "Play Counts":
        st.header("▶️ Play Count Analysis")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            show_stats = st.checkbox("Show Statistics", value=True)
        
        # Main plot
        st.subheader("Plays Over Time")
        fig_plays = plot_cumulative_plays_over_time(activity)
        st.plotly_chart(fig_plays, use_container_width=True)
        
        # Distribution and stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Play Distribution")
            fig_dist = plot_plays_distribution(activity)
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with col2:
            st.subheader("📈 Statistics")
            play_counts = activity['play_count']
            stats_data = {
                'Metric': [
                    'Total Plays', 'Average per Song', 'Median Plays',
                    'Max Plays', 'Min Plays', 'Std Deviation'
                ],
                'Value': [
                    f"{play_counts.sum():,}",
                    f"{play_counts.mean():.2f}",
                    f"{play_counts.median():.0f}",
                    f"{play_counts.max():.0f}",
                    f"{play_counts.min():.0f}",
                    f"{play_counts.std():.2f}"
                ]
            }
            st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)
        
        # Active periods
        st.subheader("🔥 Most Active Listening Periods")
        library_stats = get_library_stats_by_date(activity, metadata)
        top_periods = library_stats.nlargest(10, 'total_plays')[
            ['library_date', 'total_plays', 'n_songs_played']
        ].copy()
        top_periods.columns = ['Date', 'Total Plays', 'Unique Songs']
        st.dataframe(top_periods, use_container_width=True, hide_index=True)
    
    
    # ====== PAGE: LIBRARY GROWTH ======
    elif page == "Library Growth":
        st.header("📈 Library Growth Over Time")
        
        # Cumulative library size
        st.subheader("Library Growth")
        fig_size = plot_cumulative_library_size(metadata)
        st.plotly_chart(fig_size, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Monthly Additions")
            fig_additions = plot_new_additions_per_month(metadata)
            st.plotly_chart(fig_additions, use_container_width=True)
        
        with col2:
            st.subheader("Artist Growth")
            fig_artist_growth = plot_artist_growth(metadata)
            st.plotly_chart(fig_artist_growth, use_container_width=True)
        
        # Growth statistics
        st.subheader("📊 Growth Statistics")
        lib_growth = get_library_growth(metadata)
        date_added = pd.to_datetime(metadata['date_added_simple'])
        min_date = date_added.min()
        max_date = date_added.max()
        time_span_days = (max_date - min_date).days
        
        stats_data = {
            'Metric': [
                'First Song Added',
                'Last Song Added',
                'Time Span (Years)',
                'Total Songs',
                'Avg Additions/Day',
                'Total Artists'
            ],
            'Value': [
                str(min_date.date()),
                str(max_date.date()),
                f"{time_span_days / 365.25:.1f}",
                f"{len(metadata):,}",
                f"{len(metadata) / max(time_span_days, 1):.2f}",
                f"{metadata['artist'].nunique():,}"
            ]
        }
        st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)
    
    
    # ====== PAGE: SEASONAL TRENDS ======
    elif page == "Seasonal Trends":
        st.header("🌍 Seasonal Listening Trends")
        
        # Metric selector
        metric = st.radio(
            "Select Metric:",
            ["plays", "skips"],
            horizontal=True,
            index=0
        )
        metric_display = "Play Count" if metric == "plays" else "Skip Count"
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"By Month ({metric_display})")
            fig_month = plot_seasonal_trends_by_month(activity, metric=metric)
            st.plotly_chart(fig_month, use_container_width=True)
        
        with col2:
            st.subheader(f"By Season ({metric_display})")
            fig_season = plot_seasonal_trends_by_season(activity, metric=metric)
            st.plotly_chart(fig_season, use_container_width=True)
        
        # Year-over-year
        st.subheader(f"Year-over-Year Comparison ({metric_display})")
        fig_yoy = plot_year_over_year_comparison(activity, metric=metric)
        st.plotly_chart(fig_yoy, use_container_width=True)
    
    
    # ====== PAGE: ARTIST ANALYSIS ======
    elif page == "Artist Analysis":
        st.header("👥 Artist Analysis")
        
        # Artist selector
        artists = sorted(metadata['artist'].dropna().unique())
        selected_artist = st.selectbox("Select Artist:", artists)
        
        if selected_artist:
            # Artist play history
            st.subheader(f"Play History - {selected_artist}")
            fig_history = plot_artist_play_history(activity, metadata, selected_artist)
            st.plotly_chart(fig_history, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"Songs by {selected_artist}")
                artist_songs = metadata[metadata['artist'] == selected_artist].copy()
                
                # Merge with play counts
                artist_activity = activity.merge(
                    artist_songs[['persistent_id']], on='persistent_id'
                ).groupby('persistent_id').agg({
                    'play_count': 'sum',
                    'skip_count': 'sum'
                }).reset_index()
                
                song_stats = artist_songs.merge(
                    artist_activity, on='persistent_id', how='left'
                )[['title', 'album', 'year', 'play_count', 'skip_count']].fillna(0)
                song_stats.columns = ['Title', 'Album', 'Year', 'Plays', 'Skips']
                song_stats['Plays'] = song_stats['Plays'].astype(int)
                song_stats['Skips'] = song_stats['Skips'].astype(int)
                
                st.dataframe(
                    song_stats.sort_values('Plays', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
            
            with col2:
                st.subheader("Artist Statistics")
                artist_stats = get_artist_statistics(metadata, activity)
                artist_row = artist_stats[artist_stats['artist'] == selected_artist]
                
                if not artist_row.empty:
                    row = artist_row.iloc[0]
                    stats_data = {
                        'Metric': ['Total Plays', 'Avg per Song', 'Max Single Song', 'Number of Songs'],
                        'Value': [
                            f"{int(row['total_plays']):,}",
                            f"{row['avg_plays_per_song']:.2f}",
                            f"{int(row['max_plays_single_song'])}",
                            f"{int(row['n_songs'])}"
                        ]
                    }
                    st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)
        
        # Top artists comparison
        st.markdown("---")
        st.subheader("Top 10 Artists - Comparison")
        fig_comparison = plot_top_artists_comparison(activity, metadata, n_artists=10)
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    
    # ====== PAGE: DATA MANAGEMENT ======
    elif page == "Data Management":
        st.header("⚙️ Data Management")
        
        # Database information
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Database Info")
            try:
                db_info = get_database_info(DB_PATH)
                info_data = {
                    'Property': [
                        'File Size (MB)',
                        'Tables',
                        'Metadata Records',
                        'Activity Records'
                    ],
                    'Value': [
                        f"{db_info['file_size_mb']:.2f}",
                        ', '.join(db_info['tables']),
                        f"{db_info['records'].get('metaMusic', 0):,}",
                        f"{db_info['records'].get('activity', 0):,}"
                    ]
                }
                st.dataframe(pd.DataFrame(info_data), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error retrieving database info: {e}")
        
        with col2:
            st.subheader("Data Quality")
            total_records = len(activity)
            records_with_plays = (activity['play_count'] > 0).sum()
            coverage = (records_with_plays / total_records * 100) if total_records > 0 else 0
            
            quality_data = {
                'Metric': [
                    'Total Records',
                    'Records with Plays',
                    'Coverage %',
                    'Null Play Counts',
                    'Null Skip Counts'
                ],
                'Value': [
                    f"{total_records:,}",
                    f"{records_with_plays:,}",
                    f"{coverage:.1f}%",
                    str(activity['play_count'].isnull().sum()),
                    str(activity['skip_count'].isnull().sum())
                ]
            }
            st.dataframe(pd.DataFrame(quality_data), use_container_width=True, hide_index=True)
        
        # Consistency checks
        st.markdown("---")
        st.subheader("🔍 Data Consistency Report")
        
        if st.button("Generate Report", use_container_width=True):
            with st.spinner("Generating report..."):
                report = generate_consistency_report(metadata, activity)
                st.code(report, language="text")
        
        # Duplicate artists
        st.markdown("---")
        st.subheader("⚠️ Potential Duplicate Artists")
        
        if st.button("Identify Duplicates", use_container_width=True):
            with st.spinner("Analyzing artist names..."):
                duplicates = identify_duplicate_artists(metadata)
                
                if not duplicates.empty:
                    st.dataframe(duplicates, use_container_width=True, hide_index=True)
                    
                    st.warning(
                        f"Found {len(duplicates)} potential duplicate artist names. "
                        "Consider standardizing these for better analysis."
                    )
                else:
                    st.success("No significant duplicate artist names detected.")
        
        # Data cleaning preview
        st.markdown("---")
        st.subheader("🧹 Data Cleaning Preview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Clean Artist Names", use_container_width=True):
                cleaned = clean_artist_names(metadata)
                st.write("Sample of cleaned artist names:")
                st.dataframe(
                    cleaned[['artist']].drop_duplicates().head(10),
                    use_container_width=True,
                    hide_index=True
                )
        
        with col2:
            if st.button("Clean Track Names", use_container_width=True):
                cleaned = clean_track_names(metadata)
                st.write("Sample of cleaned track names:")
                st.dataframe(
                    cleaned[['title']].drop_duplicates().head(10),
                    use_container_width=True,
                    hide_index=True
                )

except FileNotFoundError as e:
    st.error(f"❌ Database not found: {e}")
    st.info(f"Make sure the iTunes.db database is in the project root or set the ITUNES_DB_PATH environment variable.")
    
except Exception as e:
    st.error(f"❌ An error occurred: {str(e)}")
    st.info("Please check the error message above and try again.")
    import traceback
    with st.expander("Show detailed error"):
        st.code(traceback.format_exc())
