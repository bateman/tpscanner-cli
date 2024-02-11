# TPScanner

TPScanner is a Python script that extracts prices of items from [Trovaprezzi.it](https://www.trovaprezzi.it/), sorts them, displays and saves the results in a spreadsheet. It also finds the best cumulative and individual deals.

![Intro Image](img/intro.gif)

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

### External dependencies

The script relies on [Selenium](https://www.selenium.dev/) web driver. Make sure that and [chromedriver](https://chromedriver.chromium.org/) and the Chrome/Chromium web browser are both installed before running the script. 

### Note

If you don't have `poetry` installed (or don't want to install), you can use `pip` as follows:

1. First, create a virual environment: `python -m venv .tps`.
2. Activate it: `source .tps/bin/activate`.
3. Install requirements: `pip install -r requirements.txt`.
4. Optional, for development purposes only, run also: `pip install -r requirements-dev.txt`.


## Usage

To run the script, use the following command:

```bash
python -m tpscanner -u url1 url2 ... | -f path/to/input/file.txt [-q n1 n2 ...] [-w n] [--headless] [--console=true|false] [--excel=true|false]
```
```
options:
  -h, --help              Show this help message and exit
  -u URL [URL ...], --url URL [URL ...]
                          List of URLs to scan
  -f FILE, --file FILE    File containing URLs to scan
  -q QUANTITY [QUANTITY ...], --quantity  QUANTITY [QUANTITY ...]
                          List of quantities to buy for each URL (in order)
  -w WAIT, --wait WAIT    Wait time between URLs requests
  --headless              Run in headless mode
  -c=BOOL, --console=BOOL Whether to print results to the console (default true)
  -x=BOOL, --excel=BOOL   Whether to save results to Excel (default true)
```

Alternatively, you can run the script as:

```bash
python -m tpscanner ...
```

Alternatively:
```bash
poetry run tpscanner ...
```

or 

```bash
make run ARGS="..."
```

### Note

By default, running the script with browser in `headless` mode is disabled. In my tests, I've noticed that it causes the server to display captchas, thus making the script scraping process to fail.


## Output

When the `--console` option is enabled, the script outputs to the console
the results in form of tables.

When the `--excel` option is enabled, the script creates a spreadsheet named `results_<current_datetime>.xlsx` with the sorted list of items and the best cumulative deals.

## Configuration

You can configure the script by editing the file `config/config.ini`. At the moment, you can configure:

- `sleep_rate_limit = 5`: Too aggressive scraping will cause the server to show captchas. By default, the script will wait 5 secs. in between each item's offer scraping.
- `output_dir = results`: The output directory where to store the Excel output file. By default, it is set to the `results/` subfolder in the current working directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
