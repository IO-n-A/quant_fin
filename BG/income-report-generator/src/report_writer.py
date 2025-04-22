from datetime import datetime
from pathlib import Path
from typing import DataFrame

def write_rtf_report(regular_summary: DataFrame, irregular_payments: DataFrame, avg_monthly_income: float, output_path: str):
    rtf_content = r"{\rtf1\ansi\ansicpg1252\deff0\nouicompat{\fonttbl{\f0\fnil\fcharset0 Calibri;}}"
    rtf_content += r"{\*\generator Riched20 10.0.18362;}viewkind4\uc1 \pard\sa200\sl276\slmult1\f0\fs22\lang9 "
    rtf_content += r"Income Report\par"
    rtf_content += r"\pard\sa200\sl276\slmult1\b Average Monthly Income: \b0 €{:.2f}\par".format(avg_monthly_income)
    
    rtf_content += r"\par\b Regular Incoming Payments Summary:\b0\par"
    rtf_content += r"\pard\sa200\sl276\slmult1"
    
    for cluster, group in regular_summary.groupby(level=0):
        rtf_content += r"\par\b Cluster {}: \b0\par".format(cluster)
        for index, row in group.iterrows():
            rtf_content += r"Description: {}, Count: {}, Average Amount: €{:.2f}, Average Day: {:.2f}\par".format(
                row['Description'], row['count'], row['avg_amount'], row['avg_day']
            )
    
    rtf_content += r"\par\b Irregular Incoming Payments:\b0\par"
    for index, row in irregular_payments.iterrows():
        rtf_content += r"Date: {}, Description: {}, Amount: €{:.2f}\par".format(
            row['Date'].strftime('%Y-%m-%d'), row['Description'], row['Amount']
        )
    
    rtf_content += r"}"
    
    # Write the RTF content to the specified output file
    output_file = Path(output_path)
    with output_file.open('w', encoding='utf-8') as file:
        file.write(rtf_content)