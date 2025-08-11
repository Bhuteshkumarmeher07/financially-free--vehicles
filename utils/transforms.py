# These will handle YoY/QoQ calculations and filtering
import pandas as pd
import numpy as np

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['date']).dt.to_period('M').dt.to_timestamp()
    df['vehicle_category'] = df['vehicle_category'].astype(str).str.upper()
    df['manufacturer'] = df['manufacturer'].astype(str).str.strip()
    df['registrations'] = pd.to_numeric(df['registrations'], errors='coerce').fillna(0).astype(int)
    return df

def add_quarter(df: pd.DataFrame) -> pd.DataFrame:
    df['quarter'] = df['date'].dt.to_period('Q')
    return df

def yoy_qoq_growth(df: pd.DataFrame, group_cols):
    df = df.copy()
    df = add_quarter(df)
    grouped = df.groupby(['quarter'] + group_cols, as_index=False)['registrations'].sum()
    grouped['prev_q'] = grouped.groupby(group_cols)['registrations'].shift(1)
    grouped['qoq_pct'] = np.where(grouped['prev_q'] > 0, 
                                  (grouped['registrations'] - grouped['prev_q']) / grouped['prev_q'] * 100, np.nan)
    grouped['prev_y'] = grouped.groupby(group_cols)['registrations'].shift(4)
    grouped['yoy_pct'] = np.where(grouped['prev_y'] > 0, 
                                  (grouped['registrations'] - grouped['prev_y']) / grouped['prev_y'] * 100, np.nan)
    return grouped
