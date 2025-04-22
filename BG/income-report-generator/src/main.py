import pandas as pd
from data_processing import load_data, calculate_average_monthly_income, identify_payments
from report_writer import generate_report

def main():
    # Load data
    dkb_df = load_data('DKB.csv')
    fyrst_df = load_data('FYRST.csv')
    paypal_df = load_data('PayPal.csv')

    # Process data
    avg_monthly_income, regular_summary, irregular_payments = identify_payments(fyrst_df, paypal_df)

    # Generate report
    generate_report(avg_monthly_income, regular_summary, irregular_payments)

if __name__ == "__main__":
    main()