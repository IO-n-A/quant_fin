import pandas as pd
import numpy as np
from datetime import datetime
from dateutil import parser
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

def load_data(filepath):
    # Try to find the header row by searching for a row containing all required columns
    with open(filepath, encoding='utf-8') as f:
        lines = f.readlines()
    header_row = None
    for i, line in enumerate(lines):
        # Remove quotes and split by semicolon
        cols = [col.strip().replace('"', '') for col in line.strip().split(';')]
        # Check for a date and amount column
        if any('Datum' in c or 'Date' in c or 'Buchungsdatum' in c for c in cols) and \
           any('Betrag' in c or 'Amount' in c for c in cols):
            header_row = i
            break
    if header_row is None:
        return pd.DataFrame(columns=['Date', 'Amount', 'Description'])
    # Now read with correct header and separator
    df = pd.read_csv(filepath, sep=';', header=header_row, encoding='utf-8', dtype=str)
    # Normalize column names
    df.columns = [c.strip().replace('"', '') for c in df.columns]
    # Date
    date_col = next((c for c in df.columns if 'Datum' in c or 'Date' in c or 'Buchungsdatum' in c), None)
    if date_col:
        df['Date'] = pd.to_datetime(df[date_col].str.replace('"','').str.strip(), errors='coerce', dayfirst=True)
    else:
        df['Date'] = pd.NaT
    # Amount
    amount_col = next((c for c in df.columns if 'Betrag' in c or 'Amount' in c), None)
    if amount_col:
        df['Amount'] = pd.to_numeric(
            df[amount_col].str.replace('"','').str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.replace('€','').str.replace(' ',''), 
            errors='coerce'
        )
    else:
        df['Amount'] = np.nan
    # Description
    desc_col = next((c for c in df.columns if 'Verwendungszweck' in c or 'Description' in c or 'Zahlungsempfänger' in c), None)
    if desc_col:
        df['Description'] = df[desc_col].astype(str)
    else:
        df['Description'] = ""
    return df.dropna(subset=['Date', 'Amount'])

# Use full paths for all files
dkb_path = r'C:\Users\Jonas\code\vscode\quant_fin\BG\DKB.csv'
fyrst_path = r'C:\Users\Jonas\code\vscode\quant_fin\BG\FYRST.csv'
paypal_path = r'C:\Users\Jonas\code\vscode\quant_fin\BG\PayPal.CSV'

dkb_df = load_data(dkb_path)
fyrst_df = load_data(fyrst_path)
paypal_df = load_data(paypal_path)

print(paypal_df.head())
print(dkb_df.head())
print(fyrst_df.head())

# Combine incoming transactions (positive amounts)
incoming = pd.concat([
    fyrst_df[fyrst_df['Amount'] > 0],
    paypal_df[paypal_df['Amount'] > 0]
], ignore_index=True)

# Only proceed if incoming is not empty
if not incoming.empty:
    incoming['Date'] = pd.to_datetime(incoming['Date'], errors='coerce')
    # 1) Calculate average monthly income
    incoming['YearMonth'] = incoming['Date'].dt.to_period('M')
    monthly_sums = incoming.groupby('YearMonth')['Amount'].sum()
    avg_monthly_income = monthly_sums.mean()
    print(f"Average monthly income: €{avg_monthly_income:.2f}")

    # 2) Identify regular vs irregular incoming payments via clustering
    incoming['Day'] = incoming['Date'].dt.day
    features = incoming[['Amount', 'Day']].values

    # Standardize features for clustering
    df_scaler = StandardScaler()
    X_scaled = df_scaler.fit_transform(features)

    # Use DBSCAN to detect clusters of regular payments
    db = DBSCAN(eps=0.5, min_samples=3)
    clusters = db.fit_predict(X_scaled)
    incoming['Cluster'] = clusters

    # Regular payments: cluster labels >= 0
    regular = incoming[incoming['Cluster'] >= 0]
    irregular = incoming[incoming['Cluster'] == -1]

    # 2a) Regular incoming payments summary
    regular_summary = regular.groupby(['Cluster', 'Description']).agg(
        count=('Amount', 'size'),
        avg_amount=('Amount', 'mean'),
        avg_day=('Day', 'mean')
    ).sort_values('count', ascending=False)
    print("\nRegular incoming payments:")
    print(regular_summary)

    # 2b) List irregular incoming payments
    print("\nIrregular incoming payments:")
    print(irregular[['Date', 'Description', 'Amount']].sort_values('Date'))

    # Optionally, save summaries to CSV
    monthly_sums.to_csv('monthly_income_summary.csv')
    regular_summary.to_csv('regular_payments_summary.csv')
    irregular.to_csv('irregular_payments_list.csv', index=False)
else:
    print("No incoming transactions found.")
