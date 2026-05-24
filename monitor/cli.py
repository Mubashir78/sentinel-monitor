import argparse
import asyncio
import sys
from blessed import Terminal
from checker import run_all_checks
from config import load_config

term = Terminal()


def print_table(results):
    tw = term.width or 120

    # fixed columns
    fixed = {
        "status": 8,
        "code": 10,
        "rtime": 14,
        "ssl": 24,
    }
    seps = 3 * 5 # 5 separators at 3 chars each
    name_w = 20
    fixed_total = sum(fixed.values()) + seps + name_w

    # url gets whatever is left, minimum 10
    url_w = max(tw - fixed_total -3, 10) # -3 for its own separator

    col = {
        "status": fixed["status"],
        "name": name_w,
        "url": url_w,
        "code": fixed["code"],
        "rtime": fixed["rtime"],
        "ssl": fixed["ssl"],
            }
    def cell(s, w):
        visible = term.length(s)
        return s + " " * max(w - visible, 0)

    def trunc(s, w):
        return s[:w-1] + "..." if len(s) > w else s

    sep = term.dim(" | ")
    total_w = sum(col.values()) + 3 + (len(col) - 1)
    divider = term.dim("-" * total_w)

    header = (
        cell(term.bold_magenta("Status"), col["status"]) + sep +
        cell(term.bold_magenta("Site Name"), col["name"]) + sep +
        cell(term.bold_magenta("URL"), col["url"]) + sep +
        cell(term.bold_magenta("HTTP"), col["code"]) + sep +
        cell(term.bold_magenta("Resp(ms)"), col["rtime"]) + sep +
        cell(term.bold_magenta("SSL Expires"), col["ssl"])
    )

    print()
    print(term.bold("Sentinel Uptime & SSL Monitor"))
    print(divider)
    print(header)
    print(divider)

    for res in results:
        if res.is_up:
            status_str = term.bold_green("UP")
            code_str = term.green(str(res.status_code))
        else:
            status_str = term.bold_red("DOWN")
            code_str = term.red(str(res.status_code) if res.status_code else "-")

        ssl_raw = res.ssl_days_left

        if isinstance(ssl_raw, int):
            if ssl_raw < 7:
                ssl_str = term.bold_red(f"{ssl_raw} days (CRITICAL)")
            elif ssl_raw < 30:
                ssl_str = term.yellow(f"{ssl_raw} days (WARN)")
            else:
                ssl_str = term.green(f"{ssl_raw} days")
        else:
            ssl_str = str(ssl_raw)

        row = (
            cell(status_str, col["status"]) + sep +
            cell(term.cyan(res.name), col["name"]) + sep +
            cell(term.dim(res.url), col["url"]) + sep +
            cell(code_str, col["code"]) + sep +
            cell(f"{res.response_time_ms}ms", col["rtime"]) + sep +
            cell(ssl_str, col["ssl"])
        )

        print(row)

        if res.error_msg:
            print(term.red(f"Error: {res.error_msg}"))

    print(divider)
    print()


def main():
    """Main CLI entry point."""

    parser = argparse.ArgumentParser(
        description="Sentinel: A fast concurrent uptime and SSL monitor."
    )

    parser.add_argument(
        "-c",
        "--config",
        default="../targets.yaml",
        help="Path to the configuration file",
    )

    args = parser.parse_args()

    try:
        # Load the configurations
        app_config = load_config(args.config)

        print(f"[*] Loaded {len(app_config.sites)} sites from {args.config}...")

        # Run the asynchronous checks
        print(term.bold_green("Probing network targets concurrently..."))

        results = asyncio.run(
            run_all_checks(app_config.sites, app_config.timeout)
        )

        # Draw the table
        print_table(results)

    except FileNotFoundError as e:
        print(term.bold_red(f"Error: {e}"))
        sys.exit(1)

    except Exception as e:
        print(term.bold_red(f"Fatal Error: {e}"))
        sys.exit(1)


if __name__ == "__main__":
    main()
