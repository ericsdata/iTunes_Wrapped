"""
Data Visualization Module
Functions for creating interactive plots and charts using Plotly.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def plot_cumulative_plays_over_time(activity: pd.DataFrame) -> go.Figure:
    """
    Create a time series plot of cumulative plays over time.
    
    Args:
        activity: Activity dataframe
        
    Returns:
        Plotly figure object
    """
    plot_data = (
        activity
        .groupby('library_date')['play_count']
        .sum()
        .reset_index()
        .sort_values('library_date')
    )
    
    plot_data['cumulative_plays'] = plot_data['play_count'].cumsum()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=plot_data['library_date'],
        y=plot_data['cumulative_plays'],
        mode='lines+markers',
        name='Total Plays',
        line=dict(color='rgb(55, 128, 191)', width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title='Cumulative Play Counts Over Time',
        xaxis_title='Date',
        yaxis_title='Total Plays',
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    
    return fig


def plot_plays_distribution(activity: pd.DataFrame) -> go.Figure:
    """
    Create a histogram showing the distribution of play counts.
    
    Args:
        activity: Activity dataframe
        
    Returns:
        Plotly figure object
    """
    play_counts = activity[activity['play_count'] > 0]['play_count']
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=play_counts,
        nbinsx=50,
        name='Play Count',
        marker=dict(color='rgb(55, 128, 191)')
    ))
    
    fig.update_layout(
        title='Distribution of Play Counts',
        xaxis_title='Plays per Song',
        yaxis_title='Frequency',
        height=350,
        template='plotly_white'
    )
    
    return fig


def plot_cumulative_library_size(metadata: pd.DataFrame) -> go.Figure:
    """
    Create a plot showing cumulative songs added over time.
    
    Args:
        metadata: Metadata dataframe
        
    Returns:
        Plotly figure object
    """
    plot_data = (
        metadata
        .dropna(subset=['date_added_simple'])
        .sort_values('date_added_simple')
        .copy()
    )
    
    plot_data['cumulative_songs'] = range(1, len(plot_data) + 1)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=plot_data['date_added_simple'],
        y=plot_data['cumulative_songs'],
        mode='lines',
        name='Library Size',
        line=dict(color='rgb(50, 171, 96)', width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title='Cumulative Songs Added Over Time',
        xaxis_title='Date',
        yaxis_title='Total Songs in Library',
        hovermode='x',
        height=400,
        template='plotly_white'
    )
    
    return fig


def plot_new_additions_per_month(metadata: pd.DataFrame) -> go.Figure:
    """
    Create a bar chart showing new additions per month.
    
    Args:
        metadata: Metadata dataframe
        
    Returns:
        Plotly figure object
    """
    plot_data = (
        metadata
        .dropna(subset=['date_added_simple'])
        .copy()
    )
    
    plot_data['year_month'] = plot_data['date_added_simple'].dt.to_period('M')
    
    monthly = (
        plot_data
        .groupby('year_month')
        .size()
        .reset_index(name='new_songs')
    )
    
    monthly['year_month'] = monthly['year_month'].astype(str)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly['year_month'],
        y=monthly['new_songs'],
        name='New Songs',
        marker=dict(color='rgb(50, 171, 96)')
    ))
    
    fig.update_layout(
        title='New Additions per Month',
        xaxis_title='Month',
        yaxis_title='Number of New Songs',
        height=350,
        template='plotly_white'
    )
    
    return fig


def plot_artist_growth(metadata: pd.DataFrame) -> go.Figure:
    """
    Create a plot showing unique artists in library over time.
    
    Args:
        metadata: Metadata dataframe
        
    Returns:
        Plotly figure object
    """
    plot_data = (
        metadata
        .dropna(subset=['date_added_simple', 'artist'])
        .sort_values('date_added_simple')
        .copy()
    )
    
    # Get cumulative unique artists
    plot_data['n_artists'] = plot_data['artist'].expanding().nunique()
    plot_data = plot_data.drop_duplicates('date_added_simple', keep='last')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=plot_data['date_added_simple'],
        y=plot_data['n_artists'],
        mode='lines',
        name='Unique Artists',
        line=dict(color='rgb(219, 112, 147)', width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title='Unique Artists in Library Over Time',
        xaxis_title='Date',
        yaxis_title='Number of Unique Artists',
        height=350,
        template='plotly_white'
    )
    
    return fig


def plot_seasonal_trends_by_month(
    activity: pd.DataFrame,
    metric: str = 'plays'
) -> go.Figure:
    """
    Create a bar chart showing seasonal trends by month.
    
    Args:
        activity: Activity dataframe
        metric: 'plays' or 'skips'
        
    Returns:
        Plotly figure object
    """
    plot_data = activity.copy()
    plot_data['month'] = plot_data['library_date'].dt.month
    
    metric_col = 'play_count' if metric == 'plays' else 'skip_count'
    
    monthly = (
        plot_data
        .groupby('month')[metric_col]
        .sum()
        .reset_index()
    )
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly['month_name'] = monthly['month'].map(lambda x: month_names[x-1] if 1 <= x <= 12 else 'Unknown')
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly['month_name'],
        y=monthly[metric_col],
        name='Metric',
        marker=dict(color='rgb(55, 128, 191)')
    ))
    
    title_map = {'plays': 'Total Plays', 'skips': 'Total Skips'}
    fig.update_layout(
        title=f'{title_map.get(metric, "Metric")} by Month',
        xaxis_title='Month',
        yaxis_title=title_map.get(metric, 'Metric'),
        height=350,
        template='plotly_white'
    )
    
    return fig


def plot_seasonal_trends_by_season(
    activity: pd.DataFrame,
    metric: str = 'plays'
) -> go.Figure:
    """
    Create a bar chart showing seasonal trends by season.
    
    Args:
        activity: Activity dataframe
        metric: 'plays' or 'skips'
        
    Returns:
        Plotly figure object
    """
    plot_data = activity.copy()
    plot_data['month'] = plot_data['library_date'].dt.month
    
    def get_season(month):
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'
    
    plot_data['season'] = plot_data['month'].apply(get_season)
    
    metric_col = 'play_count' if metric == 'plays' else 'skip_count'
    
    seasonal = (
        plot_data
        .groupby('season')[metric_col]
        .sum()
        .reset_index()
    )
    
    # Order seasons
    season_order = ['Winter', 'Spring', 'Summer', 'Fall']
    seasonal['season'] = pd.Categorical(seasonal['season'], categories=season_order, ordered=True)
    seasonal = seasonal.sort_values('season')
    
    colors = ['lightblue', 'lightgreen', 'yellow', 'orange']
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=seasonal['season'],
        y=seasonal[metric_col],
        marker=dict(color=colors),
        name='Metric'
    ))
    
    title_map = {'plays': 'Total Plays', 'skips': 'Total Skips'}
    fig.update_layout(
        title=f'{title_map.get(metric, "Metric")} by Season',
        xaxis_title='Season',
        yaxis_title=title_map.get(metric, 'Metric'),
        height=350,
        template='plotly_white'
    )
    
    return fig


def plot_year_over_year_comparison(
    activity: pd.DataFrame,
    metric: str = 'plays'
) -> go.Figure:
    """
    Create a line plot showing year-over-year comparison.
    
    Args:
        activity: Activity dataframe
        metric: 'plays' or 'skips'
        
    Returns:
        Plotly figure object
    """
    plot_data = activity.copy()
    plot_data['year'] = plot_data['library_date'].dt.year
    plot_data['month'] = plot_data['library_date'].dt.month
    
    metric_col = 'play_count' if metric == 'plays' else 'skip_count'
    
    yearly = (
        plot_data
        .groupby(['year', 'month'])[metric_col]
        .sum()
        .reset_index()
    )
    
    fig = go.Figure()
    
    for year in yearly['year'].unique():
        year_data = yearly[yearly['year'] == year].sort_values('month')
        fig.add_trace(go.Scatter(
            x=year_data['month'],
            y=year_data[metric_col],
            mode='lines+markers',
            name=str(int(year))
        ))
    
    title_map = {'plays': 'Total Plays', 'skips': 'Total Skips'}
    fig.update_layout(
        title=f'Year-over-Year {title_map.get(metric, "Metric")} Comparison',
        xaxis_title='Month',
        yaxis_title=title_map.get(metric, 'Metric'),
        height=400,
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig


def plot_artist_play_history(
    activity: pd.DataFrame,
    metadata: pd.DataFrame,
    artist: str
) -> go.Figure:
    """
    Create a plot showing play history for a specific artist.
    
    Args:
        activity: Activity dataframe
        metadata: Metadata dataframe
        artist: Artist name
        
    Returns:
        Plotly figure object
    """
    # Get track IDs for artist
    artist_tracks = metadata[metadata['artist'] == artist]['persistent_id'].unique()
    
    # Filter activity for artist
    plot_data = (
        activity[activity['persistent_id'].isin(artist_tracks)]
        .groupby('library_date')['play_count']
        .sum()
        .reset_index()
        .sort_values('library_date')
    )
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=plot_data['library_date'],
        y=plot_data['play_count'],
        mode='lines+markers',
        name=artist,
        line=dict(width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title=f'Play History for {artist}',
        xaxis_title='Date',
        yaxis_title='Total Plays',
        height=400,
        template='plotly_white'
    )
    
    return fig


def plot_top_artists_comparison(
    activity: pd.DataFrame,
    metadata: pd.DataFrame,
    n_artists: int = 10
) -> go.Figure:
    """
    Create a multi-line plot comparing top artists over time.
    
    Args:
        activity: Activity dataframe
        metadata: Metadata dataframe
        n_artists: Number of top artists to include
        
    Returns:
        Plotly figure object
    """
    # Get top artists
    top_artists = (
        activity
        .merge(metadata[['persistent_id', 'artist']], on='persistent_id')
        .groupby('artist')['play_count']
        .sum()
        .nlargest(n_artists)
        .index.tolist()
    )
    
    # Get time series for top artists
    plot_data = (
        activity
        .merge(metadata[['persistent_id', 'artist']], on='persistent_id')
        .filter(['library_date', 'artist', 'play_count'])
        [lambda x: x['artist'].isin(top_artists)]
        .groupby(['library_date', 'artist'])['play_count']
        .sum()
        .reset_index()
    )
    
    fig = go.Figure()
    
    for artist in top_artists:
        artist_data = plot_data[plot_data['artist'] == artist].sort_values('library_date')
        fig.add_trace(go.Scatter(
            x=artist_data['library_date'],
            y=artist_data['play_count'],
            mode='lines',
            name=artist
        ))
    
    fig.update_layout(
        title='Top 10 Artists - Play Trend Comparison',
        xaxis_title='Date',
        yaxis_title='Total Plays',
        height=400,
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig
