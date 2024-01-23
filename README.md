# TPScanner

TPScanner is a Python script that extracts prices of items from [Trovaprezzi.it](https://www.trovaprezzi.it/), sorts them, and saves the results in a spreadsheet. It also finds the best cumulative and individual deals.

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
python tpscanner.py -u url1 url2 ... | -f path/to/input/file.txt [-q n1 n2 ...] [-w n] [--headless]

options:
  -h, --help            show this help message and exit
  -u URL [URL ...], --url URL [URL ...]
                        List of URLs to scan
  -f FILE, --file FILE  File containing URLs to scan
  -q QUANTITY [QUANTITY ...], --quantity QUANTITY [QUANTITY ...]
                        List of quantities to buy for each URL (in order)
  -w WAIT, --wait WAIT  Wait time between URLs requests
  --headless            Run in headless mode
```

Alternatively, you can run the script as:

```bash
poetry run tpscanner ...
```

## Output

The script outputs a spreadsheet named `results_<current_datetime>.xlsx` with the sorted list of items and the best cumulative deals.


## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
