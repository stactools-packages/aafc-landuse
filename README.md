[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/stactools-packages/aafc-landuse/main?filepath=docs/installation_and_basic_usage.ipynb)

# stactools aafc-landuse

## Agriculture and Agri-Food Canada (AAFC) Land Use Semi-Decadal Land Use Time Series

### Description

The AAFC Land Use Time Series is a culmination and curated meta-analysis of several high-quality spatial datasets produced between 1990 and 2021 using a variety of methods by teams of researchers as techniques and capabilities have evolved. The information from the input datasets was consolidated and embedded within each 30m x 30m pixel to create consolidated pixel histories, resulting in thousands of unique combinations of evidence ready for careful consideration. Informed by many sources of high-quality evidence and visual observation of imagery in Google Earth, we apply an incremental strategy to develop a coherent best current understanding of what has happened in each pixel through the time series.

### Usage

1. As a python module

```python
from stactools.aafc_landuse import cog, stac

# Create a STAC Collection
# Note: a url pointing to existing metadata is provided in stac.constants,
# and it may be overridden
collection = stac.create_collection()

# Create a COG
# Note, the native tif paths provided by AAFC should be used to retain
# information so the time and id can be parsed for the creation of a STAC item
# This command creates the file "/path/to/output/dir/LU2000_u22_v3_2021_06_cog.tif"
aafc_tif_path = "/path/to/LU2000_u22_v3_2021_06.tif"
cog.create_cog(aafc_tif_path, "/path/to/output/dir")

# Create a STAC Item
item = stac.create_item("/path/to/output/dir/LU2000_u22_v3_2021_06_cog.tif")
```

2. Using the CLI

```bash
# Create a STAC Collection
stac aafclanduse create-collection -d "/path/to/directory"
# ...creates "/path/to/directory/collection.json"

# Create a COG
stac aafclanduse create-cog "/path/to/LU2000_u22_v3_2021_06.tif" "/path/to/output/dir"

# Create a STAC Item from the above COG
stac aafclanduse create-item -c "/path/to/output/dir/LU2000_u22_v3_2021_06_cog.tif" -d "/path/to/directory"
# ...creates "/path/to/directory/LU2000_u22_v3_2021_06_cog.json"
```
