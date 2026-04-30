import argparse
import asyncio
import sys
from rich.console import Console
from rich.table import Table
from rich.live import Live

from config import load_config
from checker import run_all_checks

console = Console()

def create_results_table(results) -> Table:
    """Generate a rich terminal table from the check results."""
    table = Table(title="Sentinel Uptime & SSL Monitor", show_header=True, header_style="bold magenta")

    table.add_column("Status", justify="center")
    table.add_column("Site Name", style="cyan")
    table.add_column("URL", style="dim")
    table.add_column("HTTP Code", justify="center")
    table.add_column("Response Time", justify="right")
    table.add_column("SSL Expires", justify="right")

    for res in results:
        # Determine Status formatting
        if res.is_up:
            status_str = "[bold green] UP[/bold green]"
            code_str = f"[green]{res.status_code}[/green]"
        else:
            status_str = "[bold red] DOWN[/bold red]"
            code_str = f"[red]{res.status_code}[/red]"

        # Determine SSL formatting
        ssl_str = str(res.ssl_days_left)
        if isinstance(res.ssl_days_left, int):
            if res.ssl_days_left < 7:
                ssl_str = f"[bold red]{res.ssl_days_left} days (CRITICAL)[/bold red]"
            elif res.ssl_days_left < 30:
                ssl_str = f"[yellow]{res.ssl_days_left} days (WARN)[/yellow]"
            else:
                ssl_str = f"[green]{res.ssl_days_left} days[/green]"
        table.add_row(
            status_str,
            res.name,
            res.url,
            code_str,
            f"{res.response_time_ms}ms",
            ssl_str
        )

        # If there's an error, print it on the next line
        if res.error_msg:
            table.add_row(
                "", "", f"[red]Error: {res.error_msg}[/red]", "", "", "")

    return table


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Sentinel: A fast concurrent uptime and SSL monitor.")
    parser.add_argument("-c", "--config", default="targets.yaml", help="Path to the configuration file")
    args = parser.parse_args()

    try:
        # Load the configurations
        app_config = load_config(args.config)
        console.print(f"[*] Loaded {len(app_config.sites)} sites from {args.config}...", style="bold blue")

        # Run the asynchronous checks
        with console.status(f"[bold green]Probing network targets concurrently...") as status:
            results = asyncio.run(run_all_checks(app_config.sites, app_config.timeout)

        # Draw the table
        table = create_results_table(results)
        console.print(table)

    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Fatal Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
            
