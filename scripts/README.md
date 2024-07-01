# Scripts

## Download Tiles

The `get_usgs_tiles.py` script with download the raster tiles that gradeit uses to lookup elevation data

### Usage

The script takes a few optional arguments:

- `--output-dir`: Where should the script write the tiles to? Defaults to a relative folder `usgs_tiles/`
- `--tile-data`: Which tiles should we download? Defaults to the `usgs_tiles.txt` file.
- `--nprocs`: How many processors to use for downloading? Defaults to 4

### Example

This example would use the `colorado_tiles.txt` to just download raster tiles that cover the state of colorado:

```console
python get_usgs_tiles.py --output-dir colorado_tiles/ --tile-data colorado_tiles.txt --nprocs 2
```
