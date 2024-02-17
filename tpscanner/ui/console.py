# console.py

from rich.console import Console as RichConsole
from rich.rule import Rule
from rich.table import Table
from rich.theme import Theme


class Console:
    console = None
    columns_individual = []
    columns_cumulative = []

    def __init__(self):
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

    def print(self, message, level="info"):
        if level == "banner":
            self.console.print(message, style="bold green")
        elif level == "start" or level == "end":
            print("\n")
            self.console.print(Rule(message), style="bold magenta")
            print("\n")
        else:
            self.console.print(message, style=level)

    def _create_table(self, title, columns):
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

    def display_best_individual_deals(self, best_individual_deals, title):
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
        self.console.print(best_individual_deals_table)

    def display_best_cumulative_deals(self, best_cumulative_deals, title):
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
        self.console.print(best_cumulative_deals_table)
