[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/stactools-packages/aafc-landuse/main?filepath=docs/installation_and_basic_usage.ipynb)

# stactools aafc-landuse

## Agriculture and Agri-Food Canada Land Use

### Description

The Land Use (LU) maps cover all areas of Canada south of 60&deg;N at a spatial resolution of 30 metres. The LU classes follow the protocol of the Intergovernmental Panel on Climate Change (IPCC) and consist of: Forest, Water, Cropland, Grassland, Settlement and Otherland.

The Land Use (LU) maps were developed in response to a need for explicit, high-accuracy, high-resolution land use data to meet AAFC’s commitments in international reporting, especially for the annual National Inventory Report (NIR) to the United Nations Framework Convention on Climate Change (UNFCCC), the Agri-Environmental program of the Organization for Economic Co-operation and Development (OECD) and the FAOSTAT component of the Food and Agriculture Organization of the United Nations (FAO).

### Usage

```bash
# Create a STAC Collection
stac aafclanduse create-collection "/path/to/directory"
# The file /path/to/directory/aafc_landuse_collection.json is created

# Create a COG - this can be done using remote or local .tif or .zip assets
stac aafclanduse create-cog "/path/to/directory/IMG_AAFC_LANDUSE_Z07_2010.tif" "/path/to/directory"
# The file /path/to/directory/IMG_AAFC_LANDUSE_Z07_2010_cog.tif is created

# Create a STAC Item from the above COG
stac aafclanduse create-item /path/to/directory /path/to/directoryIMG_AAFC_LANDUSE_Z07_2010_cog.tif
# The file /path/to/directory/IMG_AAFC_LANDUSE_Z07_2010_cog.json is created

```
