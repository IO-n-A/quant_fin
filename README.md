__pycache__/
# Quantitative Finance Analysis

This project performs a quantitative analysis on stock returns using data sourced from CSV and Excel files. The analysis includes computing monthly excess returns for the market portfolio and the XLE ETF.

## Project Overview

- **Data Sources:**
  - `data.csv` – Preprocessed data in CSV format.
  - `original_data.xlsx` – The original Excel file containing the raw data.

- **Main Scripts:**
  - `data_analysis_csv.py` – Performs the primary quantitative analysis using the CSV data.

## Requirements

- Python 3.x
- [pandas](https://pandas.pydata.org/)

Install the required package with:
```sh
pip install pandas
```

## Getting Started

1. **Clone the Repository** (if starting fresh):
   ```sh
   git clone https://github.com/IO-n-A/quant_fin
   cd quant_fin
   ```

2. **Run the Analysis**:
   - To analyze CSV data:
     ```sh
     python data_analysis_csv.py
     ```
   - If needed, you can also run:
     ```sh
     python airline_oil_csv.py
     ```



## License

This project is licensed under the MIT License 