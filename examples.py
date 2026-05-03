"""
Example usage of iTunes Wrapped modules.
This script demonstrates how to use the data loading, visualization, and cleaning modules
directly in Python scripts or notebooks.

Run this from the project root directory:
    python examples.py
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / 'modules'))

from data_loader import (
    load_music_data, get_top_tracks, get_top_artists, 
    get_library_growth, get_library_stats_by_date
)
from data_cleaning import (
    identify_duplicate_artists, generate_consistency_report,
    get_artist_statistics, clean_artist_names
)
from visualizations import (
    plot_cumulative_plays_over_time, plot_cumulative_library_size
)

# Database path
DB_PATH = "iTunes.db"


def example_1_basic_loading():
    """Example 1: Load data and display basic statistics."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Data Loading")
    print("="*60 + "\n")
    
    try:
        metadata, activity = load_music_data(DB_PATH, apply_cleaning=True)
        
        print(f"✓ Loaded {len(metadata):,} songs")
        print(f"✓ Loaded {len(activity):,} activity records")
        print(f"✓ Found {metadata['artist'].nunique():,} unique artists")
        print(f"✓ Total plays: {activity['play_count'].sum():,}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_2_top_tracks():
    """Example 2: Get and display top tracks."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Top 10 Most Played Tracks")
    print("="*60 + "\n")
    
    try:
        metadata, activity = load_music_data(DB_PATH, apply_cleaning=True)
        top_tracks = get_top_tracks(activity, metadata, n=10)
        
        print(f"{'Rank':<6} {'Title':<30} {'Artist':<20} {'Plays':<8}")
        print("-" * 64)
        
        for idx, row in top_tracks.iterrows():
            rank = idx + 1
            title = row['title'][:28]
            artist = row['artist'][:18]
            plays = int(row['total_plays'])
            print(f"{rank:<6} {title:<30} {artist:<20} {plays:<8}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_3_top_artists():
    """Example 3: Get and display top artists."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Top 10 Artists")
    print("="*60 + "\n")
    
    try:
        metadata, activity = load_music_data(DB_PATH, apply_cleaning=True)
        top_artists = get_top_artists(activity, metadata, n=10)
        
        print(f"{'Rank':<6} {'Artist':<25} {'Plays':<10} {'Songs':<8}")
        print("-" * 49)
        
        for idx, row in top_artists.iterrows():
            rank = idx + 1
            artist = row['artist'][:23]
            plays = int(row['total_plays'])
            n_songs = int(row['n_songs'])
            print(f"{rank:<6} {artist:<25} {plays:<10} {n_songs:<8}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_4_library_growth():
    """Example 4: Analyze library growth."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Library Growth Timeline")
    print("="*60 + "\n")
    
    try:
        metadata, _ = load_music_data(DB_PATH, apply_cleaning=True)
        growth = get_library_growth(metadata)
        
        # Get yearly summary
        yearly = growth.groupby('year').agg({
            'cumulative_songs': 'max',
            'artist': 'nunique'
        }).reset_index()
        
        print(f"{'Year':<8} {'Total Songs':<15} {'Total Artists':<15}")
        print("-" * 38)
        
        for _, row in yearly.iterrows():
            year = int(row['year'])
            songs = int(row['cumulative_songs'])
            artists = int(row['artist'])
            print(f"{year:<8} {songs:<15} {artists:<15}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_5_data_cleaning():
    """Example 5: Data cleaning and consistency checks."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Data Cleaning & Consistency Checks")
    print("="*60 + "\n")
    
    try:
        metadata, activity = load_music_data(DB_PATH, apply_cleaning=True)
        
        # Generate report
        print("Generating consistency report...\n")
        report = generate_consistency_report(metadata, activity)
        print(report)
        
        # Find duplicate artists
        print("\nSearching for duplicate artists...\n")
        duplicates = identify_duplicate_artists(metadata)
        
        if not duplicates.empty:
            print(f"Found {len(duplicates)} potential duplicates:\n")
            print(duplicates[['primary_name', 'variant_name', 'primary_count']].head(5))
        else:
            print("No significant duplicates found.")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_6_artist_analysis():
    """Example 6: Analyze a specific artist."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Artist Analysis (Top Artist)")
    print("="*60 + "\n")
    
    try:
        metadata, activity = load_music_data(DB_PATH, apply_cleaning=True)
        
        # Get most played artist
        top_artists = get_top_artists(activity, metadata, n=1)
        if top_artists.empty:
            print("✗ No artists found")
            return
        
        top_artist = top_artists.iloc[0]['artist']
        
        print(f"Analyzing: {top_artist}\n")
        
        # Get artist statistics
        stats = get_artist_statistics(metadata, activity)
        artist_stats = stats[stats['artist'] == top_artist]
        
        if not artist_stats.empty:
            row = artist_stats.iloc[0]
            print(f"  Total Plays: {int(row['total_plays']):,}")
            print(f"  Avg per Song: {row['avg_plays_per_song']:.1f}")
            print(f"  Max Single Song: {int(row['max_plays_single_song'])}")
            print(f"  Number of Songs: {int(row['n_songs'])}")
            
            # Get songs by this artist
            artist_songs = metadata[metadata['artist'] == top_artist].copy()
            artist_activity = activity.merge(
                artist_songs[['persistent_id']], on='persistent_id'
            ).groupby('persistent_id').agg({'play_count': 'sum'}).reset_index()
            
            top_songs = (
                artist_songs.merge(artist_activity, on='persistent_id')
                .nlargest(5, 'play_count')[['title', 'album', 'play_count']]
            )
            
            print(f"\n  Top 5 Songs by {top_artist}:")
            for idx, song in top_songs.iterrows():
                plays = int(song['play_count'])
                print(f"    - {song['title']} ({plays} plays)")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_7_data_overview():
    """Example 7: Get detailed data overview."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Detailed Data Overview")
    print("="*60 + "\n")
    
    try:
        metadata, activity = load_music_data(DB_PATH, apply_cleaning=True)
        
        # Data types and sizes
        print("Metadata Statistics:")
        print(f"  Rows: {len(metadata):,}")
        print(f"  Columns: {len(metadata.columns)}")
        print(f"  Memory: {metadata.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        print("\nActivity Statistics:")
        print(f"  Rows: {len(activity):,}")
        print(f"  Columns: {len(activity.columns)}")
        print(f"  Memory: {activity.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Column info
        print("\nMetadata Columns:")
        for col in metadata.columns:
            dtype = str(metadata[col].dtype)
            null_count = metadata[col].isnull().sum()
            print(f"  - {col:<25} ({dtype:<12}) {null_count} nulls")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Run all examples."""
    print("\n" + "🎵 "*20)
    print("iTunes Wrapped - Module Examples")
    print("🎵 "*20)
    
    examples = [
        example_1_basic_loading,
        example_2_top_tracks,
        example_3_top_artists,
        example_4_library_growth,
        example_5_data_cleaning,
        example_6_artist_analysis,
        example_7_data_overview
    ]
    
    for example_func in examples:
        try:
            example_func()
        except KeyboardInterrupt:
            print("\n\n✗ Interrupted by user")
            break
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
            continue
    
    print("\n" + "🎵 "*20 + "\n")
    print("Examples complete! Now try running the Streamlit app:")
    print("  streamlit run app.py")
    print("\n" + "🎵 "*20 + "\n")


if __name__ == "__main__":
    main()
