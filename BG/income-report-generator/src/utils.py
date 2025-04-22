def format_currency(amount):
    return f"€{amount:.2f}"

def format_date(date):
    return date.strftime("%d %B %Y")

def format_summary_table(summary_df):
    table = ""
    for index, row in summary_df.iterrows():
        table += f"{row['Description']}: Count = {row['count']}, Average Amount = {format_currency(row['avg_amount'])}, Average Day = {row['avg_day']:.1f}\n"
    return table.strip()