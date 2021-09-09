# flake8: noqa

from pyproj import CRS
from pystac import Provider
from pystac import Link

LANDUSE_ID = "aafc-landuse"
LANDUSE_EPSG = 3978
LANDUSE_CRS = CRS.from_epsg(LANDUSE_EPSG)
LANDUSE_TITLE = "Land Use 1990, 2000 & 2010"
LICENSE = "OGL-Canada-2.0"
LICENSE_LINK = Link(
    rel="license",
    target="https://open.canada.ca/en/open-government-licence-canada",
    title="Open Government Licence - Canada",
)

DESCRIPTION = """The 1990, 2000 and 2010 Land Use (LU) maps cover all areas of Canada south of 60 degrees N at a spatial resolution of 30 metres. The LU classes follow the protocol of the Intergovernmental Panel on Climate Change (IPCC) and consist of: Forest, Water, Cropland, Grassland, Settlement and Otherland."""

LANDUSE_PROVIDER = Provider(
    name="Natural Resources Canada | Ressources naturelles Canada",
    roles=["producer", "processor", "host"],
    url=
    "https://open.canada.ca/data/en/dataset/18e3ef1a-497c-40c6-8326-aac1a34a0dec",
)

JSONLD_HREF = (
    "https://open.canada.ca/data/en/dataset/18e3ef1a-497c-40c6-8326-aac1a34a0dec.jsonld"
)

LANDUSE_FTP = "https://www.agr.gc.ca/atlas/data_donnees/lcv/aafcLand_Use/tif/"

CLASSIFICATION_VALUES = {
    11: "Unclassified",
    21: "Settlement",
    25: "Roads",
    31: "Water",
    41: "Forest",
    42: "Forest Wetland",
    45: "Trees",
    46: "Treed Wetland",
    51: "Cropland",
    61: "Grassland Managed",
    62: "Grassland Unmanaged",
    71: "Wetland",
    73: "Wetland Shrub",
    74: "Wetland Herb",
    91: "Other land",
}
