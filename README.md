# stactools aafc-landuse

## Agriculture and Agri-Food Canada Land Use

### Description

The Land Use (LU) maps cover all areas of Canada south of 60&deg;N at a spatial resolution of 30 metres. The LU classes follow the protocol of the Intergovernmental Panel on Climate Change (IPCC) and consist of: Forest, Water, Cropland, Grassland, Settlement and Otherland.

The Land Use (LU) maps were developed in response to a need for explicit, high-accuracy, high-resolution land use data to meet AAFC’s commitments in international reporting, especially for the annual National Inventory Report (NIR) to the United Nations Framework Convention on Climate Change (UNFCCC), the Agri-Environmental program of the Organization for Economic Co-operation and Development (OECD) and the FAOSTAT component of the Food and Agriculture Organization of the United Nations (FAO).

### Usage

1. As a python module

```python
from stactools.aafc_landuse.constants import JSONLD_HREF
from stactools.aafc_landuse import utils, cog, stac


# Read metadata
metadata = utils.get_metadata(JSONLD_HREF)

# Create a STAC Collection
json_path = os.path.join(tmp_dir, "/path/to/aafc-landuse.json")
stac.create_collection(metadata, json_path)

# Create a COG
cog.create_cog("/path/to/local.tif", "/path/to/cog.tif")

# Create a STAC Item
stac.create_item(metadata, "/path/to/item.json", "/path/to/cog.tif")
```

2. Using the CLI

```bash
# Create a STAC Collection
stac aafclanduse create-collection -d "/path/to/directory"

# Create a STAC Item and COG - this can be done using remote or local .tif or .zip assets
stac aafclanduse create-item -s "https://www.agr.gc.ca/atlas/data_donnees/lcv/aafcLand_Use/tif/2010/IMG_AAFC_LANDUSE_Z07_2010.zip" -d "/path/to/directory"
```
