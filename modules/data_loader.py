"""
Data Loading Module
Functions for connecting to and loading data from the iTunes SQLite database.
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Optional
from datetime import datetime


def connect_db(db_path: str) -> sqlite3.Connection:
    """
    Create a connection to the SQLite database.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        sqlite3.Connection object
        
    Raises:
        FileNotFoundError: If database file doesn't exist
    """
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def load_music_data(
    db_path: str, 
    apply_cleaning: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load music metadata and activity data from the iTunes database.
    
    Args:
        db_path: Path to the SQLite database file
        apply_cleaning: Whether to apply data cleaning transformations
        
    Returns:
        Tuple of (metadata_df, activity_df)
        
    Raises:
        Exception: If database connection or query fails
    """
    try:
        conn = connect_db(db_path)
        
        # Load metadata
        metadata = pd.read_sql_query(
            "SELECT * FROM metaMusic ORDER BY persistent_id",
            conn
        )
        
        # Load activity
        activity = pd.read_sql_query(
            "SELECT * FROM activity ORDER BY persistent_id, library_date",
            conn
        )
        
        conn.close()
        
        # Convert date columns
        if not metadata.empty:
            metadata['date_added'] = pd.to_datetime(metadata['date_added'], errors='coerce')
            metadata['date_added_simple'] = pd.to_datetime(metadata['date_added_simple'], errors='coerce')
        
        if not activity.empty:
            activity['library_date'] = pd.to_datetime(activity['library_date'], errors='coerce')
        
        # Apply cleaning if requested
        if apply_cleaning:
            metadata = clean_metadata(metadata)
            activity = clean_activity(activity)
        
        return metadata, activity
        
    except Exception as e:
        raise Exception(f"Error loading data from database: {str(e)}")


def clean_metadata(metadata: pd.DataFrame) -> pd.DataFrame:
    """
    Apply cleaning transformations to metadata.
    
    Args:
        metadata: Raw metadata dataframe
        
    Returns:
        Cleaned metadata dataframe
    """
    df = metadata.copy()
    
    # Standardize column names
    df.columns = df.columns.str.lower()
    
    # Check which required columns exist before processing
    required_cols = ['persistent_id', 'title', 'artist']
    existing_required = [col for col in required_cols if col in df.columns]
    
    # Only try to process numeric columns that exist
    numeric_cols = ['total_time', 'track_number', 'disc_number', 'year', 'track_count', 'disc_count']
    for col in numeric_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except (ValueError, TypeError):
                pass
    
    # Remove records with missing essential info (only if those columns exist)
    if existing_required:
        df = df.dropna(subset=existing_required, how='any')
    
    return df.reset_index(drop=True)


def clean_activity(activity: pd.DataFrame) -> pd.DataFrame:
    """
    Apply cleaning transformations to activity data.
    
    Args:
        activity: Raw activity dataframe
        
    Returns:
        Cleaned activity dataframe
    """
    df = activity.copy()
    
    # Standardize column names to lowercase
    df.columns = df.columns.str.lower()
    
    # Check which count columns exist and handle them
    if 'play_count' in df.columns:
        df['play_count'] = df['play_count'].fillna(0)
        try:
            df['play_count'] = df['play_count'].astype(int)
        except (ValueError, TypeError):
            df['play_count'] = pd.to_numeric(df['play_count'], errors='coerce').fillna(0).astype(int)
    
    if 'skip_count' in df.columns:
        df['skip_count'] = df['skip_count'].fillna(0)
        try:
            df['skip_count'] = df['skip_count'].astype(int)
        except (ValueError, TypeError):
            df['skip_count'] = pd.to_numeric(df['skip_count'], errors='coerce').fillna(0).astype(int)
    
    # Remove invalid records
    required_cols = ['persistent_id', 'library_date']
    existing_required = [col for col in required_cols if col in df.columns]
    if existing_required:
        df = df.dropna(subset=existing_required, how='any')
    
    # Sort by tracking ids and date for differential calculations
    if 'persistent_id' in df.columns and 'library_date' in df.columns:
        df = df.sort_values(['persistent_id', 'library_date']).reset_index(drop=True)
    
    return df


def calculate_play_differential(activity: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the change in play count between consecutive snapshots for each track.
    
    Args:
        activity: Activity dataframe (should be sorted by persistent_id, library_date)
        
    Returns:
        Activity dataframe with added play_differential column
    """
    df = activity.copy()
    
    df['play_differential'] = df.groupby('persistent_id')['play_count'].diff().fillna(0)
    # Remove negative differentials (shouldn't happen in normal data)
    df['play_differential'] = df['play_differential'].clip(lower=0)
    
    return df


def get_top_tracks(
    activity: pd.DataFrame,
    metadata: pd.DataFrame,
    n: int = 25
) -> pd.DataFrame:
    """
    Get the most played tracks based on activity data.
    
    Args:
        activity: Activity dataframe
        metadata: Metadata dataframe
        n: Number of top tracks to return
        
    Returns:
        DataFrame with top tracks and their statistics
    """
    top = (
        activity
        .groupby('persistent_id')
        .agg({
            'play_count': 'sum',
            'skip_count': 'sum',
            'library_date': ['min', 'max', 'count']
        })
        .reset_index()
    )
    
    top.columns = ['persistent_id', 'total_plays', 'total_skips', 'first_played', 'last_played', 'snapshots']
    
    # Join with metadata
    top = top.merge(
        metadata[['persistent_id', 'title', 'artist', 'album', 'year']],
        on='persistent_id',
        how='left'
    )
    
    return top.sort_values('total_plays', ascending=False).head(n).reset_index(drop=True)


def get_top_artists(
    activity: pd.DataFrame,
    metadata: pd.DataFrame,
    n: int = 25
) -> pd.DataFrame:
    """
    Get the most played artists based on activity data.
    
    Args:
        activity: Activity dataframe
        metadata: Metadata dataframe
        n: Number of top artists to return
        
    Returns:
        DataFrame with top artists and their statistics
    """
    # Merge activity with artist info
    combined = activity.merge(
        metadata[['persistent_id', 'artist']],
        on='persistent_id',
        how='left'
    )
    
    top = (
        combined
        .groupby('artist')
        .agg({
            'play_count': 'sum',
            'skip_count': 'sum',
            'persistent_id': 'nunique'
        })
        .reset_index()
    )
    
    top.columns = ['artist', 'total_plays', 'total_skips', 'n_songs']
    
    return top.sort_values('total_plays', ascending=False).head(n).reset_index(drop=True)


def get_library_stats_by_date(
    activity: pd.DataFrame,
    metadata: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate aggregate statistics for each library snapshot.
    
    Args:
        activity: Activity dataframe
        metadata: Metadata dataframe
        
    Returns:
        DataFrame with daily statistics
    """
    combined = activity.merge(
        metadata[['persistent_id', 'artist']],
        on='persistent_id',
        how='left'
    )
    
    stats = (
        combined
        .groupby('library_date')
        .agg({
            'play_count': 'sum',
            'skip_count': 'sum',
            'persistent_id': 'nunique',
            'artist': 'nunique'
        })
        .reset_index()
    )
    
    stats.columns = ['library_date', 'total_plays', 'total_skips', 'n_songs_played', 'n_artists']
    
    # Calculate averages
    stats['avg_plays_per_song'] = (stats['total_plays'] / stats['n_songs_played']).fillna(0)
    
    return stats.sort_values('library_date').reset_index(drop=True)


def get_library_growth(metadata: pd.DataFrame) -> pd.DataFrame:
    """
    Track the cumulative growth of the music library over time.
    
    Args:
        metadata: Metadata dataframe with date_added_simple column
        
    Returns:
        DataFrame with cumulative library size over time
    """
    df = (
        metadata
        .dropna(subset=['date_added_simple'])
        .sort_values('date_added_simple')
        .copy()
    )
    
    df['cumulative_songs'] = range(1, len(df) + 1)
    df['year'] = df['date_added_simple'].dt.year
    df['month'] = df['date_added_simple'].dt.month
    df['year_month'] = df['date_added_simple'].dt.to_period('M')
    
    return df.reset_index(drop=True)


def get_database_info(db_path: str) -> Dict:
    """
    Get information about the database (size, tables, record counts).
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        Dictionary with database information
    """
    try:
        conn = connect_db(db_path)
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        info = {
            'path': db_path,
            'file_size_mb': Path(db_path).stat().st_size / (1024 * 1024),
            'tables': tables,
            'records': {}
        }
        
        # Get record counts for each table
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            info['records'][table] = count
        
        conn.close()
        return info
        
    except Exception as e:
        raise Exception(f"Error getting database info: {str(e)}")


def query_database(db_path: str, query: str) -> pd.DataFrame:
    """
    Execute a custom SQL query against the database.
    
    Args:
        db_path: Path to the SQLite database file
        query: SQL query string
        
    Returns:
        DataFrame with query results
    """
    try:
        conn = connect_db(db_path)
        result = pd.read_sql_query(query, conn)
        conn.close()
        return result
    except Exception as e:
        raise Exception(f"Query error: {str(e)}")
