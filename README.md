# GradeIT
Road Grade Inference Tool (GradeIT) - a python package to append elevation and road grade to a sequence of GPS points.

## Overview
GradeIT looks up and filters elevation and derives road grade data from the 
[USGS Digital Elevation Model](https://www.usgs.gov/core-science-systems/ngp/3dep) to append to GPS points, typically 
for vehicles traveling on paved roads. The python package offers options to use either the the freely accessible USGS
[Elevation Point Query Service](https://nationalmap.gov/epqs/) or a locally available raster database of the elevation 
model.

## Setup
Clone or download the git repository and re-create the conda environment to automatically ensure that python and package 
version dependencies are satisfied.

```git clone https://github.com/NREL/gradeit.git```

```cd gradeit```

If you do not have the conda package manager, you can download and install it from the 
[Anaconda website](https://www.anaconda.com/). Then conda will create a new environment from the ```environment.yml``` 
file in this repository.

```conda env create -f environment.yml```

```conda activate gradeit```

You have now created and activated the gradeit conda environment and are ready to run the package.

## Filters
[update image with something that exactly represents how this version of GradeIT filters]

<img src="docs/imgs/grade_filters.png">