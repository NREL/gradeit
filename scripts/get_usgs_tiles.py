from pathlib import Path
from multiprocessing import Pool

import argparse
import logging

import requests

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Download USGS 1/3 arc-second DEM tiles")

parser.add_argument(
    "--tile-data",
    type=str,
    default="usgs_tiles.txt",
    help="File containing list of tiles to download",
)

parser.add_argument(
    "--output-dir",
    type=str,
    default="usgs_tiles",
    help="Directory to save downloaded tiles",
)

parser.add_argument(
    "--nprocs",
    type=int,
    default=4,
    help="Number of processes to use for downloading",
)


LINK_BASE = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current"


def build_link(tile: str) -> str:
    link = f"{LINK_BASE}/{tile}/USGS_13_{tile}.tif"
    return link


def download_file(tile: str, output_dir: Path):
    url = build_link(tile)
    destination = output_dir / f"{tile}" / f"USGS_13_{tile}.tif"
    if destination.is_file():
        print(f"{str(destination)} already exists, skipping")
        return

    print(f"downloading {url} to {str(destination)}")

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
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    tile_data_file = Path(args.tile_data)

    with tile_data_file.open("r") as f:
        tiles = [line.strip() for line in f.readlines()]

    log.info(f"downloading {len(tiles)} tiles..")

    with Pool(args.nprocs) as p:
        p.map(download_file, tiles)


if __name__ == "__main__":
    run()
