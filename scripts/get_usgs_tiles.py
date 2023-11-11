from pathlib import Path
from mpire import WorkerPool

import os

import requests


LINK_BASE = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current"
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "usgs_tiles"))
TILE_DATA = Path(os.environ.get("TILE_DATA", "usgs_tiles.txt"))
NPROCS = int(os.environ.get("NPROCS", 4))

if not OUTPUT_DIR.exists():
    OUTPUT_DIR.mkdir(parents=True)


def build_link(tile: str) -> str:
    link = f"{LINK_BASE}/{tile}/USGS_13_{tile}.tif"
    return link


def download_file(tile: str):
    url = build_link(tile)
    destination = OUTPUT_DIR / f"{tile}" / f"USGS_13_{tile}.tif"
    if destination.is_file():
        print(f"{str(destination)} already exists, skipping")
        return

    with requests.get(url, stream=True) as r:
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"error downloading {url}: {e}")
            return

        destination.parent.mkdir(parents=True, exist_ok=True)

        # write to file in chunks
        with destination.open("wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def run():
    with TILE_DATA.open("r") as f:
        tiles = [line.strip() for line in f.readlines()]

    print("downloading tiles..")

    with WorkerPool(NPROCS) as p:
        p.map(download_file, tiles, progress_bar=True)


if __name__ == "__main__":
    run()
