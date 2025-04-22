# Income Report Generator

This project is designed to process financial transaction data and generate a comprehensive income report in RTF format. It utilizes various Python libraries to load, process, and format the data for easy analysis and presentation.

## Project Structure

```
income-report-generator
├── src
│   ├── main.py            # Entry point of the application
│   ├── report_writer.py    # Functions for generating and writing the report in .rtf format
│   ├── data_processing.py   # Handles data processing logic
│   └── utils.py            # Utility functions for formatting and other tasks
├── requirements.txt        # Lists project dependencies
└── README.md               # Documentation for the project
```

## Installation

To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd income-report-generator
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application and generate the income report, execute the following command:

```
python src/main.py
```

This will load the transaction data, process it, and generate an income report in RTF format.

## Dependencies

The project requires the following Python libraries:

- pandas
- numpy
- dateutil
- sklearn
- any additional libraries needed for RTF file generation

Make sure to install all dependencies listed in `requirements.txt`.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.