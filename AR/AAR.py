import pandas as pd
import numpy as np

# 1. Load the data
file_path = r'C:\Users\Jonas\code\vscode\quant_fin\data_stocks_4.csv'
df = pd.read_csv(file_path)

# 2. Parse the 'date' column into actual datetimes
parsed_dates = pd.to_datetime(df['date'], format='%m/%d/%y')
df['date'] = parsed_dates

# 3. Make sure the rows are sorted by ticker and date
df = df.sort_values(['TICKER', 'date'])

# 4. Compute the previous day's closing price for each stock
prev_prices = df.groupby('TICKER')['Price'].shift(1)
df['prev_price'] = prev_prices

# 5. Compute the stock’s total raw return each day (price change plus any dividend)
#    R_stock = (P_t + D_t) / P_{t-1} - 1
price_plus_dividends = df['Price'] + df['Dividends']
raw_return = price_plus_dividends / df['prev_price'] - 1
df['stock_return'] = raw_return

# 6. Compute the abnormal return as the difference from the market return
market_return = df['Market Return']
abnormal_return = raw_return - market_return
df['abnormal_return'] = abnormal_return

# 7. Define the known announcement dates for each ticker
announcement_dates = {
    'CEA': '1981-04-15',  # CESSNA AIRCRAFT
    'BONT': '2007-03-29', # BON TON STORES
    'GBX': '2014-07-02',  # GREENBRIER COMPANIES
    'GES': '2012-11-28'   # GUESS
}

# 8. For each stock, pick out the announcement-day row and record its abnormal return
records = []
for ticker, date_str in announcement_dates.items():
    announcement_date = pd.to_datetime(date_str)
    ticker_mask = df['TICKER'] == ticker
    date_mask = df['date'] == announcement_date
    subset = df.loc[ticker_mask & date_mask]
    if not subset.empty:
        ar_value = subset['abnormal_return'].iloc[0]
    else:
        ar_value = None
    records.append({
        'Ticker': ticker,
        'Announcement Date': date_str,
        'Abnormal Return': ar_value
    })

# 9. Build the results DataFrame and print individual abnormal returns.
results_df = pd.DataFrame(records)
print("Individual Abnormal Returns on Announcement Dates:")
print(results_df.to_string(index=False))

# 10. Compute the Average Abnormal Return (AAR) across all 4 stocks.
#     AAR_t = (1/N) * sum_{i=1}^{N} AR_it.
abnormal_return_series = results_df['Abnormal Return']
aar = abnormal_return_series.mean()

aar_formatted = f"{aar:.4%}"
print("\nAverage Abnormal Return (AAR) across all 4 stocks:")
print(aar_formatted)

# ----------------------------
# Part (c): Compute daily abnormal returns for each stock
# from Day -10 to Day +10, using only business days (excluding weekends and given holidays).
# Then compute the AAR for each event day.
# ----------------------------

# Define the list of holidays to exclude
holidays = [pd.to_datetime('1981-04-17'),
            pd.to_datetime('2007-04-06'),
            pd.to_datetime('2012-11-22'),
            pd.to_datetime('2014-07-04')]

# Create a custom business day offset that excludes those holidays.
custom_bday = pd.offsets.CustomBusinessDay(holidays=holidays)

# Define the event window from Day -10 to Day +10.
event_window = range(-10, 11)

# For each stock, for each day in the event window, get the abnormal return.
ticker_events = {}
for ticker, date_str in announcement_dates.items():
    event_date = pd.to_datetime(date_str)
    day_returns = {}
    for offset in event_window:
        # Compute the event day using the custom business day offset.
        event_day = event_date + offset * custom_bday
        mask = (df['TICKER'] == ticker) & (df['date'] == event_day)
        subset = df.loc[mask]
        if not subset.empty:
            ar = subset['abnormal_return'].iloc[0]
        else:
            ar = np.nan  # Use NaN if data is missing.
        day_returns[offset] = ar
    ticker_events[ticker] = day_returns

# Compute the AAR on each event day (averaging across stocks)
aar_dict = {}
for offset in event_window:
    values = [ticker_events[ticker][offset] for ticker in ticker_events]
    aar_value = np.nanmean(values)  # Compute mean, ignoring NaN's.
    aar_dict[offset] = aar_value

print("\nEvent Study: Average Abnormal Returns (AAR) by Event Day:")
for offset in sorted(aar_dict.keys()):
    print(f"Day {offset}: {aar_dict[offset]:.4%}")

# (c) What is the AAR on Day -10?
print("\nAAR on Day -10:")
print(f"{aar_dict[-10]:.4%}")

# ----------------------------
# Part (d): What is the AAR on Day +10?
# ----------------------------
print("\nAAR on Day +10:")
print(f"{aar_dict[10]:.4%}")

# ----------------------------
# Part (e): Compute CAAR from Day -10 to Day -1
# ----------------------------
# Define the event window for CAAR (Day -10 to Day -1)
caar_window = range(-10, 0)
# Sum the AAR values from Day -10 to Day -1
caar = sum(aar_dict[offset] for offset in caar_window)
print("\nCumulative Average Abnormal Return (CAAR) from Day -10 to Day -1:")
print(f"{caar:.4%}")

# ----------------------------
# Part (f): Compute CAAR from Day +1 to Day +10
# ----------------------------
# Define the event window for positive CAAR (Day +1 to Day +10)
caar_positive_window = range(1, 11)
# Sum the AAR values from Day +1 to Day +10
caar_positive = sum(aar_dict[offset] for offset in caar_positive_window)
print("\nCumulative Average Abnormal Return (CAAR) from Day +1 to Day +10:")
print(f"{caar_positive:.4%}")

# ----------------------------
# Part (g): Compute cumulative CAAR starting on Day -1 and ending on Day +10, and plot the graph.
# ----------------------------
import matplotlib.pyplot as plt

# Compute cumulative CAAR starting at Day -1 for each day from -1 to +10.
# That is, for each event day t in [-1, 0, 1, ..., 10],
# CAAR(-1, t) = sum_{d=-1}^{t} AAR_d.
caar_cumulative = {}
for day in range(-1, 11):
    cumulative_sum = sum(aar_dict[d] for d in range(-1, day+1))
    caar_cumulative[day] = cumulative_sum

# Prepare data for plotting.
days = sorted(caar_cumulative.keys())
caar_values = [caar_cumulative[day] for day in days]

plt.figure(figsize=(8, 6))
plt.plot(days, caar_values, marker='o', linestyle='-', color='b')
plt.xlabel('Event Day')
plt.ylabel('Cumulative Average Abnormal Return (CAAR)')
plt.title('Cumulative CAAR from Day -1 to Day +10')
plt.grid(True)
plt.show()
