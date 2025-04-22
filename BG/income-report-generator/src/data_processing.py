import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from report_writer import generate_report

def load_data(filepath, date_col='Date', amount_col='Amount', desc_col='Description'):
    df = pd.read_csv(filepath, parse_dates=[date_col], dayfirst=True)
    df = df.rename(columns={date_col: 'Date', amount_col: 'Amount', desc_col: 'Description'})
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    return df.dropna(subset=['Date', 'Amount'])

def process_income_data(fyrst_filepath, paypal_filepath):
    fyrst_df = load_data(fyrst_filepath)
    paypal_df = load_data(paypal_filepath)

    incoming = pd.concat([
        fyrst_df[fyrst_df['Amount'] > 0],
        paypal_df[paypal_df['Amount'] > 0]
    ], ignore_index=True)

    incoming['YearMonth'] = incoming['Date'].dt.to_period('M')
    monthly_sums = incoming.groupby('YearMonth')['Amount'].sum()
    avg_monthly_income = monthly_sums.mean()

    incoming['Day'] = incoming['Date'].dt.day
    features = incoming[['Amount', 'Day']].values

    df_scaler = StandardScaler()
    X_scaled = df_scaler.fit_transform(features)

    db = DBSCAN(eps=0.5, min_samples=3)
    clusters = db.fit_predict(X_scaled)
    incoming['Cluster'] = clusters

    regular = incoming[incoming['Cluster'] >= 0]
    irregular = incoming[incoming['Cluster'] == -1]

    regular_summary = regular.groupby(['Cluster', 'Description']).agg(
        count=('Amount', 'size'),
        avg_amount=('Amount', 'mean'),
        avg_day=('Day', 'mean')
    ).sort_values('count', ascending=False)

    return avg_monthly_income, regular_summary, irregular

def generate_income_report(fyrst_filepath, paypal_filepath):
    avg_monthly_income, regular_summary, irregular = process_income_data(fyrst_filepath, paypal_filepath)
    generate_report(avg_monthly_income, regular_summary, irregular)