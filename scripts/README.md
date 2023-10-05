# Scripts

## Download Tiles

The `get_usgs_tiles.py` script with download the raster tiles that gradeit uses to lookup elevation data

### Usage

The script takes a few environment variables:

- `OUTPUT_DIR`: Where should the script write the tiles to? Defaults to a relative folder `usgs_tiles/`
- `TILE_DATA`: Which tiles should we download? Defaults to the `usgs_tiles.txt` file.
- `NPROCS`: How many processors to use for downloading? Defaults to 4

### Example

This example would use the `colorado_tiles.txt` to just download raster tiles that cover the state of colorado:

```console
export OUTPUT_DIR=colorado_tiles/
export TILE_DATA=colorado_tiles.txt
export NPROCS=2

python get_usgs_tiles.py
```
