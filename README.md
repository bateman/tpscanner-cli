# TPScanner

TPScanner is a Python script that extracts prices of items from [Trovaprezzi.it](https://www.trovaprezzi.it/), sorts them, and saves the results in a spreadsheet. It also finds the best cumulative deals and saves them in the same spreadsheet.

## Setup

Before you can run TPScanner, you need to set up your environment. This project uses [Poetry](https://python-poetry.org/) for dependency management. If you haven't installed Poetry yet, you can do so by following the instructions on their [official website](https://python-poetry.org/docs/#installation).

Once you have Poetry installed, follow these steps to set up the project:

1. Clone the repository:

```bash
git clone https://github.com/yourusername/tpscanner.git
cd tpscanner
```

2. Install the project dependencies:
```bash
poetry install
```

3. Activate the virtual environment:
```bash
poetry shell
```

## Usage

To run the script, use the following command:

```bash
python tpscanner.py -u url1 url2 ...
```

## Output

The script outputs a spreadsheet named `results_<current_datetime>.xlsx` with the sorted list of items and the best cumulative deals.

## Functions

The script contains the following main functions:

* `extract_prices(html)`: This function extracts the prices from the given HTML.
* `save_intermediate_results(filename, name, items)`: This function saves the intermediate results to a spreadsheet.
* `find_best_deals(all_items)`: This function finds the best cumulative deals from the list of all items.
* `save_best_cumulative_deals(filename, name, best_cumulative_deals)`: This function saves the best cumulative deals to a spreadsheet.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
