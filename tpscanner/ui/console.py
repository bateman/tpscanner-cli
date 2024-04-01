"""This module contains the Console class for displaying formatted output using the Rich library."""

from typing import ClassVar, Dict, Iterable, List, Optional

from rich.console import Console as RichConsole
from rich.rule import Rule
from rich.table import Table
from rich.theme import Theme


class Console:
    """Console class for displaying formatted output using the Rich library.

    Attributes:
        console (RichConsole): The RichConsole object used for printing formatted output.
        columns_individual (list): List of tuples representing the columns for individual deals table.
        columns_cumulative (list): List of tuples representing the columns for cumulative deals table.

    Methods:
        __init__(): Initializes the Console object with a RichConsole instance and sets the column configurations.
        print(message, level="info"): Prints a message with the specified level of styling.
        _create_table(title, columns): Creates a Rich Table object with the specified title and column configurations.
        display_best_individual_deals(best_individual_deals, title): Displays the best individual deals in a formatted table.
        display_best_cumulative_deals(best_cumulative_deals, title): Displays the best cumulative deals in a formatted table.

    """

    console: ClassVar = None
    columns_individual: List[Dict] = []
    columns_cumulative: List[Dict] = []

    def __init__(self):
        """Initialize the Console object with a RichConsole instance and sets the column configurations."""
        theme = Theme(
            {
                "banner": "bold green",
                "start": "bold magenta",
                "end": "bold magenta",
                "debug": "bold cyan",
                "info": "bold blue",
                "warning": "bold yellow",
                "error": "bold red",
                "critical": "bold red",
                "success": "bold green",
            }
        )
        self.console = RichConsole(theme=theme)
        self.columns_individual = [
            ("Product", "cyan", "left", 16),
            ("Q.ty", "cyan", "center", 5),
            ("Price", "magenta", "center", 10),
            ("Seller", "blue", "left", 16),
            ("Seller Rating", "blue", "center", 8),
            ("Seller Reviews", "blue", "center", 8),
            ("Delivery Price", "blue", "center", 10),
            ("Free Delivery from", "blue", "center", 10),
            ("Total Price", "magenta", "center", 10),
            ("Total Price + Delivery", "magenta", "center", 10),
            ("Avail.", "white", "center", 7),
        ]

        self.columns_cumulative = [
            ("Seller", "blue", "left", 16),
            ("Seller Reviews", "blue", "center", 8),
            ("Seller Rating", "blue", "center", 8),
            ("Cumulative Price", "magenta", "center", 10),
            ("Delivery Price", "blue", "center", 10),
            ("Free Delivery from", "blue", "center", 10),
            ("Cumulative Price + Delivery", "magenta", "center", 10),
            ("Avail.", "white", "center", 7),
        ]

    def print(self, message: str, level: str = "info") -> None:
        """Print a message with the specified level of styling.

        Arguments:
            message (str): The message to be printed.
            level (str): The level of styling to be applied to the message.

        """
        if level == "banner":
            self._rich_print(message, style="bold white")
        elif level == "start" or level == "end":
            print("\n")
            self._rich_print(Rule(message), style="bold magenta")
            print("\n")
        else:
            self._rich_print(message, style=level)

    def _create_table(self, title: str, columns: Iterable[Dict]) -> Table:
        table = Table(
            title=title,
            header_style="white on dark_blue",
            show_footer=False,
            show_header=True,
            show_lines=False,
        )
        for column, style, justify, width in columns:
            table.add_column(column, style=style, justify=justify, width=width)
        return table

    def display_best_individual_deals(
        self, best_individual_deals: Iterable[Dict], title: str
    ) -> None:
        """Display the best individual deals.

        This function takes a list of deals, sorts them in descending order of value,
        and prints the top deals to the console.

        Arguments:
            best_individual_deals (Iterable[Dict]): A list of deal objects. Each Deal object should have a 'value' attribute.
            title (str): The title of the table.

        """
        best_individual_deals_table = self._create_table(title, self.columns_individual)
        for item in best_individual_deals:
            best_individual_deals_table.add_row(
                item["name"],
                str(item["quantity"]),
                format(item["price"], ".2f") + " €",
                item["seller"],
                str(item["seller_rating"]) + ":star:" if item["seller_rating"] else "-",
                str(item["seller_reviews"]),
                format(item["delivery_price"], ".2f") + " €",
                format(item["free_delivery"], ".2f") + " €"
                if item["free_delivery"]
                else "-",
                format(item["total_price"], ".2f") + " €",
                format(item["total_price_plus_delivery"], ".2f") + " €",
                ":white_check_mark:" if item["availability"] else ":x:",
            )
        print("\n")
        self._rich_print(best_individual_deals_table)

    def display_best_cumulative_deals(
        self, best_cumulative_deals: Iterable[Dict], title: str
    ) -> None:
        """Display the best cumulative deals.

        This function takes a list of cumulative deals, sorts them in descending order of value,
        and prints the top deals to the console.

        Arguments:
            best_cumulative_deals (Iterable[Dict]): A list of cumulative deal objects. Each cumulative deal object should have a 'value' attribute.
            title (str): The title of the table.

        """
        best_cumulative_deals_table = self._create_table(title, self.columns_cumulative)
        for item in best_cumulative_deals:
            best_cumulative_deals_table.add_row(
                item["seller"],
                str(item["seller_reviews"]),
                str(item["seller_rating"]) + ":star:" if item["seller_rating"] else "-",
                format(item["cumulative_price"], ".2f") + " €",
                format(item["delivery_price"], ".2f") + " €",
                format(item["free_delivery"], ".2f") + " €"
                if item["free_delivery"]
                else "-",
                format(item["cumulative_price_plus_delivery"], ".2f") + " €",
                ":white_check_mark:" if item["availability"] else ":x:",
            )
        print("\n")
        self._rich_print(best_cumulative_deals_table)

    def _rich_print(self, message: str, style: Optional[str] = None) -> None:
        """Print a message with the specified style using the Rich library.

        Arguments:
            message (str): The message to be printed.
            style (str): The style to be applied to the message.

        """
        self.console.print(message, style=style)
