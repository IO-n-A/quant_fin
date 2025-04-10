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
# Use 'companyname' as the unique firm identifier.
# If the column exists, rename it to 'firm' for ease of use.
# ------------------------------------------------------------------
if 'companyname' in df.columns:
    df.rename(columns={'companyname': 'firm'}, inplace=True)
else:
    print("Error: 'companyname' column not found in the data. Please ensure your data contains a firm identifier.")
    exit(1)

# Compute the factor excess returns for the market and energy ETF.
df['excess_market'] = (df['r_mkt'] - df['r_f']).round(20)
df['excess_xle'] = (df['r_xle'] - df['r_f']).round(20)

# Compute each stock's excess return (stock return minus risk-free rate).
df['stock_excess'] = df['r'] - df['r_f']

# -------------------------
# PART (a): Time-Series Regressions for Each Firm
# -------------------------
# Run a separate regression of stock_excess on excess_market and excess_xle for each firm.
firms = df['firm'].unique()
beta_list = []  # will store the regression estimates for each firm

for firm in firms:
    df_firm = df[df['firm'] == firm]
    Y = df_firm['stock_excess']
    X = df_firm[['excess_market', 'excess_xle']]
    X = sm.add_constant(X)
    model = sm.OLS(Y, X).fit()
    beta_list.append({
        'firm': firm,
        'alpha': round(model.params['const'], 10),
        'beta_mkt': round(model.params['excess_market'], 10),
        'beta_xle': round(model.params['excess_xle'], 10)
    })

betas_df = pd.DataFrame(beta_list)
print("Part (a) - Time-Series Regression Estimates by Firm:")
print(betas_df)
default_size = mpl.rcParams['font.size']
reduced_size = default_size * 0.75

# -------------------------
# 3D Visualization for Part (a): 3D Scatter Plot for Regression Estimates
# Each firm is represented in a 3D space (alpha, beta_mkt, beta_xle)
# -------------------------
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(betas_df['alpha'], betas_df['beta_mkt'], betas_df['beta_xle'], 
           color='skyblue', marker='o', s=50)
for i, firm in enumerate(betas_df['firm']):
    ax.text(betas_df['alpha'].iloc[i], betas_df['beta_mkt'].iloc[i], betas_df['beta_xle'].iloc[i],
            firm, fontsize=reduced_size)
ax.set_xlabel('Alpha')
ax.set_ylabel('Beta Market')
ax.set_zlabel('Beta XLE')
ax.set_title('Part (a) - 3D Scatter: Regression Estimates by Firm')
plt.show()

# -------------------------
# PART (b): Cross-Sectional Regression
# -------------------------
# Compute the time-series average excess return for each firm.
avg_stock_excess = df.groupby('firm')['stock_excess'].mean().reset_index()
avg_stock_excess.rename(columns={'stock_excess': 'avg_stock_excess'}, inplace=True)

# Merge the regression estimates with the firm-specific average excess returns.
cs_df = pd.merge(betas_df, avg_stock_excess, on='firm')

# Also merge the firm-level classification (airline and oil indicators).
firm_info = df[['firm', 'airline', 'oil']].drop_duplicates()
cs_df = pd.merge(cs_df, firm_info, on='firm')

# Run the cross-sectional regression:
# avg_stock_excess = γ0 + γ_mkt * beta_mkt + γ_xle * beta_xle + error
X_cs = cs_df[['beta_mkt', 'beta_xle']]
X_cs = sm.add_constant(X_cs)
Y_cs = cs_df['avg_stock_excess']
cs_model = sm.OLS(Y_cs, X_cs).fit()

print("\nPart (b) - Cross-Sectional Regression Results:")
print(cs_model.summary())

gamma_mkt = round(cs_model.params['beta_mkt'], 10)
gamma_xle = round(cs_model.params['beta_xle'], 10)
print("\nEstimated risk premium on market factor (γ_mkt): {:.10f}".format(gamma_mkt))
print("Estimated risk premium on energy ETF factor (γ_xle): {:.10f}".format(gamma_xle))

# For 3D visualization in Part (b), plot beta_mkt, beta_xle, and avg_stock_excess.
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(cs_df['beta_mkt'], cs_df['beta_xle'], cs_df['avg_stock_excess'], 
           color='purple', marker='o', s=50)
ax.set_xlabel('Beta Market')
ax.set_ylabel('Beta XLE')
ax.set_zlabel('Avg Stock Excess')
ax.set_title('Part (b) - 3D Scatter: Beta Parameters vs. Actual Avg Stock Excess')
plt.show()

# -------------------------
# PART (c): Average Excess Return for Airline Stocks
# -------------------------
# For firms identified as airlines (airline == 1), compute the arithmetic average of their average excess returns.
airline_avg = cs_df[cs_df['airline'] == 1]['avg_stock_excess'].mean()
airline_avg = round(airline_avg, 10)
print("\nPart (c) - Arithmetic average of individual stock average excess returns for airline stocks: {:.10f}".format(airline_avg))

# -------------------------
# PART (d): Average Excess Return for Oil Stocks
# -------------------------
# For firms identified as oil (oil == 1), compute the arithmetic average of their average excess returns.
oil_avg = cs_df[cs_df['oil'] == 1]['avg_stock_excess'].mean()
oil_avg = round(oil_avg, 10)
print("Part (d) - Arithmetic average of individual stock average excess returns for oil stocks: {:.10f}".format(oil_avg))

# -------------------------
# 3D Visualization for Parts (c) and (d):
# Use a 3D scatter plot (with a dummy z-axis) to represent the average excess returns.
# -------------------------
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
# For visualization, assign x positions 1 for Airline and 2 for Oil, y as the average return, and z as zero.
ax.scatter([1], [airline_avg], [0], color='blue', marker='o', s=100, label='Airline Stocks')
ax.scatter([2], [oil_avg], [0], color='green', marker='o', s=100, label='Oil Stocks')
ax.set_xticks([1, 2])
ax.set_xticklabels(['Airline', 'Oil'])
ax.set_ylabel('Average Stock Excess Return')
ax.set_zlabel('Z (dummy)')
ax.set_title('Part (c) & (d) - 3D Scatter: Average Excess Returns')
plt.legend()
plt.show()
