import argparse
import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

SOURCES = {
    "acb": {
        "league": "ACB",
        "country": "Spain",
        "url": "https://acb.com/es/liga/estadisticas/estadisticas-de-jugador/detalle",
    },
    "nbl": {
        "league": "NBL",
        "country": "Australia",
        "url": "https://www.nbl.com.au/stats/statistics",
    },
    "nba": {
        "league": "NBA",
        "country": "USA",
        "url": "https://www.nba.com/stats/players/traditional",
    },
}

COLUMNS = [
    "source", "player_id", "player_name",
    "team", "league", "country", "season",
    "gp", "mpg", "ppg", "rpg", "apg",
    "spg", "bpg", "tpg", "fg_pct",
    "fg3_pct", "ft_pct", "source_url",
    "retrieved_utc"
]


def inspect_source(source, output):
    url = SOURCES[source]["url"]
    response = requests.get(
        url,
        timeout=90,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()

    try:
        tables = pd.read_html(io.StringIO(response.text))
    except ValueError:
        tables = []

    report = {
        "source": source,
        "url": url,
        "tables_found": len(tables),
        "tables": [
            {
                "rows": len(table),
                "columns": [str(c) for c in table.columns]
            }
            for table in tables
        ],
        "note": "Inspection only; player export not yet validated."
    }

    Path(output).parent.mkdir(
        parents=True, exist_ok=True
    )
    Path(output).write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )
    print(f"Inspected {source}: {len(tables)} tables")


def export_nba(season, output):
    from nba_api.stats.endpoints import leaguedashplayerstats

    endpoint = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        per_mode_detailed="PerGame",
        season_type_all_star="Regular Season",
        timeout=30
    )

    df = endpoint.get_data_frames()[0]

    if df.empty:
        raise ValueError("NBA returned no players")

    mapping = {
        "PLAYER_ID": "player_id",
        "PLAYER_NAME": "player_name",
        "TEAM_ABBREVIATION": "team",
        "GP": "gp",
        "MIN": "mpg",
        "PTS": "ppg",
        "REB": "rpg",
        "AST": "apg",
        "STL": "spg",
        "BLK": "bpg",
        "TOV": "tpg",
        "FG_PCT": "fg_pct",
        "FG3_PCT": "fg3_pct",
        "FT_PCT": "ft_pct"
    }

    df = df.rename(columns=mapping)

    if "player_id" not in df or "ppg" not in df:
        raise ValueError("NBA mandatory fields missing")

    df["source"] = "nba_stats"
    df["league"] = "NBA"
    df["country"] = "USA"
    df["season"] = season
    df["source_url"] = SOURCES["nba"]["url"]
    df["retrieved_utc"] = datetime.now(
        timezone.utc
    ).isoformat()

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = None

    Path(output).parent.mkdir(
        parents=True, exist_ok=True
    )
    df[COLUMNS].to_csv(output, index=False)

    print(f"Exported {len(df)} NBA player rows")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source", required=True,
        choices=["acb", "nbl", "nba"]
    )
    parser.add_argument(
        "--mode", required=True,
        choices=["inspect", "export"]
    )
    parser.add_argument(
        "--season", default="2025-26"
    )
    parser.add_argument("--output")

    args = parser.parse_args()

    if args.mode == "export":
        if args.source != "nba":
            parser.error(
                "ACB/NBL export not yet enabled"
            )
        output = args.output or "out/nba.csv"
        export_nba(args.season, output)
    else:
        if args.source == "nba":
            parser.error("Use export for NBA")
        output = args.output or (
            f"out/{args.source}_inspection.json"
        )
        inspect_source(args.source, output)


if __name__ == "__main__":
    main()
