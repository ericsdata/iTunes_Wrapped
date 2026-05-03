"""
Data Cleaning Module
Functions for standardizing and cleaning artist/track names and checking data consistency.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from difflib import SequenceMatcher


def fuzzy_match_strings(
    s1: str,
    s2: str,
    threshold: float = 0.85
) -> bool:
    """
    Compare two strings using fuzzy matching.
    
    Args:
        s1: First string
        s2: Second string
        threshold: Similarity threshold (0-1)
        
    Returns:
        True if strings are similar enough
    """
    if not isinstance(s1, str) or not isinstance(s2, str):
        return False
    
    s1_clean = str(s1).lower().strip()
    s2_clean = str(s2).lower().strip()
    
    ratio = SequenceMatcher(None, s1_clean, s2_clean).ratio()
    return ratio >= threshold


def identify_duplicate_artists(metadata: pd.DataFrame) -> pd.DataFrame:
    """
    Identify likely duplicate/variant artist names using fuzzy matching.
    
    Args:
        metadata: Metadata dataframe
        
    Returns:
        DataFrame with identified duplicates
    """
    artists = metadata['artist'].dropna().unique()
    duplicates = []
    
    for i, artist1 in enumerate(artists):
        for artist2 in artists[i+1:]:
            # Skip exact matches
            if artist1.lower() == artist2.lower():
                continue
            
            # Check fuzzy match
            if fuzzy_match_strings(artist1, artist2, threshold=0.80):
                # Count occurrences
                count1 = (metadata['artist'] == artist1).sum()
                count2 = (metadata['artist'] == artist2).sum()
                
                duplicates.append({
                    'primary_name': artist1 if count1 >= count2 else artist2,
                    'variant_name': artist2 if count1 >= count2 else artist1,
                    'primary_count': max(count1, count2),
                    'variant_count': min(count1, count2),
                    'similarity_score': fuzzy_match_strings(artist1, artist2, threshold=0.0)
                })
    
    if not duplicates:
        return pd.DataFrame(columns=['primary_name', 'variant_name', 'primary_count', 'variant_count'])
    
    return (
        pd.DataFrame(duplicates)
        .drop_duplicates()
        .sort_values('primary_count', ascending=False)
        .reset_index(drop=True)
    )


def standardize_artist_names(
    metadata: pd.DataFrame,
    replacements: Dict[str, str] = None
) -> pd.DataFrame:
    """
    Standardize artist names using manual replacement mappings.
    
    Args:
        metadata: Metadata dataframe
        replacements: Dictionary mapping old names to new names
                     If None, returns dataframe unchanged
        
    Returns:
        Metadata dataframe with standardized artist names
    """
    df = metadata.copy()
    
    if replacements is None:
        replacements = {}
    
    # Apply replacements
    df['artist'] = df['artist'].replace(replacements)
    
    return df


def standardize_track_names(
    metadata: pd.DataFrame,
    replacements: Dict[str, str] = None
) -> pd.DataFrame:
    """
    Standardize track names using manual replacement mappings.
    
    Args:
        metadata: Metadata dataframe
        replacements: Dictionary mapping old names to new names
                     If None, returns dataframe unchanged
        
    Returns:
        Metadata dataframe with standardized track names
    """
    df = metadata.copy()
    
    if replacements is None:
        replacements = {}
    
    # Apply replacements
    df['title'] = df['title'].replace(replacements)
    
    return df


def clean_artist_names(metadata: pd.DataFrame) -> pd.DataFrame:
    """
    Apply common cleaning rules to artist names.
    
    Args:
        metadata: Metadata dataframe
        
    Returns:
        Cleaned metadata dataframe
    """
    df = metadata.copy()
    
    # Strip whitespace
    df['artist'] = df['artist'].str.strip()
    
    # Standardize case (title case)
    df['artist'] = df['artist'].str.title()
    
    # Remove common suffixes that shouldn't be there
    suffixes_to_remove = [
        ' (Deluxe Edition)',
        ' (Deluxe)',
        ' (Remaster)',
        ' (Explicit)',
        ' (Clean)',
        ' - Feat.',
        ' - feat.',
        ' Feat.',
        ' feat.'
    ]
    
    for suffix in suffixes_to_remove:
        df['artist'] = df['artist'].str.replace(suffix, '', regex=False)
    
    return df


def clean_track_names(metadata: pd.DataFrame) -> pd.DataFrame:
    """
    Apply common cleaning rules to track names.
    
    Args:
        metadata: Metadata dataframe
        
    Returns:
        Cleaned metadata dataframe
    """
    df = metadata.copy()
    
    # Strip whitespace
    df['title'] = df['title'].str.strip()
    
    # Remove version suffixes (commonly added by iTunes)
    version_patterns = [
        r'\s*\(Album Version\)',
        r'\s*\(Album Version Edited\)',
        r'\s*\(Explicit\)',
        r'\s*\(Clean\)',
        r'\s*\(Remaster\)',
        r'\s*\(Remastered\)',
        r'\s*- Album Version',
    ]
    
    for pattern in version_patterns:
        df['title'] = df['title'].str.replace(pattern, '', regex=True, case=False)
    
    return df


def identify_data_inconsistencies(
    metadata: pd.DataFrame,
    activity: pd.DataFrame
) -> Dict[str, List]:
    """
    Identify potential data consistency issues.
    
    Args:
        metadata: Metadata dataframe
        activity: Activity dataframe
        
    Returns:
        Dictionary with various inconsistency lists
    """
    inconsistencies = {
        'missing_metadata': [],
        'missing_activity': [],
        'null_plays': [],
        'zero_duration': [],
        'future_dates': [],
        'missing_artists': []
    }
    
    # Check for missing essential metadata
    if metadata.isnull().any():
        null_cols = metadata.columns[metadata.isnull().any()].tolist()
        inconsistencies['missing_metadata'] = null_cols
    
    # Check for orphaned activity records (persistent_ids in activity but not in metadata)
    activity_ids = set(activity['persistent_id'].unique())
    metadata_ids = set(metadata['persistent_id'].unique())
    
    orphaned = activity_ids - metadata_ids
    if orphaned:
        inconsistencies['missing_activity'] = list(orphaned)[:10]  # Show first 10
    
    # Check for songs with no plays
    null_plays = activity[activity['play_count'].isnull()].shape[0]
    if null_plays > 0:
        inconsistencies['null_plays'] = [f"{null_plays} records with NULL play_count"]
    
    # Check for songs with zero duration
    if 'total_time' in metadata.columns:
        zero_duration = metadata[metadata['total_time'] == 0].shape[0]
        if zero_duration > 0:
            inconsistencies['zero_duration'] = [f"{zero_duration} songs with zero duration"]
    
    # Check for future dates
    if 'date_added' in metadata.columns:
        pd.to_datetime(metadata['date_added'], errors='coerce')
        future_dates = metadata[metadata['date_added'] > pd.Timestamp.now()].shape[0]
        if future_dates > 0:
            inconsistencies['future_dates'] = [f"{future_dates} songs with future dates"]
    
    # Check for missing artists
    missing_artists = metadata['artist'].isnull().sum()
    if missing_artists > 0:
        inconsistencies['missing_artists'] = [f"{missing_artists} songs without artist names"]
    
    return inconsistencies


def generate_consistency_report(
    metadata: pd.DataFrame,
    activity: pd.DataFrame
) -> str:
    """
    Generate a human-readable consistency report.
    
    Args:
        metadata: Metadata dataframe
        activity: Activity dataframe
        
    Returns:
        Formatted report string
    """
    issues = identify_data_inconsistencies(metadata, activity)
    
    report = "=== Data Consistency Report ===\n\n"
    
    # Summary stats
    report += f"Total Tracks: {len(metadata):,}\n"
    report += f"Total Artists: {metadata['artist'].nunique():,}\n"
    report += f"Total Activity Records: {len(activity):,}\n"
    report += f"Date Range: {metadata['date_added'].min()} to {metadata['date_added'].max()}\n\n"
    
    # Issues found
    report += "=== Issues Found ===\n"
    
    if any(issues.values()):
        for issue_type, issue_list in issues.items():
            if issue_list:
                report += f"\n{issue_type.upper()}:\n"
                for item in issue_list:
                    report += f"  - {item}\n"
    else:
        report += "No major inconsistencies detected.\n"
    
    # Data quality percentage
    total_records = len(metadata) + len(activity)
    problematic_records = sum(len(v) for v in issues.values() if isinstance(v, list))
    quality_pct = (1 - (problematic_records / max(total_records, 1))) * 100
    
    report += f"\nEstimated Data Quality: {quality_pct:.1f}%\n"
    
    return report


def get_artist_statistics(metadata: pd.DataFrame, activity: pd.DataFrame) -> pd.DataFrame:
    """
    Get statistics about artists in the library.
    
    Args:
        metadata: Metadata dataframe
        activity: Activity dataframe
        
    Returns:
        DataFrame with artist statistics
    """
    combined = (
        activity
        .merge(metadata[['persistent_id', 'artist']], on='persistent_id')
        .groupby('artist')
        .agg({
            'play_count': ['sum', 'mean', 'max'],
            'persistent_id': 'count'
        })
        .reset_index()
    )
    
    combined.columns = ['artist', 'total_plays', 'avg_plays_per_song', 
                       'max_plays_single_song', 'n_songs']
    
    return combined.sort_values('total_plays', ascending=False)


def identify_collection_gaps(
    metadata: pd.DataFrame,
    artist: str
) -> pd.DataFrame:
    """
    For a given artist, identify their songs that are in the library
    and return basic album/year info (useful for seeing what's missing).
    
    Args:
        metadata: Metadata dataframe
        artist: Artist name to analyze
        
    Returns:
        DataFrame with artist's songs grouped by album
    """
    artist_songs = metadata[metadata['artist'] == artist].copy()
    
    if artist_songs.empty:
        return pd.DataFrame()
    
    gaps = (
        artist_songs
        .groupby(['album', 'year'])
        .agg({'title': 'count', 'persistent_id': 'count'})
        .reset_index()
        .rename(columns={'title': 'n_songs', 'persistent_id': 'n_tracks'})
        .sort_values(['year', 'album'])
    )
    
    return gaps
