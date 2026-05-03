"""
iTunes Wrapped Analysis Modules
Utilities for loading, cleaning, and visualizing iTunes library data.
"""

from .data_loader import (
    load_music_data,
    calculate_play_differential,
    get_top_tracks,
    get_top_artists,
    get_library_stats_by_date,
    get_library_growth,
    get_database_info,
    query_database
)

from .data_cleaning import (
    identify_duplicate_artists,
    standardize_artist_names,
    standardize_track_names,
    clean_artist_names,
    clean_track_names,
    identify_data_inconsistencies,
    generate_consistency_report,
    get_artist_statistics,
    identify_collection_gaps
)

__all__ = [
    # data_loader
    'load_music_data',
    'calculate_play_differential',
    'get_top_tracks',
    'get_top_artists',
    'get_library_stats_by_date',
    'get_library_growth',
    'get_database_info',
    'query_database',
    # data_cleaning
    'identify_duplicate_artists',
    'standardize_artist_names',
    'standardize_track_names',
    'clean_artist_names',
    'clean_track_names',
    'identify_data_inconsistencies',
    'generate_consistency_report',
    'get_artist_statistics',
    'identify_collection_gaps'
]
