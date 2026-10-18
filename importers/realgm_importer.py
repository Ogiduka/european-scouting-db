#!/usr/bin/env python3
"""Small, deliberately bounded RealGM public table CSV exporter."""
import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

LEAGUES = {
    "acb": "https://basketball.realgm.com/international/league/4/Spanish-ACB/stats",
    "nbl": "https://basketball.realgm.com/international/league/5/Australian-NBL/stats",
}
STATS = ("GP", "MPG", "PPG", "FGM", "FGA", "FG%", "3PM", "3PA", "3P%",
         "FTM", "FTA", "FT%", "ORB", "DRB", "RPG", "APG", "SPG", "BPG", "TOV", "PF")
FIELDS = ["source", "league", "season", "player", "player_url", "team", *STATS,
          "source_url", "retrieved_utc"]


def parse_table(html, url, league, season):
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.select("table"):
        header_row = table.select_one("thead tr") or table.select_one("tr")
        if not header_row:
            continue
        heads = [c.get_text(" ", strip=True).replace(" ", "") for c in header_row.find_all(["th", "td"])]
        if not {"Player", "Team", "GP", "PPG"}.issubset(set(heads)):
            continue
        header_map = {name: i for i, name in enumerate(heads)}
        results = []
        body = table.select_one("tbody") or table
        for tr in body.select("tr"):
            cells = tr.find_all(["td", "th"], recursive=False)
            if len(cells) < len(heads):
                continue
            def val(name):
                i = header_map.get(name)
                return cells[i].get_text(" ", strip=True) if i is not None else ""
            player = val("Player")
            if not player or player == "Player":
                continue
            cell = cells[header_map["Player"]]
            link = cell.find("a", href=True)
            row = {
                "source": "RealGM", "league": league.upper(), "season": season,
                "player": player,
                "player_url": urljoin(url, link["href"]) if link else "",
                "team": val("Team"), "source_url": url,
                "retrieved_utc": datetime.now(timezone.utc).isoformat(),
            }
            row.update({stat: val(stat) for stat in STATS})
            results.append(row)
        return results
    raise ValueError("Nije pronaÄena javna tabela sa kolonama Player, Team, GP i PPG")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--league", choices=LEAGUES, required=True)
    p.add_argument("--season", type=int, default=2027, help="RealGM end-year: 2027 = season 2026/27")
    p.add_argument("--output", default="realgm_stats.csv")
    a = p.parse_args()
    url = f"{LEAGUES[a.league]}/{a.season}/Averages/All/All"
    try:
        res = requests.get(url, timeout=20, headers={"User-Agent": "EuropeanScoutingDB/0.1 (one-page public-data test)"})
        if res.status_code in (401, 403, 429):
            raise RuntimeError(f"RealGM ograniÄava pristup (HTTP {res.status_code}); test zaustavljen")
        res.raise_for_status()
        rows = parse_table(res.text, url, a.league, f"{a.season-1}/{str(a.season)[-2:]}")
        if not rows:
            raise ValueError("Stranica nema igraÄe; CSV nije napravljen")
        dest = Path(a.output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"OK: {len(rows)} redova za {a.league.upper()} -> {dest}")
        print("Ovo je samo jedna javna stranica, ne kompletan roster lige.")
    except (requests.RequestException, RuntimeError, ValueError) as exc:
        print(f"IMPORT FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
