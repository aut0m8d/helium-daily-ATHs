#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from typing import Dict, List, Tuple
from urllib.request import urlopen

DEFAULT_DATA_URL = (
    "https://helium-mobile-prod-metrics.s3.us-west-2.amazonaws.com/"
    "v0/latest/daily_total_data_tb_all_carriers_6mo_hist.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Print every historical day whose value sets a new record "
            "for its weekday at the moment it occurs."
        )
    )
    parser.add_argument(
        "--json-url",
        default=DEFAULT_DATA_URL,
        help=(
            "URL to the growth data JSON (default: Helium Mobile public metrics feed)"
        ),
    )
    return parser.parse_args()


def load_series(url: str) -> List[Dict[str, float]]:
    with urlopen(url) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload["historical_daily"]


def emit_records(series: List[Dict[str, float]]) -> List[Tuple[str, str, float, float]]:
    by_weekday: Dict[int, float] = {}
    new_records: List[Tuple[str, str, float, float]] = []

    for entry in sorted(series, key=lambda e: e["time"]):
        timestamp = datetime.fromisoformat(entry["time"])
        weekday_idx = timestamp.weekday()
        weekday = timestamp.strftime("%A")
        value = float(entry["value"])
        stored = by_weekday.get(weekday_idx)

        if stored is None or value > stored:
            delta = value - stored if stored is not None else float("nan")
            by_weekday[weekday_idx] = value
            new_records.append(
                (timestamp.date().isoformat(), weekday, value, delta)
            )

    return new_records


def format_table(records: List[Tuple[str, str, float, float]]) -> str:
    date_col = [r[0] for r in records]
    weekday_col = [r[1] for r in records]
    value_col = [f"{r[2]:.3f} TB" for r in records]
    delta_plain_col = []

    for _, _, _, delta in records:
        if delta == delta:
            sign = "+" if delta >= 0 else "-"
            delta_plain_col.append(f"({sign}{abs(delta):.3f} TB)")
        else:
            delta_plain_col.append("N/A")

    date_w = max(len("Date"), *(len(item) for item in date_col))
    weekday_w = max(len("Weekday"), *(len(item) for item in weekday_col))
    value_w = max(len("Value (TB)"), *(len(item) for item in value_col))
    delta_w = max(len("Delta vs prior (TB)"), *(len(item) for item in delta_plain_col))

    header = (
        f"{'Date':<{date_w}}  "
        f"{'Weekday':<{weekday_w}}  "
        f"{'Value (TB)':>{value_w}}  "
        f"{'Delta vs prior (TB)':>{delta_w}}"
    )
    header_width = len(header)
    lines = [header, "-" * header_width]
    prev_month = None

    for date, weekday, value_str, delta_plain in zip(
        date_col, weekday_col, value_col, delta_plain_col
    ):
        current_month = date[:7]
        if prev_month and current_month != prev_month:
            month_label = datetime.fromisoformat(date).strftime("%B %Y")
            divider = f"-- {month_label} --".center(header_width, "-")
            lines.append(divider)
        prev_month = current_month

        padded_value = f"{value_str:>{value_w}}"
        padded_delta = f"{delta_plain:>{delta_w}}"
        lines.append(
            f"{date:<{date_w}}  "
            f"{weekday:<{weekday_w}}  "
            f"{padded_value}  "
            f"{padded_delta}"
        )

    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    series = load_series(args.json_url)
    records = emit_records(series)

    if not records:
        print("No weekday records found.")
        return

    print(format_table(records))


if __name__ == "__main__":
    main()
