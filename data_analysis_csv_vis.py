import pandas as pd
import os
import matplotlib as mpl
import statsmodels.api as sm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # For 3D plotting

# Set the working directory to the directory where the script is located.
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print("Working Directory:", os.getcwd())

# Check if the CSV file exists.
csv_file = "data.csv"
if not os.path.exists(csv_file):
    print(f"Error: {csv_file} not found in the working directory!")
    exit(1)

# Load the CSV file using its header and specify the decimal separator.
df = pd.read_csv(csv_file, decimal=",")

# ------------------------------------------------------------------
# Use 'companyname' as the unique firm identifier; rename to 'firm'
# ------------------------------------------------------------------
if 'companyname' in df.columns:
    df.rename(columns={'companyname': 'firm'}, inplace=True)
else:
    print("Error: 'companyname' column not found in the data.")
    exit(1)

# Compute the factor excess returns for the market and energy ETF.
df['excess_market'] = (df['r_mkt'] - df['r_f']).round(20)
df['excess_xle']    = (df['r_xle'] - df['r_f']).round(20)

# Extract year and month from 'mdate' (formatted like "1999m1")
df['year']  = df['mdate'].apply(lambda x: int(x.split('m')[0]))
df['month'] = df['mdate'].apply(lambda x: int(x.split('m')[1]))

# -----------------------------
# Fix for Parts (a) & (b): Count each month once
# -----------------------------
df_filtered = df[(df['year'] >= 1999) & (df['year'] <= 2019)]
df_monthly  = df_filtered.drop_duplicates(subset=['year','month'])

avg_market_excess = df_monthly['excess_market'].mean()
avg_etf_excess    = df_monthly['excess_xle'].mean()

print("\nPart (a): Avg monthly excess return on the market (1999–2019): {:.10f}".format(avg_market_excess))
print("Part (b): Avg monthly excess return on the energy ETF (1999–2019): {:.10f}".format(avg_etf_excess))

# Compute each stock's excess return (stock minus risk-free)
df['stock_excess'] = df['r'] - df['r_f']

# -------------------------
# PART (a) [Regression stage]: Time-Series Regressions for Each Firm
# -------------------------
firms = df['firm'].unique()
beta_list = []

for firm in firms:
    df_firm = df[df['firm'] == firm]
    Y = df_firm['stock_excess']
    X = df_firm[['excess_market', 'excess_xle']]
    X = sm.add_constant(X)
    model = sm.OLS(Y, X).fit()
    beta_list.append({
        'firm':    firm,
        'alpha':   round(model.params['const'],         10),
        'beta_mkt':round(model.params['excess_market'], 10),
        'beta_xle':round(model.params['excess_xle'],    10)
    })

betas_df = pd.DataFrame(beta_list)
print("Part (a) - Time-Series Regression Estimates by Firm:")
print(betas_df)

# Optional 3D visualization
fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(betas_df['alpha'], betas_df['beta_mkt'], betas_df['beta_xle'], marker='o', s=50)
ax.set_xlabel('Alpha')
ax.set_ylabel('Beta Market')
ax.set_zlabel('Beta XLE')
ax.set_title('Part (a) - 3D Scatter: Regression Estimates by Firm')
plt.show()

# -------------------------
# PART (b): Cross-Sectional Regression
# -------------------------
# (Same as before, merges betas + average stock excess + sector flags)
avg_stock_excess = df.groupby('firm')['stock_excess'].mean().reset_index()
avg_stock_excess.rename(columns={'stock_excess': 'avg_stock_excess'}, inplace=True)

firm_info = df[['firm','airline','oil']].drop_duplicates()

cs_df = pd.merge(betas_df, avg_stock_excess, on='firm')
cs_df = pd.merge(cs_df, firm_info, on='firm')

X_cs = cs_df[['beta_mkt', 'beta_xle']]
X_cs = sm.add_constant(X_cs)
Y_cs = cs_df['avg_stock_excess']
cs_model = sm.OLS(Y_cs, X_cs).fit()

print("\nPart (b) - Cross-Sectional Regression Results:")
print(cs_model.summary())
print("γ_mkt = {:.5f}".format(cs_model.params['beta_mkt']))
print("γ_xle = {:.5f}".format(cs_model.params['beta_xle']))

fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(cs_df['beta_mkt'], cs_df['beta_xle'], cs_df['avg_stock_excess'], marker='o', s=50)
ax.set_xlabel('Beta Market')
ax.set_ylabel('Beta XLE')
ax.set_zlabel('Avg Stock Excess')
ax.set_title('Part (b) - 3D Scatter: Beta Parameters vs. Actual Avg Stock Excess')
plt.show()

# -------------------------
# PART (c) & (d): Averages of average excess returns by sector
# -------------------------
airline_avg = cs_df[cs_df['airline'] == 1]['avg_stock_excess'].mean()
oil_avg     = cs_df[cs_df['oil']     == 1]['avg_stock_excess'].mean()

print("\nPart (c): Arithmetic average excess returns for airline stocks: {:.10f}".format(airline_avg))
print("Part (d): Arithmetic average excess returns for oil stocks: {:.10f}".format(oil_avg))

fig = plt.figure(figsize=(8,6))
ax = fig.add_subplot(111, projection='3d')
ax.scatter([1],[airline_avg],[0], marker='o', s=100, label='Airline Stocks')
ax.scatter([2],[oil_avg],[0],     marker='o', s=100, label='Oil Stocks')
ax.set_xticks([1,2])
ax.set_xticklabels(['Airline','Oil'])
ax.set_ylabel('Average Stock Excess Return')
ax.set_zlabel('Z (dummy)')
ax.set_title('Part (c)&(d) - 3D Scatter: Avg Excess Returns')
plt.legend()
plt.show()

# -------------------------
# PART (e) – (h): Average factor loadings by sector
# -------------------------
oil_betas     = cs_df[cs_df['oil'] == 1]
airline_betas = cs_df[cs_df['airline'] == 1]

# (e) Oil stocks, market-factor beta
oil_avg_mkt_beta = oil_betas['beta_mkt'].mean()
print("\nPart (e): Avg factor loading of the oil stocks on the market factor: {:.6f}".format(oil_avg_mkt_beta))

# (f) Oil stocks, energy-factor beta
oil_avg_xle_beta = oil_betas['beta_xle'].mean()
print("Part (f): Avg factor loading of the oil stocks on the energy factor: {:.6f}".format(oil_avg_xle_beta))

# (g) Airline stocks, market-factor beta
airline_avg_mkt_beta = airline_betas['beta_mkt'].mean()
print("Part (g): Avg factor loading of the airline stocks on the market factor: {:.6f}".format(airline_avg_mkt_beta))

# (h) Airline stocks, energy-factor beta
airline_avg_xle_beta = airline_betas['beta_xle'].mean()
print("Part (h): Avg factor loading of the airline stocks on the energy factor: {:.6f}".format(airline_avg_xle_beta))

# -------------------------
# PART (i) & (j): Average alpha by sector (in %)
# -------------------------
oil_avg_alpha      = oil_betas['alpha'].mean()      # in decimal
airline_avg_alpha  = airline_betas['alpha'].mean()  # in decimal

print("\nPart (i): Arithmetic avg alpha of the oil stocks (monthly, %): {:.4f}".format(oil_avg_alpha * 100))
print("Part (j): Arithmetic avg alpha of the airline stocks (monthly, %): {:.4f}".format(airline_avg_alpha * 100))

# -------------------------
# PART (k) & (l): Expected excess returns for each sector
# using average betas & forecasted factor returns (0.4% market, 0.7% energy)
# -------------------------
mkt_forecast = 0.004  # 0.4% in decimal form
xle_forecast = 0.007  # 0.7% in decimal form

# (k) Oil sector
oil_exp_return = (oil_avg_mkt_beta * mkt_forecast +
                  oil_avg_xle_beta * xle_forecast) * 100  # convert to %
print("\nPart (k): Expected excess return for the oil sector (monthly, %): {:.4f}".format(oil_exp_return))

# (l) Airline sector
airline_exp_return = (airline_avg_mkt_beta * mkt_forecast +
                      airline_avg_xle_beta * xle_forecast) * 100
print("Part (l): Expected excess return for the airline sector (monthly, %): {:.4f}".format(airline_exp_return))
