#!/usr/bin/env python3
"""Make data/city_median_sale_price.json from data/college_town_home_sales.csv.

Rule: sales under $10,000 are left out, and so are rows with no sale price.
For each city, the script writes the number of sales kept and their median
sale price (the average of the two middle values when the count is even).

Run from the repository root:
    python3 scripts/city_median_sale_price.py

The dataset files are read only. The output is a new file.
"""

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "college_town_home_sales.csv"
OUTPUT = ROOT / "data" / "city_median_sale_price.json"
MIN_PRICE = 10_000


def main() -> None:
    kept = defaultdict(list)
    excluded_low = 0
    missing_price = 0
    total_rows = 0

    # Text columns (zipcode, county_fips, parcel_number) are not used here, and
    # csv reads every field as text, so nothing is converted by accident.
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            total_rows += 1
            raw = row["sale_price"].strip()
            if raw == "":
                missing_price += 1
                continue
            price = int(float(raw))
            if price < MIN_PRICE:
                excluded_low += 1
                continue
            kept[(row["city"], row["state"])].append(price)

    cities = []
    for (city, state), prices in kept.items():
        cities.append({
            "city": city,
            "state": state,
            "sales": len(prices),
            "median_sale_price": statistics.median(prices),
        })
    cities.sort(key=lambda c: (-c["median_sale_price"], c["city"]))

    output = {
        "rule": f"Sales under ${MIN_PRICE:,} are left out, and so are rows with no sale price.",
        "source": "data/college_town_home_sales.csv",
        "total_rows": total_rows,
        "rows_excluded_under_minimum": excluded_low,
        "rows_missing_price": missing_price,
        "rows_kept": sum(c["sales"] for c in cities),
        "cities": cities,
    }

    with OUTPUT.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)
        handle.write("\n")

    print(f"Wrote {OUTPUT.relative_to(ROOT)}: {len(cities)} cities, "
          f"{output['rows_kept']:,} of {total_rows:,} rows kept, "
          f"{excluded_low} under ${MIN_PRICE:,}, {missing_price} with no price.")


if __name__ == "__main__":
    main()
