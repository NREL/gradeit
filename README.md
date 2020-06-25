# GradeIT
Road Grade Inference Tool (GradeIT) - a python package, developed by the National Renewable Energy Laboratory, 
to append elevation and road grade to a sequence of GPS points.

## Overview
GradeIT looks up and filters elevation and derives road grade from the 
[USGS Digital Elevation Model](https://www.usgs.gov/core-science-systems/ngp/3dep) to append to GPS points, typically 
for vehicles traveling on paved roads. The python package offers options to use either the the freely accessible USGS
[Elevation Point Query Service](https://nationalmap.gov/epqs/) or a locally available raster database of the elevation 
model, which provides much faster results.

## Setup
Clone or download the git repository and re-create the conda environment to automatically ensure that python and package 
version dependencies are satisfied.

```git clone https://github.com/NREL/gradeit.git```

```cd gradeit```

If you do not have the conda package manager, you can download and install it from the 
[Anaconda website](https://www.anaconda.com/). Then conda can be used to create a new environment from the 
```environment.yml``` file in this repository.

```conda env create -f environment.yml```

```conda activate gradeit```

You have now created and activated the gradeit conda environment and are ready to run the package.

## Getting Started
In this repository, `tests/basic.py` will demonstrate a basic workflow to introduce users to the gradeit package. Additionally, the [gradeit-notebooks](https://github.com/NREL/gradeit-notebooks) repo contains various Jupyter notebooks that demonstrate gradeit applications and explore potential improvements.

## Filters
Given the spatial noise that can be present in GPS data and the 1/3 arc-second resolution of the digital elevation
model being employed, outliers and unrealistic topographical features can be present in the raw elevation profiles. 
Therefore, a series of filtering procedures can be applied to the elevation data, if desired by the user. The primary
filter procedure is summarized in the figure below from Wood et al in 2014.

<img src="docs/imgs/grade_filters.png">

<sub>Wood, Eric, E. Burton, A. Duran, and J. Gonder. Appending High-Resolution Elevation Data to GPS Speed Traces for 
Vehicle Energy Modeling and Simulation. No. NREL/TP-5400-61109. National Renewable Energy Lab.(NREL), Golden, CO 
(United States), 2014.<sub>

Additionally, since the USGS Digital Elevation Model is a "bare earth" model, road infrastructure features (i.e. 
bridges and overpasses) are often not represented in the data. Rather, the "bare earth" model represents the valley or
body of water that is being spanned. GradeIT has optional filtering routines to explicitly handle this by
"building" a bridge to span the river, valley, etc where necessary.