"""Télécharge la base de géolocalisation DB-IP « IP to City Lite » (gratuite, CC BY 4.0, sans clé).

Usage, depuis barry_back/ :
    uv run python -m db.download_geoip
    uv run python -m db.download_geoip --strict   # code de sortie 1 en cas d'échec
"""

import argparse
import gzip
import os
import shutil
import tempfile
import urllib.request
from datetime import date

from services import geo

URL = "https://download.db-ip.com/free/dbip-city-lite-{year:04d}-{month:02d}.mmdb.gz"


def _candidate_months(today: date) -> list[tuple[int, int]]:
    """Mois courant puis précédent (la base du mois n'est publiée qu'en début de mois)."""
    y, m = today.year, today.month
    previous = (y - 1, 12) if m == 1 else (y, m - 1)
    return [(y, m), previous]


def _download_file(url: str, target_path) -> None:
    directory = target_path.parent
    directory.mkdir(parents=True, exist_ok=True)

    req = urllib.request.Request(url, headers={"User-Agent": "barry-back-geoip-downloader/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        with tempfile.NamedTemporaryFile(dir=directory, suffix=".mmdb.part", delete=False) as tmp:
            tmp_path = tmp.name
            try:
                with gzip.GzipFile(fileobj=response) as gz:
                    shutil.copyfileobj(gz, tmp, length=1024 * 1024)
                tmp.close()
                # Contrôle : la base doit s'ouvrir avant de remplacer l'ancienne.
                import maxminddb

                maxminddb.open_database(tmp_path).close()
                os.replace(tmp_path, target_path)
            except BaseException:
                tmp.close()
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Télécharge la base DB-IP City Lite (.mmdb)")
    parser.add_argument("--strict", action="store_true", help="Code de sortie 1 en cas d'échec.")
    args = parser.parse_args()

    target = geo.db_path()
    errors: list[str] = []
    for year, month in _candidate_months(date.today()):
        url = URL.format(year=year, month=month)
        try:
            _download_file(url, target)
        except Exception as exc:
            errors.append(f"{url} : {exc}")
            continue
        geo.reset()
        print(f"Base géo installée ({year:04d}-{month:02d}) : {target}")
        return

    message = "Téléchargement de la base géo impossible :\n  " + "\n  ".join(errors)
    if args.strict:
        raise SystemExit(message)
    print(f"AVERTISSEMENT : {message}\nL'application fonctionnera sans pays/région.")


if __name__ == "__main__":
    main()
