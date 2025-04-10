import pandas as pd

# 1. Read the data
df = pd.read_excel("original_data.xlsx")

# 2. Compute monthly excess returns
df["excess_mkt"] = df["rmkt"] - df["rf"]
df["excess_xle"] = df["rxle"] - df["rf"]

# 3. Calculate the average (mean) of these excess returns
avg_excess_mkt = df["excess_mkt"].mean()
avg_excess_xle = df["excess_xle"].mean()

# 4. Convert to % (monthly)
avg_excess_mkt_percent = avg_excess_mkt * 100
avg_excess_xle_percent = avg_excess_xle * 100

# 5. Print results
print(f"Average monthly excess return on the market portfolio: {avg_excess_mkt_percent:.4f}%")
print(f"Average monthly excess return on the XLE ETF: {avg_excess_xle_percent:.4f}%")
